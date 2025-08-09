"""API for fetching meal data from Google Calendar.

This module provides functions to interact with the Google Calendar API
to retrieve meal events for the FamilyHub Mealboard.
"""

import os, datetime, pytz
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CAL_ID = os.getenv("FAMILYHUB_CALENDAR_ID")


def get_meals():
    """Fetches meal events from Google Calendar for a 15-day window.

    Returns:
        A dictionary mapping ISO date strings to a list of meal titles,
        or an error dictionary if configuration is missing.
    """
    # Check for required environment variables
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        return {"error": "Missing GOOGLE_APPLICATION_CREDENTIALS or file not found"}
    if not CAL_ID:
        return {"error": "Missing FAMILYHUB_CALENDAR_ID"}

    # Authenticate and build the Google Calendar service
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    svc = build("calendar", "v3", credentials=creds, cache_discovery=False)

    # Define the time window for fetching events (+/- 7 days from today)
    tz = pytz.timezone(os.getenv("FAMILYHUB_TZ", "America/Chicago"))
    now = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_dt = now - relativedelta(days=7)
    end_dt = now + relativedelta(days=7, hours=23, minutes=59)

    # Fetch events from the calendar
    res = (
        svc.events()
        .list(
            calendarId=CAL_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    # Process the fetched events
    items = res.get("items", [])
    # Initialize the output dictionary with all dates in the window
    out = {}
    for i in range(-7, 8):
        d = (now + relativedelta(days=i)).date().isoformat()
        out[d] = []

    # Populate the output dictionary with event summaries
    for e in items:
        start = e["start"].get("date") or e["start"].get("dateTime", "")[:10]
        if start in out:
            out[start].append(e.get("summary", "Dinner"))
    return out
