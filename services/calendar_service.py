"""Calendar service abstraction.

Provides meal (dinner) event retrieval from Google Calendar. Returns a
mapping of ISO date -> list[str] meal names for a +/- window.

This was migrated from the legacy module `calendar_api.py` to live under
`services/` alongside other service abstractions (e.g., chores_service).
External code should import from `services.calendar_service` going forward.
`calendar_api.get_meals` remains as a compatibility re-export.
"""

from __future__ import annotations

import os
import datetime as dt
import logging
from typing import Dict, List

import pytz
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

logger = logging.getLogger("calendar_service")


def _window_dates(center: dt.datetime, days: int = 7) -> List[str]:
    """Generates a list of ISO date strings for a window around a center date.

    Args:
        center: The central datetime for the window.
        days: The number of days to extend on either side of the center date.

    Returns:
        A list of date strings in 'YYYY-MM-DD' format.
    """
    return [
        (center + relativedelta(days=offset)).date().isoformat()
        for offset in range(-days, days + 1)
    ]


def get_meals(calendar_id: str | None = None, *, days: int = 7) -> Dict[str, List[str]]:
    """Fetch dinner (meal) events from the configured Google Calendar.

    Parameters
    ----------
    calendar_id: str | None
        Calendar ID. If None, pulled from env FAMILYHUB_CALENDAR_ID.
    days: int
        Half-window size; total range = today +/- days.

    Returns
    -------
    dict
        Mapping of ISO date string -> list of meal titles. On error returns
        ``{"error": "message"}``.
    """
    logger.info("get_meals called (days=%s)", days)
    # Check for Google credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        logger.error("Credentials path missing or file not found: %s", creds_path)
        return {"error": "Missing GOOGLE_APPLICATION_CREDENTIALS or file not found"}

    # Get calendar ID from parameter or environment variable
    cal_id = calendar_id or os.getenv("FAMILYHUB_CALENDAR_ID")
    if not cal_id:
        logger.error("FAMILYHUB_CALENDAR_ID env var not set")
        return {"error": "Missing FAMILYHUB_CALENDAR_ID"}

    # Determine the timezone for date calculations
    tz_name = os.getenv("FAMILYHUB_TZ", "America/Chicago")
    try:
        tz = pytz.timezone(tz_name)
    except Exception:  # pragma: no cover
        logger.warning("Invalid timezone %s, defaulting to America/Chicago", tz_name)
        tz = pytz.timezone("America/Chicago")

    # Define the time window for fetching calendar events
    now = dt.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_dt = now - relativedelta(days=days)
    end_dt = now + relativedelta(days=days, hours=23, minutes=59)
    logger.info(
        "Fetching events window %s -> %s", start_dt.isoformat(), end_dt.isoformat()
    )

    try:
        # Authenticate and build the Google Calendar service
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES
        )
        svc = build("calendar", "v3", credentials=creds, cache_discovery=False)
        # Fetch events from the calendar
        res = (
            svc.events()
            .list(
                calendarId=cal_id,
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed fetching calendar events: %s", exc)
        return {"error": f"Exception fetching events: {exc}"}

    # Process the fetched events
    items = res.get("items", [])
    logger.info("Fetched %d calendar events", len(items))
    # Initialize the output dictionary with all dates in the window
    out: Dict[str, List[str]] = {d: [] for d in _window_dates(now, days=days)}
    for e in items:
        # Extract the event's start date (handles both all-day and timed events)
        start = (
            e.get("start", {}).get("date")
            or e.get("start", {}).get("dateTime", "")[:10]
        )
        # Add the event summary to the corresponding date in the output
        if start in out:
            out[start].append(e.get("summary", "Dinner"))
    return out
