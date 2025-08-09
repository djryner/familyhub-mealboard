from datetime import date, datetime

from services.meals_service import fetch_meals
import services.calendar_service as cal


def monkey_calendar(monkeypatch, mapping):
    def fake_get_meals(calendar_id=None, *, days=7):
        return mapping
    monkeypatch.setattr(cal, 'get_meals', fake_get_meals)


def test_fetch_meals_normalizes_dates_and_titles(monkeypatch):
    mapping = {
        date.today().isoformat(): ["Honey Sesame Chicken", "Tacos"],
        datetime.now().isoformat(): ["Duplicate Day Meal"],  # datetime string
    }
    monkey_calendar(monkeypatch, mapping)
    meals = fetch_meals()
    assert all(isinstance(m.date, date) for m in meals)
    titles = [m.title for m in meals]
    assert "Honey Sesame Chicken" in titles
    assert "Tacos" in titles


def test_week_filter_includes_today_and_limits(monkeypatch):
    today = date.today()
    mapping = { today.isoformat(): [f"Meal {i}" for i in range(1, 5)] }
    monkey_calendar(monkeypatch, mapping)
    meals = fetch_meals(start=today, end=today)
    assert len(meals) == 4  # de-dup not triggered (unique titles)
    assert all(m.date == today for m in meals)
