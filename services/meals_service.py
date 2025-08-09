"""Meals service abstraction.

Provides a single normalized fetch_meals() function that both the
dashboard index route and the meal plans page use. This wraps the
calendar_service.get_meals() mapping (ISO date -> list[str]) and
produces a list of MealDTO objects with consistent field names.

Responsibilities:
* Fetch raw mapping from calendar_service
* Normalize/validate dates (accept str/datetime/date)
* Emit MealDTO(date=<datetime.date>, title=<str>) entries
* Optional date range filtering (inclusive)
* Deterministic de-duplication rule for multiple meals on the same day
  with the same title: keep the last occurrence encountered (later in
  raw list order from calendar API) to provide an intuitive override
  mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional
import logging

from services import calendar_service

logger = logging.getLogger("meals_service")


@dataclass(slots=True)
class MealDTO:
    date: date
    title: str
    notes: Optional[str] = None  # reserved for future expansion


def _to_date(val) -> Optional[date]:
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return date.fromisoformat(val[:10])
        except ValueError:
            return None
    return None


def fetch_meals(*, start: Optional[date] = None, end: Optional[date] = None) -> List[MealDTO]:
    """Return normalized meal entries.

    Parameters
    ----------
    start, end : date | None
        If provided, inclusive bounding window. If omitted, all meals
        returned by the underlying calendar mapping are included.
    """
    raw = calendar_service.get_meals()
    if isinstance(raw, dict) and "error" in raw:
        logger.warning("fetch_meals: underlying calendar_service error: %s", raw["error"])
        return []
    meals: List[MealDTO] = []
    for iso_day, titles in raw.items():
        d = _to_date(iso_day)
        if not d:
            continue
        if start and d < start:
            continue
        if end and d > end:
            continue
        for t in titles:
            meals.append(MealDTO(date=d, title=t))

    # De-dup rule: keep last occurrence of duplicate (date,title)
    dedup: dict[tuple[date, str], MealDTO] = {}
    for m in meals:
        dedup[(m.date, m.title)] = m

    ordered = sorted(dedup.values(), key=lambda m: (m.date, m.title.lower()))
    logger.info(
        "fetch_meals: raw_events=%d unique=%d window=%s..%s", len(meals), len(ordered), start, end
    )
    # Provide a compact per-day listing for observability (INFO so it surfaces in basic logs)
    if ordered:
        # Group by date preserving order
        by_date: dict[date, list[str]] = {}
        for m in ordered:
            by_date.setdefault(m.date, []).append(m.title)
        for d, titles in by_date.items():  # pragma: no cover (log only)
            logger.info("fetch_meals: day %s -> %s", d.isoformat(), ", ".join(titles))
    return ordered
