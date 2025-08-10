import pytest
from datetime import date, timedelta
from services.chores_service import to_rrule, to_utc_midnight_rfc3339

def test_to_rrule_daily():
    assert to_rrule("daily") == ["RRULE:FREQ=DAILY"]

def test_to_rrule_schooldays():
    assert to_rrule("schooldays") == ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]

def test_to_rrule_weekends():
    assert to_rrule("weekends") == ["RRULE:FREQ=WEEKLY;BYDAY=SA,SU"]

def test_to_rrule_weekly():
    assert to_rrule("weekly", "friday") == ["RRULE:FREQ=WEEKLY;BYDAY=FR"]

def test_to_rrule_once():
    assert to_rrule("once") is None

def test_to_utc_midnight_rfc3339():
    d = date(2025, 8, 9)
    assert to_utc_midnight_rfc3339(d) == "2025-08-09T00:00:00.000Z"
