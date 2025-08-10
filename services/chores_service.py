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
from models import ChoreMetadata, ChoreOccurrence
from db import db

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

def fetch_chores(start: Optional[date]=None, end: Optional[date]=None, *, include_completed=True, limit=None) -> List[ChoreDTO]:
    """Fetch all chore occurrences, optionally filtered by date/status."""
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
        dtos.append(ChoreDTO(
            id=occ.id,
            title=meta.title,
            assigned_to=meta.assigned_to,
            due_date=occ.due_date,
            status=occ.status,
            points=meta.points
        ))
    return dtos

def create_chore(title: str, assigned_to: Optional[str], due_date: date, points: int = 1, recurrence: Optional[str] = None) -> ChoreDTO:
    """Create a new recurring chore definition and its first occurrence."""
    # Generate a unique task_id (could use uuid4 or slug)
    import uuid
    task_id = str(uuid.uuid4())
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
