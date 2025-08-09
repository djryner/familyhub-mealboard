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
from models import ChoreMetadata
from db import db

logger = logging.getLogger("chores_service")

# Optional backend flag (future: implement DB branch if needed)
CHORES_BACKEND = os.getenv("CHORES_BACKEND", "google").lower()


@dataclass
class ChoreDTO:
    """Data Transfer Object for a chore, providing a stable, backend-agnostic interface."""

    id: str
    title: str
    assigned_to: Optional[str]
    due_date: Optional[date]
    priority: str  # 'low' | 'medium' | 'high'
    completed: bool
    notes: Optional[str] = None


def _service_and_list():
    """Initializes the Google service and gets the target task list ID."""
    svc = build_google_service()
    task_list_id = get_or_create_task_list(svc, "Family chores")
    return svc, task_list_id


def _google_fetch() -> List[ChoreDTO]:
    """Fetches all tasks from Google and normalizes them into ChoreDTOs, using local metadata if available."""
    logger.info("_google_fetch: building service & retrieving task list")
    svc, task_list_id = _service_and_list()
    logger.info("_google_fetch: using task_list_id=%s", task_list_id)
    tasks = get_google_tasks(svc, task_list_id)
    logger.info("_google_fetch: retrieved %d raw tasks", len(tasks))

    # Fetch all metadata in one go for efficiency
    try:
        meta_map = {m.task_id: m for m in ChoreMetadata.query.all()}
    except Exception:  # pragma: no cover - occurs when DB not initialized
        meta_map = {}

    out: List[ChoreDTO] = []
    for t in tasks:
        due = t.get("due_date")
        due_dt = None
        # The due date from the API can be a datetime object or an ISO string.
        if hasattr(due, "date"):
            due_dt = due.date() if isinstance(due, datetime) else due
        else:
            try:
                due_dt = (
                    datetime.fromisoformat(due[:10]).date() if due else None
                )
            except (TypeError, ValueError):
                due_dt = None
        task_id = str(t.get("id") or "")
        title = str(t.get("title") or "")
        meta = meta_map.get(task_id)
        out.append(
            ChoreDTO(
                id=task_id,
                title=title,
                assigned_to=meta.assigned_to if meta else None,
                due_date=due_dt,
                priority=meta.priority if meta else "low",
                completed=bool(t.get("completed")),
                notes=t.get("description") or t.get("notes"),
            )
        )
    return out


def fetch_chores(
    start: Optional[date] = None,
    end: Optional[date] = None,
    *,
    include_completed: bool = True,
    limit: Optional[int] = None,
) -> List[ChoreDTO]:
    """Fetches and filters chores from the configured backend.

    Args:
        start: The start date for filtering chores (inclusive).
        end: The end date for filtering chores (inclusive).
        include_completed: Whether to include completed chores in the result.
        limit: The maximum number of chores to return.

    Returns:
        A sorted and filtered list of ChoreDTOs.
    """
    if CHORES_BACKEND != "google":  # placeholder for future DB backend
        logger.warning("Non-google backend not implemented; defaulting to google")

    logger.info(
        "fetch_chores: start=%s end=%s include_completed=%s limit=%s",
        start,
        end,
        include_completed,
        limit,
    )
    chores = _google_fetch()
    logger.info("fetch_chores: %d chores after raw fetch", len(chores))

    # Apply filters based on arguments
    if not include_completed:
        chores = [c for c in chores if not c.completed]
        logger.info("fetch_chores: filtered to %d incomplete chores", len(chores))
    if start:
        chores = [c for c in chores if c.due_date and c.due_date >= start]
    if end:
        chores = [c for c in chores if c.due_date and c.due_date <= end]

    # Sort chores by due date (placing chores without a due date at the end), then by title.
    chores.sort(key=lambda c: (c.due_date or date.max, c.title.lower()))

    # Apply the limit after sorting
    if limit is not None and len(chores) > limit:
        chores = chores[:limit]
        logger.info("fetch_chores: truncated to limit -> %d chores", len(chores))

    # Log a brief summary for debugging
    if chores:
        preview = ", ".join(f"{c.id}:{c.title}" for c in chores[:5])
        logger.info(
            "fetch_chores: returning %d chores (preview: %s%s)",
            len(chores),
            preview,
            "..." if len(chores) > 5 else "",
        )
    return chores


def complete_chore(chore_id: str) -> None:
    """Marks a specific chore as complete in the backend."""
    if CHORES_BACKEND != "google":
        raise NotImplementedError("Only google backend supported")
    svc, task_list_id = _service_and_list()
    task = svc.tasks().get(tasklist=task_list_id, task=chore_id).execute()
    # Only update the task if it's not already completed to avoid unnecessary API calls.
    if task.get("status") != "completed":
        task["status"] = "completed"
        task["completed"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
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
    """Creates a new chore in the backend and stores metadata locally."""
    if CHORES_BACKEND != "google":
        raise NotImplementedError("Only google backend supported")
    svc, task_list_id = _service_and_list()

    # Build the request body for the Google Tasks API
    body: dict = {"title": title}
    if notes:
        body["notes"] = notes.strip()
    if due_date:
        # Google Tasks API requires due date in RFC 3339 format.
        body["due"] = due_date.isoformat() + "T00:00:00.000Z"

    # Create the task and log the result
    task = svc.tasks().insert(tasklist=task_list_id, body=body).execute()
    logger.info("create_chore: created task %s (%s)", task.get("title"), task.get("id"))

    # Store metadata in the local database

    # Store metadata in the local database (use SQLAlchemy attribute assignment)
    meta = ChoreMetadata()
    meta.task_id = str(task.get("id") or "")
    meta.assigned_to = assigned_to
    meta.priority = priority
    db.session.add(meta)
    db.session.commit()

    # Return a normalized DTO for the newly created chore
    return ChoreDTO(
        id=task.get("id"),
        title=task.get("title"),
        assigned_to=assigned_to,
        due_date=due_date,
        priority=priority,
        completed=False,
        notes=notes.strip() if notes else None,
    )
