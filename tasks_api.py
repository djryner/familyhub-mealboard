import os
import datetime
import pytz
import logging
import re
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build


logger = logging.getLogger("tasks_api")

# Path to your service account key file
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
SERVICE_ACCOUNT_FILE = creds_path


# Authenticate and build the service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/tasks']
)

service = build('tasks', 'v1', credentials=credentials)

def create_task(task_list_id, title, due_date, notes=None):
    task = {
        'title': title,
        'due': due_date,
        'notes': notes
    }
    result = service.tasks().insert(tasklist=task_list_id, body=task).execute()
    return result

def list_tasks(task_list_id):
    result = service.tasks().list(tasklist=task_list_id).execute()
    return result.get('items', [])

# Example usage:
TASK_LIST_ID = '@default'  # This is the default task

def get_google_tasks(service, task_list_id):
    logger.info("get_google_tasks called")

    tasks_result = service.tasks().list(tasklist=task_list_id).execute()
    raw_tasks = tasks_result.get('items', [])

    chores = []
    for task in raw_tasks:
        chores.append({
            'id': task['id'],
            'title': task.get('title', 'Untitled'),
            'description': task.get('notes', ''),
            'assigned_to': extract_assignee(task.get('notes', '')),
            'due_date': parse_iso_date(task.get('due')),
            'completed': task.get('status') == 'completed',
            'category': None,
            'priority': 'high' if '!' in task.get('title', '') else 'low'
        })
    for chore in chores:
        print(f"Loaded chore from Google Tasks: {chore['title']}")
    
    return chores

def extract_assignee(notes):
    # naive example: look for "Assigned to: Name"
    match = re.search(r'Assigned to:\s*(\w+)', notes)
    return match.group(1) if match else None

def parse_iso_date(iso):
    from datetime import datetime
    return datetime.fromisoformat(iso.replace('Z', '+00:00')) if iso else None

def build_google_service():
    creds = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/tasks']
    )
    return build('tasks', 'v1', credentials=creds)

def get_or_create_task_list(service, list_title="Family chores"):
    response = service.tasklists().list().execute()
    for tasklist in response.get('items', []):
        if tasklist['title'].strip().lower() == list_title.strip().lower():
            return tasklist['id']

    # Not found — create it
    new_list = {
        "title": list_title
    }
    created = service.tasklists().insert(body=new_list).execute()
    print(f"Created new task list: {created['title']} → {created['id']}")
    return created['id']