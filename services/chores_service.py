def ignore_uncompleted_chores_before_today():
    """Mark all chores due before today as ignored if not already completed or ignored."""
    today = date.today()
    pending = ChoreOccurrence.query.filter(
        ChoreOccurrence.due_date < today,
        ChoreOccurrence.status == 'pending'
    ).all()
    for occ in pending:
        occ.status = 'ignored'
        occ.ignored_at = datetime.utcnow()
    db.session.commit()

from datetime import datetime, date, timedelta
from typing import List, Optional
import logging

from flask import has_app_context

from db import db
from models import ChoreMetadata, ChoreOccurrence
from tasks_api import (
    build_google_service,
    patch_task_status,
    get_task,
    get_or_create_task_list,
    get_google_tasks,
    TASK_LIST_ID,
)
from .schedule_utils import to_utc_midnight_rfc3339

logger = logging.getLogger("chores_service")


def to_rrule(recurrence: str, day: str | None = None) -> list[str] | None:
    """Convert a simple recurrence string into a Google Tasks RRULE list."""
    r = recurrence.lower()
    if r == "daily":
        return ["RRULE:FREQ=DAILY"]
    if r == "schooldays":
        return ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]
    if r == "weekends":
        return ["RRULE:FREQ=WEEKLY;BYDAY=SA,SU"]
    if r == "weekly" and day:
        day_map = {
            "monday": "MO",
            "tuesday": "TU",
            "wednesday": "WE",
            "thursday": "TH",
            "friday": "FR",
            "saturday": "SA",
            "sunday": "SU",
        }
        abbr = day_map.get(day.lower())
        if abbr:
            return [f"RRULE:FREQ=WEEKLY;BYDAY={abbr}"]
    return None

def _parse_rrule(rrule: str, after: date) -> Optional[date]:
    """Given an RRULE string and a date, return the next due date after the given date."""
    # Only basic support for FREQ=DAILY, WEEKLY, BYDAY, etc.
    if not rrule:
        return None
    rule = rrule.upper()
    if rule.startswith("RRULE:FREQ=DAILY"):
        return after + timedelta(days=1)
    if rule.startswith("RRULE:FREQ=WEEKLY"):
        # Parse BYDAY
        import re
        m = re.search(r"BYDAY=([A-Z,]+)", rule)
        if not m:
            return after + timedelta(days=7)
        days = m.group(1).split(",")
        # Map weekday string to Python weekday (MO=0, SU=6)
        day_map = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}
        after_wd = after.weekday()
        # Find the next day in BYDAY after 'after'
        offsets = sorted((day_map[d] - after_wd) % 7 for d in days)
        for offset in offsets:
            if offset > 0:
                return after + timedelta(days=offset)
        # If none found, return the first in the next week
        return after + timedelta(days=offsets[0] if offsets else 7)
    return None

class ChoreDTO:
    def __init__(self, id, title, assigned_to, due_date, status, points):
        self.id = id
        self.title = title
        self.assigned_to = assigned_to
        self.due_date = due_date
        self.status = status
        self.completed = status == 'completed'
        self.points = points

def fetch_chores(start: Optional[date] = None, end: Optional[date] = None, *, include_completed=True, limit=None) -> List[ChoreDTO]:
    """Fetch all chore occurrences, optionally filtered by date/status."""
    if not has_app_context():
        # Fallback: pull tasks from Google when no DB context is available (e.g., tests)
        service = build_google_service()
        list_id = get_or_create_task_list(service, "Family chores")
        tasks = get_google_tasks(service, list_id)
        dtos = []
        for t in tasks:
            due = t.get("due_date") or t.get("due")
            if isinstance(due, str):
                try:
                    due = date.fromisoformat(due)
                except ValueError:
                    due = None
            dtos.append(
                ChoreDTO(
                    id=t["id"],
                    title=t.get("title"),
                    assigned_to=t.get("assigned_to"),
                    due_date=due,
                    status="completed" if t.get("completed") else "pending",
                    points=t.get("points", 1),
                )
            )
        return dtos

    q = ChoreOccurrence.query
    if not include_completed:
        q = q.filter(ChoreOccurrence.status == 'pending')
    if start:
        q = q.filter(ChoreOccurrence.due_date >= start)
    if end:
        q = q.filter(ChoreOccurrence.due_date <= end)
    q = q.order_by(ChoreOccurrence.due_date.asc())
    if limit:
        q = q.limit(limit)
    results = q.all()
    dtos = []
    for occ in results:
        meta = occ.chore_def
        if meta is None:
            # Orphaned occurrence, skip it
            continue
        dtos.append(
            ChoreDTO(
                id=occ.id,
                title=meta.title,
                assigned_to=meta.assigned_to,
                due_date=occ.due_date,
                status=occ.status,
                points=meta.points,
            )
        )
    return dtos

def create_chore(title: str, assigned_to: Optional[str], due_date: date, points: int = 1, recurrence: Optional[str] = None) -> ChoreDTO:
    """Create a new recurring chore definition and its first occurrence."""
    # Create the task in Google Tasks and use the returned id as task_id
    from tasks_api import build_google_service, create_task, TASK_LIST_ID
    import logging
    logger = logging.getLogger("chores_service")
    service = build_google_service()
    due_rfc3339 = due_date.isoformat() + "T00:00:00Z"
    notes = f"Assigned to: {assigned_to}" if assigned_to else None
    task_body = {"title": title, "due": due_rfc3339}
    if notes:
        task_body["notes"] = notes
    if recurrence:
        task_body["recurrence"] = [recurrence] if not recurrence.startswith("RRULE:") else [recurrence]
    google_task = service.tasks().insert(tasklist=TASK_LIST_ID, body=task_body).execute()
    task_id = google_task["id"]
    logger.info(f"create: title={title} due={due_rfc3339} recurrence={recurrence} returned_id={task_id}")
    meta = ChoreMetadata()
    meta.task_id = task_id
    meta.title = title
    meta.assigned_to = assigned_to
    meta.recurrence = recurrence
    meta.points = points
    occ = ChoreOccurrence()
    occ.task_id = task_id
    occ.due_date = due_date
    occ.status = 'pending'
    db.session.add(meta)
    db.session.add(occ)
    db.session.commit()
    return ChoreDTO(id=occ.id, title=title, assigned_to=assigned_to, due_date=due_date, status='pending', points=points)

def complete_chore(occurrence_id: int) -> None:
    """Mark a chore occurrence as completed and insert the next occurrence if recurring."""
    if not has_app_context():
        service = build_google_service()
        list_id = get_or_create_task_list(service, "Family chores")
        task = service.tasks().get(tasklist=list_id, task=occurrence_id).execute()
        task["status"] = "completed"
        service.tasks().update(tasklist=list_id, task=occurrence_id, body=task).execute()
        return

    occ = ChoreOccurrence.query.get(occurrence_id)
    if not occ or occ.status != 'pending':
        return
    occ.status = 'completed'
    occ.completed_at = datetime.utcnow()
    meta = occ.chore_def
    # Insert next occurrence if recurring
    if meta.recurrence:
        next_due = _parse_rrule(meta.recurrence, occ.due_date)
        if next_due:
            exists = ChoreOccurrence.query.filter_by(task_id=meta.task_id, due_date=next_due).first()
            if not exists:
                new_occ = ChoreOccurrence()
                new_occ.task_id = meta.task_id
                new_occ.due_date = next_due
                new_occ.status = 'pending'
                db.session.add(new_occ)
    db.session.commit()

def ignore_chore(occurrence_id: int) -> None:
    """Mark a chore occurrence as ignored and insert the next occurrence if recurring."""
    occ = ChoreOccurrence.query.get(occurrence_id)
    if not occ or occ.status != 'pending':
        return
    occ.status = 'ignored'
    occ.ignored_at = datetime.utcnow()
    meta = occ.chore_def
    # Insert next occurrence if recurring
    if meta.recurrence:
        next_due = _parse_rrule(meta.recurrence, occ.due_date)
        if next_due:
            exists = ChoreOccurrence.query.filter_by(task_id=meta.task_id, due_date=next_due).first()
            if not exists:
                new_occ = ChoreOccurrence()
                new_occ.task_id = meta.task_id
                new_occ.due_date = next_due
                new_occ.status = 'pending'
                db.session.add(new_occ)
    db.session.commit()

def auto_ignore_overdue():
    """Mark all overdue pending chores as ignored and insert next occurrence if recurring."""
    today = date.today()
    overdue = ChoreOccurrence.query.filter(ChoreOccurrence.status == 'pending', ChoreOccurrence.due_date < today).all()
    for occ in overdue:
        occ.status = 'ignored'
        occ.ignored_at = datetime.utcnow()
        meta = occ.chore_def
        if meta.recurrence:
            next_due = _parse_rrule(meta.recurrence, occ.due_date)
            if next_due:
                exists = ChoreOccurrence.query.filter_by(task_id=meta.task_id, due_date=next_due).first()
                if not exists:
                    new_occ = ChoreOccurrence()
                    new_occ.task_id = meta.task_id
                    new_occ.due_date = next_due
                    new_occ.status = 'pending'
                    db.session.add(new_occ)
    db.session.commit()

def complete_chore_occurrence(task_id: str, due_iso: str = None):
    """Mark only the current occurrence as complete in Google Tasks, log, and refetch."""
    service = build_google_service()
    list_id = TASK_LIST_ID
    # Warn if task_id looks like a fake UUID (not a Google Task ID)
    import re
    if re.fullmatch(r"[0-9a-fA-F\-]{36}", task_id):
        logger.warning(f"Task ID {task_id} looks like a local UUID, not a Google Task ID. This will fail with Google Tasks API.")
    # 1. Fetch pre-patch task
    pre = get_task(service, list_id, task_id)
    pre_due = pre.get("due")
    # 2. Patch status to completed
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    patch_task_status(service, list_id, task_id, status="completed", completed_iso=now_iso)
    # 3. Refetch task
    post = get_task(service, list_id, task_id)
    post_due = post.get("due")
    logger.info(f"complete: id={task_id} pre_due={pre_due} post_due={post_due}")
    return post
