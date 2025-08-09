from datetime import date, datetime, timedelta
import zoneinfo

WK = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
BY = {0:"MO",1:"TU",2:"WE",3:"TH",4:"FR",5:"SA",6:"SU"}

def next_on_or_after(start: date, target_wd: int) -> date:
    """Return the date that is start if start.weekday()==target_wd else next future date with that weekday."""
    delta = (target_wd - start.weekday()) % 7
    return start + timedelta(days=delta)


def next_in_set_on_or_after(start: date, wdays: set[int]) -> date:
    for i in range(7):
        d = start + timedelta(days=i)
        if d.weekday() in wdays:
            return d
    return start  # fallback, though loop always returns within 7 days


def to_utc_midnight_rfc3339(d: date, tz_name: str | None = None) -> str:
    """Return RFC3339 UTC midnight string for the given local date."""
    tz = zoneinfo.ZoneInfo(tz_name) if tz_name else datetime.now().astimezone().tzinfo
    # Local midnight
    local_midnight = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=tz)
    # Convert to UTC
    utc_dt = local_midnight.astimezone(zoneinfo.ZoneInfo("UTC"))
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
