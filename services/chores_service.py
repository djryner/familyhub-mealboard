"""Chores service abstraction.

Single source of truth for chores. Currently backed by Google Tasks.
Provides a narrow, testable seam so routes/templates don't reach directly
into tasks_api or the database. A future CHORES_BACKEND switch can enable
an alternate implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timezone
from typing import List, Optional
import os
import logging

from tasks_api import (
    build_google_service,
    get_or_create_task_list,
    get_google_tasks,
)

logger = logging.getLogger("chores_service")

# Optional backend flag (future: implement DB branch if needed)
CHORES_BACKEND = os.getenv("CHORES_BACKEND", "google").lower()


@dataclass
class ChoreDTO:
    id: str
    title: str
    assigned_to: Optional[str]
    due_date: Optional[date]
    priority: str  # 'low' | 'medium' | 'high'
    completed: bool
    notes: Optional[str] = None


def _service_and_list():
    """Return (service, task_list_id) tuple."""
    svc = build_google_service()
    task_list_id = get_or_create_task_list(svc, "Family chores")
    return svc, task_list_id


def _google_fetch() -> List[ChoreDTO]:
    logger.info("_google_fetch: building service & retrieving task list")
    svc, task_list_id = _service_and_list()
    logger.info("_google_fetch: using task_list_id=%s", task_list_id)
    tasks = get_google_tasks(svc, task_list_id)
    logger.info("_google_fetch: retrieved %d raw tasks", len(tasks))
    out: List[ChoreDTO] = []
    for t in tasks:
        due = t.get("due_date")
        # due might be datetime or str; normalize to date
        if hasattr(due, "date"):
            due_dt = due.date() if isinstance(due, datetime) else due
        else:
            try:
                due_dt = datetime.fromisoformat(due[:10]).date() if due else None  # type: ignore[arg-type]
            except Exception:
                due_dt = None
        out.append(ChoreDTO(
            id=t.get("id"),
            title=t.get("title"),
            assigned_to=t.get("assigned_to"),
            due_date=due_dt,
            priority=t.get("priority", "low"),
            completed=bool(t.get("completed")),
            notes=t.get("description") or t.get("notes"),
        ))
    return out


def fetch_chores(start: Optional[date] = None, end: Optional[date] = None, *, include_completed: bool = True, limit: Optional[int] = None) -> List[ChoreDTO]:
    """Return normalized chores from the configured backend.

    Dates are normalized to datetime.date in ChoreDTO.due_date. Optional
    start/end filters (inclusive) applied if provided.
    """
    if CHORES_BACKEND != "google":  # placeholder for future DB backend
        logger.warning("Non-google backend not implemented; defaulting to google")
    logger.info(
        "fetch_chores: start=%s end=%s include_completed=%s limit=%s", start, end, include_completed, limit
    )
    chores = _google_fetch()
    logger.info("fetch_chores: %d chores after raw fetch", len(chores))
    if not include_completed:
        chores = [c for c in chores if not c.completed]
        logger.info("fetch_chores: filtered to %d incomplete chores", len(chores))
    if start:
        chores = [c for c in chores if c.due_date and c.due_date >= start]
    if end:
        chores = [c for c in chores if c.due_date and c.due_date <= end]
    # Sort by due date (None at end), then title
    chores.sort(key=lambda c: (c.due_date or date.max, c.title.lower()))
    if limit is not None and len(chores) > limit:
        chores = chores[:limit]
        logger.info("fetch_chores: truncated to limit -> %d chores", len(chores))
    # Log a brief summary (ids & titles)
    if chores:
        preview = ", ".join(f"{c.id}:{c.title}" for c in chores[:5])
        logger.info("fetch_chores: returning %d chores (preview: %s%s)", len(chores), preview, "..." if len(chores) > 5 else "")
    return chores


def complete_chore(chore_id: str) -> None:
    if CHORES_BACKEND != "google":  # future DB path
        raise NotImplementedError("Only google backend supported")
    svc = build_google_service()
    task_list_id = get_or_create_task_list(svc, "Family chores")
    task = svc.tasks().get(tasklist=task_list_id, task=chore_id).execute()
    if task.get("status") != "completed":
        task["status"] = "completed"
        task["completed"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        svc.tasks().update(tasklist=task_list_id, task=chore_id, body=task).execute()
        logger.info("Marked chore %s complete", chore_id)
    else:
        logger.info("Chore %s already complete", chore_id)


def create_chore(
    title: str,
    assigned_to: Optional[str] = None,
    due_date: Optional[date] = None,
    priority: str = "low",
    notes: Optional[str] = None,
) -> ChoreDTO:
    """Create a new chore in Google Tasks and return its DTO.

    Extra metadata is encoded into the task notes (assigned/category/priority tags)
    so they travel with the task in a backend-agnostic way.
    """
    if CHORES_BACKEND != "google":  # future DB path
        raise NotImplementedError("Only google backend supported")
    svc, task_list_id = _service_and_list()
    # Compose notes field
    meta_parts = []
    if assigned_to:
        meta_parts.append(f"assigned:{assigned_to}")
    if priority:
        meta_parts.append(f"priority:{priority}")
    combined_notes = (notes.strip() if notes else "")
    if meta_parts:
        if combined_notes:
            combined_notes += "\n"
        combined_notes += " | ".join(meta_parts)
    body: dict = {"title": title}
    if combined_notes:
        body["notes"] = combined_notes
    if due_date:
        body["due"] = due_date.isoformat() + "T00:00:00.000Z"
    task = svc.tasks().insert(tasklist=task_list_id, body=body).execute()
    logger.info("create_chore: created task %s (%s)", task.get("title"), task.get("id"))
    # Return normalized DTO by refetching that single task fields
    return ChoreDTO(
        id=task.get("id"),
        title=task.get("title"),
        assigned_to=assigned_to,
        due_date=due_date,
        priority=priority,
        completed=False,
        notes=combined_notes or None,
    )
