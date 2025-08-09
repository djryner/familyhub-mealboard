"""Google Tasks API helper functions.

Provides a thin abstraction around building the service and normalizing task
data into a consistent structure consumed by templates.
"""

from __future__ import annotations

import os
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger("tasks_api")

SCOPES = ['https://www.googleapis.com/auth/tasks']


def build_google_service():
    """Return a Google Tasks service instance.

    Recreates on each call to avoid stale credentials and ease testing.
    """
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):  # pragma: no cover
        raise RuntimeError('Google credentials path not set or file missing')
    logger.info("build_google_service: using credentials at %s", creds_path)
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('tasks', 'v1', credentials=creds, cache_discovery=False)
    logger.info("build_google_service: service created")
    return service

def create_task(service, task_list_id: str, title: str, due_date: str, notes: str | None = None) -> Dict[str, Any]:
    task = {'title': title, 'due': due_date, 'notes': notes}
    return service.tasks().insert(tasklist=task_list_id, body=task).execute()

def list_tasks(service, task_list_id: str) -> List[Dict[str, Any]]:
    logger.info("list_tasks: fetching tasks for task_list_id=%s", task_list_id)
    result = service.tasks().list(tasklist=task_list_id).execute()
    items = result.get('items', [])
    logger.info("list_tasks: retrieved %d tasks", len(items))
    return items

# Example usage:
TASK_LIST_ID = '@default'  # This is the default task

def get_google_tasks(service, task_list_id: str) -> List[Dict[str, Any]]:
    logger.info("get_google_tasks: start for list %s", task_list_id)
    raw_tasks = list_tasks(service, task_list_id)
    chores: List[Dict[str, Any]] = []
    for task in raw_tasks:
        chores.append(
            {
                'id': task['id'],
                'title': task.get('title', 'Untitled'),
                'description': task.get('notes', ''),
                'assigned_to': extract_assignee(task.get('notes', '')),
                'due_date': parse_iso_date(task.get('due')),
                'completed': task.get('status') == 'completed',
                'category': None,
                'priority': 'high' if '!' in task.get('title', '') else 'low',
            }
        )
    return chores

def extract_assignee(notes: str | None) -> Optional[str]:
    if not notes:
        return None
    match = re.search(r'Assigned to:\s*(\w+)', notes)
    return match.group(1) if match else None

def parse_iso_date(iso: str | None):
    return datetime.fromisoformat(iso.replace('Z', '+00:00')) if iso else None

def get_or_create_task_list(service, list_title: str = "Family chores") -> str:
    response = service.tasklists().list().execute()
    for tasklist in response.get('items', []):
        if tasklist['title'].strip().lower() == list_title.strip().lower():
            return tasklist['id']
    created = service.tasklists().insert(body={'title': list_title}).execute()
    logger.info("Created task list '%s' (%s)", created['title'], created['id'])
    return created['id']