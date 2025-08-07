
import os, datetime, pytz
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CAL_ID = os.getenv('FAMILYHUB_CALENDAR_ID')

def get_meals():
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        return {"error": "Missing GOOGLE_APPLICATION_CREDENTIALS or file not found"}
    if not CAL_ID:
        return {"error": "Missing FAMILYHUB_CALENDAR_ID"}

    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    svc = build('calendar', 'v3', credentials=creds, cache_discovery=False)

    tz = pytz.timezone(os.getenv('FAMILYHUB_TZ', 'America/Chicago'))
    now = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_dt = now - relativedelta(days=7)
    end_dt = now + relativedelta(days=7, hours=23, minutes=59)

    res = svc.events().list(
        calendarId=CAL_ID,
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    items = res.get('items', [])
    out = {}
    for i in range(-7, 8):
        d = (now + relativedelta(days=i)).date().isoformat()
        out[d] = []

    for e in items:
        start = e['start'].get('date') or e['start'].get('dateTime', '')[:10]
        if start in out:
            out[start].append(e.get('summary', 'Dinner'))
    return out
