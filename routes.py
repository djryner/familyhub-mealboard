from __future__ import annotations
"""Web route handlers.

Primary responsibilities:
* Provide HTML pages: index, meals, chores.
* JSON APIs for meals, chore templates & categories.
* Integrate with Google Tasks & Calendar abstraction functions.
"""



import logging
from datetime import datetime, date, timezone, timedelta
from typing import List, Dict, Any

from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from sqlalchemy import text

from app import app, db
from calendar_api import get_meals  # legacy JSON endpoint still uses mapping
from services.chores_service import (
    fetch_chores,
    complete_chore as service_complete_chore,
    ChoreDTO,
)
from services.meals_service import fetch_meals, MealDTO
from services import points_service
from config import get_settings
from models import ChoreTemplate
from services.schedule_utils import (
    WK,
    BY,
    next_on_or_after,
    next_in_set_on_or_after,
    to_utc_midnight_rfc3339,
)


logger = logging.getLogger("dashboard")

# Route to ignore a chore (complete without awarding points)
@app.route("/chores/<string:chore_id>/ignore", methods=["POST"], endpoint="ignore_chore")
def ignore_chore(chore_id):
    """Mark a chore as complete but do not award points."""
    service_complete_chore(chore_id)
    # Do NOT award points
    flash("Chore ignored (no points awarded).", "warning")
    return redirect(request.referrer or url_for("view_chores"))


# app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")


# Make session permanent
@app.before_request
def make_session_permanent():
    """Sets the Flask session to be permanent."""
    session.permanent = True


@app.route("/api/meals")
def api_meals():
    """Return dinner plans from the shared Google Calendar (legacy)."""
    return jsonify(get_meals())


# Public routes
@app.route("/")
def index():
    """Renders the main dashboard page.

    This page displays a summary of upcoming chores and meals for the week.
    """
    logger.info("index: start")

    settings = get_settings()

    # Fetch all chores due today, any status
    today = date.today()
    chores_today: list[ChoreDTO] = fetch_chores(start=today, end=today, include_completed=True)
    logger.info("index: loaded %d chores due today", len(chores_today))

    # Fetch meals for the next 7 days
    today = date.today()
    end_date = today + timedelta(days=6)
    meals: list[MealDTO] = fetch_meals(start=today, end=end_date)

    # Cap the number of meals to 7, as the service might return more
    if len(meals) > 7:
        meals = meals[:7]
    logger.info(
        "index: meals final_count=%d window=%s..%s", len(meals), today, end_date
    )
    for m in meals:  # pragma: no cover (log only)
        logger.info("index: meal %s %s", m.date.isoformat(), m.title)

    leaderboard = []
    if settings.points_enabled:
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        try:
            with db.engine.begin() as conn:
                leaderboard = points_service.leaderboard_week(conn, start_week, end_week)
        except Exception:  # pragma: no cover - points tables may be missing
            leaderboard = []

    return render_template(
        "index.html",
        chores=chores_today,
        meals=meals,
        today=today,
        leaderboard=leaderboard,
        points_enabled=settings.points_enabled,
    )


@app.route("/chores")
def view_chores():
    """Renders the page that displays all chores, including completed ones."""
    logger.info("view_chores: loading all chores (include completed)")
    chores: list[ChoreDTO] = fetch_chores(include_completed=True)
    logger.info("view_chores: loaded %d chores", len(chores))
    return render_template("chores.html", chores=chores)


@app.route("/meal-plans")
def meal_plans():
    """Renders the page displaying all meal plans from the calendar."""
    today = date.today()
    # Fetch all available meals from the service (uses service's default date window)
    meals = fetch_meals()
    # Format meals for template consumption
    meal_data = [{"date": m.date.isoformat(), "meal": m.title} for m in meals]
    return render_template("meal_plans.html", meals=meal_data, today=today.isoformat())


@app.route("/chore/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """Legacy endpoint to mark a chore as complete."""
    service_complete_chore(task_id)
    return redirect(url_for("view_chores"))


@app.route("/api/chore-categories")
def api_chore_categories():
    """Returns a JSON list of unique, active chore categories."""
    categories_query = (
        db.session.query(ChoreTemplate.category)
        .filter(ChoreTemplate.is_active.is_(True))
        .distinct()
        .order_by(ChoreTemplate.category.asc())
        .all()
    )
    return jsonify([c[0] for c in categories_query])


@app.route("/api/chore-templates")
def api_chore_templates():
    """Returns a JSON list of active chore templates, optionally filtered by category."""
    category = request.args.get("category")
    query = ChoreTemplate.query.filter_by(is_active=True)
    if category:
        query = query.filter(ChoreTemplate.category == category)
    items = query.order_by(ChoreTemplate.name.asc()).all()
    return jsonify(
        [{"id": t.id, "name": t.name, "category": t.category} for t in items]
    )


def format_meals_for_template(meals):
    """DEPRECATED: Legacy helper to format meals. Kept for compatibility."""
    formatted = []
    for meal in meals:
        formatted.append(
            {
                "meal": getattr(meal, "title", meal.get("meal")),
                "date": getattr(meal, "date", meal.get("date")),
            }
        )
    return formatted


@app.route("/chores/create", methods=["GET", "POST"])
def create_chore():
    """Handles the creation of a new chore from a template."""
    if request.method == "POST":
        # Process the form submission to create a new task in Google Tasks
        template_id = request.form["template_id"]  # Selected chore template
        assigned_to = request.form["assigned_to"]
        points = int(request.form.get("points", 1))
        weekday_name = request.form.get("weekday")
        recurrence = (request.form.get("recurrence") or "Once").strip()

        tmpl = ChoreTemplate.query.get_or_404(template_id)
        title = tmpl.name
        notes = f"Assigned to: {assigned_to}"

        today = date.today()
        tz_name = app.config.get("APP_TZ")

        if recurrence in ("Once", "Once per week"):
            if not weekday_name:
                return jsonify(error="Please choose a weekday"), 400
            wd = WK[weekday_name]
            due_date = next_on_or_after(today, wd)
            rrule = None if recurrence == "Once" else [f"RRULE:FREQ=WEEKLY;BYDAY={BY[wd]}"]
        elif recurrence == "Daily":
            due_date = today
            rrule = ["RRULE:FREQ=DAILY"]
        elif recurrence == "School Days":
            due_date = next_in_set_on_or_after(today, {0,1,2,3,4})
            rrule = ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]
        elif recurrence == "Weekends":
            due_date = next_in_set_on_or_after(today, {5,6})
            rrule = ["RRULE:FREQ=WEEKLY;BYDAY=SA,SU"]
        elif recurrence == "Sunday to Thursday":
            due_date = next_in_set_on_or_after(today, {6,0,1,2,3})
            rrule = ["RRULE:FREQ=WEEKLY;BYDAY=SU,MO,TU,WE,TH"]
        else:
            return jsonify(error="Invalid recurrence"), 400

        due_iso = to_utc_midnight_rfc3339(due_date, tz_name)

        from services.chores_service import create_chore as service_create_chore
        service_create_chore(
            title=title,
            assigned_to=assigned_to,
            due_date=due_date,
            points=points,
            recurrence=rrule[0] if isinstance(rrule, list) else rrule,
        )
        flash(f"Chore '{title}' created successfully!", "success")
        return redirect(url_for("view_chores"))

    # For a GET request, render the form with the list of categories
    categories = [
        c[0]
        for c in db.session.query(ChoreTemplate.category)
        .filter(ChoreTemplate.is_active.is_(True))
        .distinct()
        .order_by(ChoreTemplate.category.asc())
        .all()
    ]
    with db.engine.begin() as conn:
        users = points_service.list_users(conn)
    return render_template("create_chore.html", categories=categories, users=users)


@app.post("/chores/<string:chore_id>/complete", endpoint="complete_chore")
def complete_chore_route(chore_id):
    """AJAX endpoint to mark a chore as complete. Used by dashboard cards."""
    payload = request.get_json(silent=True) or {}
    due_iso = payload.get("due_iso")
    service_complete_chore(chore_id)

    settings = get_settings()
    fallback = settings.points_default if getattr(settings, "points_default", None) is not None else 1

    with db.engine.begin() as conn:
        user = payload.get("assigned_to")
        if not user:
            meta = conn.execute(text("SELECT assigned_to FROM chore_metadata WHERE task_id=:id"), {"id": chore_id}).fetchone()
            user = meta[0] if meta and meta[0] else None
        pts = points_service.get_chore_points(conn, chore_id, fallback=fallback)
        # Occurrence-safe points: only award once per (task_id, due_iso)
        if user and due_iso:
            already = conn.execute(text("SELECT 1 FROM points_ledger WHERE user_name=:u AND task_id=:t AND kind='earn' AND occurred_at LIKE :d || '%'"), {"u": user, "t": chore_id, "d": due_iso}).fetchone()
            if not already:
                points_service.grant_points_for_completion(conn, user=user, task_id=chore_id, points=pts)

    return ("", 204)


@app.post('/admin/chores/<string:task_id>/points', endpoint='admin_set_points')
def admin_set_points(task_id):
    pts = int(request.form.get('points', 1))
    with db.engine.begin() as conn:
        points_service.set_chore_points(conn, task_id, pts)
    return ('', 204)


@app.get('/admin/rewards', endpoint='rewards_page')
def rewards_page():
    rows = db.session.execute(text("SELECT id, title, cost_points, active FROM rewards ORDER BY active DESC, cost_points")).fetchall()
    return render_template('admin/rewards.html', rewards=rows)


@app.post('/admin/rewards', endpoint='create_reward')
def create_reward():
    t = request.form['title']
    c = int(request.form['cost_points'])
    db.session.execute(text("INSERT INTO rewards(title, cost_points) VALUES (:t,:c)"), {"t": t, "c": c})
    db.session.commit()
    return redirect(url_for('rewards_page'))


@app.post('/admin/redeem', endpoint='redeem_reward')
def redeem_reward():
    user = request.form['user']
    rid = int(request.form['reward_id'])
    with db.engine.begin() as conn:
        points_service.redeem(conn, user=user, reward_id=rid)
    return redirect(url_for('rewards_page'))


@app.get('/admin/users', endpoint='admin_users')
def admin_users():
    rows = db.session.execute(
        text('SELECT id, name, color, avatar FROM users ORDER BY name')
    ).fetchall()
    return render_template('admin/users_simple.html', users=rows)


@app.post('/admin/users', endpoint='create_user')
def create_user():
    name = request.form['name']
    color = request.form.get('color')
    avatar = request.form.get('avatar')
    db.session.execute(
        text('INSERT INTO users(name, color, avatar) VALUES (:n,:c,:a)'),
        {'n': name, 'c': color, 'a': avatar},
    )
    db.session.commit()
    return redirect(url_for('admin_users'))
