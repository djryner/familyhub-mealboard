import os
import datetime
import pytz
import logging
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CAL_ID = os.getenv('FAMILYHUB_CALENDAR_ID')

logger = logging.getLogger("calendar_api")

def get_meals():
    """Fetch dinner plans from a shared Google Calendar.

    Returns a dictionary mapping ISO-formatted dates to lists of meal names.
    If required environment variables are missing, an error dictionary is
    returned instead.
    """
    logger.info("get_meals called")
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


    if not creds_path or not os.path.exists(creds_path):
        return {"error": "Missing GOOGLE_APPLICATION_CREDENTIALS or file not found"}
    if not CAL_ID:
        return {"error": "Missing FAMILYHUB_CALENDAR_ID"}

   # Always use America/Chicago timezone
    tz_name = 'America/Chicago'
    tz = pytz.timezone(tz_name)
    now = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_dt = now - relativedelta(days=7)
    end_dt = now + relativedelta(days=7, hours=23, minutes=59)
    logger.info(f"Fetching events from {start_dt.isoformat()} to {end_dt.isoformat()}")
    
    try:
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        svc = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        res = svc.events().list(
            calendarId=CAL_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except Exception as e:
        logger.error(f"Exception while setting up Google Calendar client or fetching events: {e}")
        return {"error": f"Exception while setting up Google Calendar client or fetching events: {e}"}


    try:
        res = svc.events().list(
            calendarId=CAL_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except Exception as e:
        logger.error(f"Exception while fetching events: {e}")
        return {"error": f"Exception while fetching events: {e}"}


    items = res.get('items', [])
    logger.info(f"Number of events fetched: {len(items)}")
    out = {}
    for i in range(-7, 8):
        d = (now + relativedelta(days=i)).date().isoformat()
        out[d] = []

    for e in items:
        start = e['start'].get('date') or e['start'].get('dateTime', '')[:10]
        if start in out:
            out[start].append(e.get('summary', 'Dinner'))
    return out
