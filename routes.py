"""Web route handlers.

Primary responsibilities:
* Provide HTML pages: index, meals, chores.
* JSON APIs for meals, chore templates & categories.
* Integrate with Google Tasks & Calendar abstraction functions.
"""

from __future__ import annotations

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
from app import app, db
from calendar_api import get_meals  # legacy JSON endpoint still uses mapping
from tasks_api import build_google_service, get_or_create_task_list
from services.chores_service import fetch_chores, complete_chore as service_complete_chore, ChoreDTO
from services.meals_service import fetch_meals, MealDTO
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
    logger.info("index: start")

    # Unified chores source: fetch upcoming (incomplete) chores
    recent_chores: list[ChoreDTO] = fetch_chores(include_completed=False, limit=5)
    logger.info("index: loaded %d chores", len(recent_chores))

    today = date.today()
    end = today + timedelta(days=6)
    meals: list[MealDTO] = fetch_meals(start=today, end=end)
    # Cap to 7 (already sorted inside service)
    if len(meals) > 7:
        meals = meals[:7]
    logger.info("index: meals final_count=%d window=%s..%s", len(meals), today, end)
    for m in meals:  # pragma: no cover (log only)
        logger.info("index: meal %s %s", m.date.isoformat(), m.title)

    return render_template(
        'index.html',
        chores=recent_chores,
        meals=meals,
        today=today
    )

@app.route('/chores')
def view_chores():
    logger.info("view_chores: loading all chores (include completed)")
    chores: list[ChoreDTO] = fetch_chores(include_completed=True)
    logger.info("view_chores: loaded %d chores", len(chores))
    return render_template('chores.html', chores=chores)

@app.route('/meal-plans')
def meal_plans():
    today = date.today()
    # broaden window for plans - reuse calendar_service default (today +/- days)
    meals = fetch_meals()  # full range from service; template will list all
    return render_template('meal_plans.html', meals=[{"date": m.date.isoformat(), "meal": m.title} for m in meals], today=today.isoformat())

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

def format_meals_for_template(meals):  # legacy helper (unused) kept for compatibility
    formatted = []
    for meal in meals:
        formatted.append({"meal": getattr(meal, 'title', meal.get('meal')), "date": getattr(meal, 'date', meal.get('date'))})
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


