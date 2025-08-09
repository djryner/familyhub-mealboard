from flask import session, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from app import app, db
#from replit_auth import require_login, require_admin, make_replit_blueprint
from flask_login import current_user
#from models import Chore, MealPlan, Notification, User
from calendar_api import get_meals
from datetime import datetime, date, timezone
from flask import render_template, session
from tasks_api import get_google_tasks, build_google_service, get_or_create_task_list
from models import ChoreTemplate


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
def index():
    # Build Google Tasks API service and get tasks
    service = build_google_service()
    task_list_id = get_or_create_task_list(service, "Family chores")
    all_chores = get_google_tasks(service, task_list_id)

    # Filter incomplete tasks and sort by due date (None goes last)
    pending_chores = [
        c for c in all_chores if not c.get("completed")
    ]
    pending_chores.sort(key=lambda c: c.get("due_date") or datetime.max)

    # Limit to 5 upcoming chores
    recent_chores = pending_chores[:5]

    # Get today's date in ISO format
    today = date.today()
    today_str = today.isoformat()

    # Fetch and filter meals
    meals_data = get_meals()
    upcoming_meals = []

    if "error" not in meals_data:
        for date_str in sorted(meals_data.keys()):
            if date_str >= today_str:
                for meal in meals_data[date_str]:
                    upcoming_meals.append({"date": date_str, "meal": meal})
            if len(upcoming_meals) >= 5:
                break
        upcoming_meals = upcoming_meals[:5]


    return render_template(
        'index.html',
        chores=recent_chores,
        meals=upcoming_meals,
        today=today_str
    )

@app.route('/chores')
def view_chores():
    # Build authorized Google Tasks API service
    service = build_google_service()  # This uses credentials/session

    # Fetch task lists from Google API
    task_list_id = get_or_create_task_list(service, "Family chores")

    # Fetch tasks from Google Tasks API
    chores = get_google_tasks(service, task_list_id)

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

@app.route('/chore/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    service = build_google_service()
    task_list_id = get_or_create_task_list(service, "Family chores")  # Use actual list

    task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()

    if task['status'] == 'completed':
        task['status'] = 'needsAction'
        task.pop('completed', None)
    else:
        task['status'] = 'completed'
        task['completed'] = datetime.now(timezone.utc).isoformat()


    service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()
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
def complete_chore(chore_id):
    # TODO: persist completion (e.g., Google Tasks); return 204 on success
    return ('', 204)


