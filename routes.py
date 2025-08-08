from flask import session, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from app import app, db
from replit_auth import require_login, require_admin, make_replit_blueprint
from flask_login import current_user
from models import Chore, MealPlan, Notification, User
from calendar_api import get_meals
from datetime import datetime, date, timezone
from flask import render_template, session
from tasks_api import get_google_tasks, build_google_service, get_or_create_task_list

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

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

    # Get active notifications
    active_notifications = Notification.query.filter_by(is_active=True)\
        .order_by(Notification.created_at.desc())\
        .limit(3).all()

    return render_template(
        'index.html',
        chores=recent_chores,
        meals=upcoming_meals,
        notifications=active_notifications,
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

@app.route('/notifications')
def notifications():
    all_notifications = Notification.query.filter_by(is_active=True).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=all_notifications)

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

@app.route('/chores/create', methods=['GET', 'POST'])
def create_chore():
    service = build_google_service()
    task_list_id = get_or_create_task_list(service, "Family chores")

    if request.method == 'POST':
        title = request.form['title']
        assigned_to = request.form['assigned_to']
        due = request.form['due_date']

        notes = f"Assigned to: {assigned_to}"

        task = {
            'title': title,
            'notes': notes,
            'due': f"{due}T23:59:59.000Z",
            'status': 'needsAction'
        }

        service.tasks().insert(tasklist=task_list_id, body=task).execute()
        return redirect(url_for('view_chores'))

    return render_template('create_chore.html')
# Admin routes
@app.route('/admin')
@require_admin
def admin_dashboard():
    total_chores = Chore.query.count()
    completed_chores = Chore.query.filter_by(completed=True).count()
    total_meals = MealPlan.query.count()
    total_users = User.query.count()
    active_notifications = Notification.query.filter_by(is_active=True).count()
    
    return render_template('admin_dashboard.html',
                         total_chores=total_chores,
                         completed_chores=completed_chores,
                         total_meals=total_meals,
                         total_users=total_users,
                         active_notifications=active_notifications)

@app.route('/admin/chores')
@require_admin
def admin_manage_chores():
    all_chores = Chore.query.order_by(Chore.created_at.desc()).all()
    return render_template('admin/manage_chores.html', chores=all_chores)

@app.route('/admin/chores/new', methods=['GET', 'POST'])
@require_admin
def admin_new_chore():
    if request.method == 'POST':
        chore = Chore()
        chore.title = request.form['title']
        chore.description = request.form['description']
        chore.assigned_to = request.form['assigned_to']
        chore.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form['due_date'] else None
        chore.priority = request.form['priority']
        chore.category = request.form['category']
        chore.created_by = current_user.id
        db.session.add(chore)
        db.session.commit()
        flash('Chore created successfully!', 'success')
        return redirect(url_for('admin_manage_chores'))
    
    return render_template('admin/manage_chores.html', chores=[], show_form=True)

@app.route('/admin/chores/<int:chore_id>/delete', methods=['POST'])
@require_admin
def admin_delete_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    db.session.delete(chore)
    db.session.commit()
    flash('Chore deleted successfully!', 'success')
    return redirect(url_for('admin_manage_chores'))

@app.route('/admin/meals')
@require_admin
def admin_manage_meals():
    all_meals = MealPlan.query.order_by(MealPlan.planned_date.desc()).all()
    return render_template('admin/manage_meals.html', meals=all_meals)

@app.route('/admin/meals/new', methods=['GET', 'POST'])
@require_admin
def admin_new_meal():
    if request.method == 'POST':
        meal = MealPlan()
        meal.meal_name = request.form['meal_name']
        meal.meal_type = request.form['meal_type']
        meal.planned_date = datetime.strptime(request.form['planned_date'], '%Y-%m-%d').date()
        meal.ingredients = request.form['ingredients']
        meal.instructions = request.form['instructions']
        meal.assigned_cook = request.form['assigned_cook']
        meal.prep_time = int(request.form['prep_time']) if request.form['prep_time'] else None
        meal.created_by = current_user.id
        db.session.add(meal)
        db.session.commit()
        flash('Meal plan created successfully!', 'success')
        return redirect(url_for('admin_manage_meals'))
    
    return render_template('admin/manage_meals.html', meals=[], show_form=True)

@app.route('/admin/meals/<int:meal_id>/delete', methods=['POST'])
@require_admin
def admin_delete_meal(meal_id):
    meal = MealPlan.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    flash('Meal plan deleted successfully!', 'success')
    return redirect(url_for('admin_manage_meals'))

@app.route('/admin/users')
@require_admin
def admin_manage_users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=all_users)

@app.route('/admin/users/<user_id>/toggle-admin', methods=['POST'])
@require_admin
def admin_toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:  # Can't change own admin status
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'User {user.first_name or user.email} admin status updated!', 'success')
    else:
        flash('You cannot change your own admin status!', 'warning')
    return redirect(url_for('admin_manage_users'))

@app.route('/admin/notifications/new', methods=['POST'])
@require_admin
def admin_new_notification():
    notification = Notification()
    notification.title = request.form['title']
    notification.message = request.form['message']
    notification.type = request.form['type']
    notification.expires_at = datetime.strptime(request.form['expires_at'], '%Y-%m-%dT%H:%M') if request.form['expires_at'] else None
    notification.created_by = current_user.id
    db.session.add(notification)
    db.session.commit()
    flash('Notification created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))
