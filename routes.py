"""Web route handlers.

Primary responsibilities:
* Provide HTML pages: index, meals, chores.
* JSON APIs for meals, chore templates & categories.
* Integrate with Google Tasks & Calendar abstraction functions.
"""

from __future__ import annotations

import logging
from datetime import datetime, date, timezone
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
from app import app, db
from calendar_api import get_meals
from tasks_api import build_google_service, get_or_create_task_list
from services.chores_service import fetch_chores, complete_chore as service_complete_chore, ChoreDTO
from models import ChoreTemplate

logger = logging.getLogger("dashboard")


#app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/api/meals')
def api_meals():
    """Return dinner plans from the shared Google Calendar."""
    return jsonify(get_meals())

# Public routes
@app.route('/')
def index():  # noqa: D401
    # Unified chores source: fetch upcoming (incomplete) chores
    logger.info("index: loading recent chores (limit=5, incomplete)")
    recent_chores: list[ChoreDTO] = fetch_chores(include_completed=False, limit=5)
    logger.info("index: loaded %d chores", len(recent_chores))

    # Get today's date in ISO format
    today = date.today()
    today_str = today.isoformat()

    # Fetch and filter meals
    meals_data = get_meals()
    all_meals = []
    if "error" not in meals_data:
        for date_str in sorted(meals_data.keys()):
            if date_str >= today_str:
                for meal in meals_data[date_str]:
                    upcoming_meals.append({"date": date_str, "meal": meal})
            if len(upcoming_meals) >= 7:
                break
        upcoming_meals = upcoming_meals[:7]

    # Format meals for template (adds dow, mmdd, iso)
    formatted_meals = []
    for meal in upcoming_meals:
        if isinstance(meal['date'], str):
            dt = datetime.strptime(meal['date'], "%Y-%m-%d").date()
        else:
            dt = meal['date']
        formatted_meals.append({
            "meal": meal["meal"],
            "date": meal["date"],
            "dow": dt.strftime("%a"),
            "mmdd": dt.strftime("%m/%d"),
            "iso": dt.strftime("%Y-%m-%d"),
        })
    # Add logging for meal data
    logger.info("today: %s", today)
    logger.info("upcoming_meals (raw): %s", upcoming_meals)
    logger.info("formatted_meals (for template): %s", formatted_meals)


    return render_template(
        'index.html',
        chores=recent_chores,
        meals=formatted_meals,
        today=today_str
    )

@app.route('/chores')
def view_chores():
    logger.info("view_chores: loading all chores (include completed)")
    chores: list[ChoreDTO] = fetch_chores(include_completed=True)
    logger.info("view_chores: loaded %d chores", len(chores))
    return render_template('chores.html', chores=chores)

@app.route('/meal-plans')
def meal_plans():
    # Get today's date in ISO format
    today = date.today()
    today_str = today.isoformat()

    # Use get_meals() instead of MealPlan.query
    meals_data = get_meals()
    if "error" in meals_data:
        meals = []
    else:
        # Flatten to a list of dicts for template
        meals = []
        for date_str in sorted(meals_data.keys()):
            for meal in meals_data[date_str]:
                meals.append({"date": date_str, "meal": meal})
    return render_template('meal_plans.html', meals=meals, today=today_str)

@app.route('/chore/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):  # legacy endpoint: mark complete only
    service_complete_chore(task_id)
    return redirect(url_for('view_chores'))

@app.route('/api/chore-categories')
def api_chore_categories():
    cats = db.session.query(ChoreTemplate.category)\
        .filter(ChoreTemplate.is_active == True)\
        .distinct().order_by(ChoreTemplate.category.asc()).all()
    return jsonify([c[0] for c in cats])

@app.route('/api/chore-templates')
def api_chore_templates():
    category = request.args.get('category')
    q = ChoreTemplate.query.filter_by(is_active=True)
    if category:
        q = q.filter(ChoreTemplate.category == category)
    items = q.order_by(ChoreTemplate.name.asc()).all()
    return jsonify([{"id": t.id, "name": t.name, "category": t.category} for t in items])

def format_meals_for_template(meals):
    formatted = []
    for meal in meals:
        # Parse date string to date object
        if isinstance(meal['date'], str):
            dt = datetime.datetime.strptime(meal['date'], "%Y-%m-%d").date()
        else:
            dt = meal['date']
        formatted.append({
            "meal": meal["meal"],
            "date": meal["date"],
            "dow": dt.strftime("%a"),
            "mmdd": dt.strftime("%m/%d"),
            "iso": dt.strftime("%Y-%m-%d"),
        })
    return formatted

@app.route('/chores/create', methods=['GET', 'POST'])
def create_chore():
    service = build_google_service()
    task_list_id = get_or_create_task_list(service, "Family chores")

    if request.method == 'POST':
        template_id = request.form['template_id']           # selected chore template
        assigned_to = request.form['assigned_to']
        due = request.form['due_date']                      # YYYY-MM-DD

        tmpl = ChoreTemplate.query.get_or_404(template_id)
        title = tmpl.name
        notes = f"Assigned to: {assigned_to}"

        task = {
            "title": title,
            "notes": notes,
            "due": f"{due}T23:59:59.000Z",
            "status": "needsAction"
        }
        service.tasks().insert(tasklist=task_list_id, body=task).execute()
        return redirect(url_for('view_chores'))

    # initial render: provide categories for the first dropdown
    categories = [c[0] for c in db.session.query(ChoreTemplate.category)
                  .filter(ChoreTemplate.is_active == True)
                  .distinct().order_by(ChoreTemplate.category.asc()).all()]
    return render_template('create_chore.html', categories=categories)


@app.post('/chores/<string:chore_id>/complete', endpoint='complete_chore')
def complete_chore_route(chore_id):  # AJAX endpoint used by dashboard cards
    service_complete_chore(chore_id)
    return ('', 204)


