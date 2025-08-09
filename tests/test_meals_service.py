"""Unit tests for the meals service."""

from datetime import date, datetime

from services.meals_service import fetch_meals
import services.calendar_service as cal


def monkey_calendar(monkeypatch, mapping):
    """A pytest helper to mock the calendar_service.get_meals function."""

    def fake_get_meals(calendar_id=None, *, days=7):
        return mapping

    monkeypatch.setattr(cal, "get_meals", fake_get_meals)


def test_fetch_meals_normalizes_dates_and_titles(monkeypatch):
    """Tests that fetch_meals correctly processes raw data from the calendar service."""
    # Setup: Create a mock mapping with both date and datetime ISO strings.
    mapping = {
        date.today().isoformat(): ["Honey Sesame Chicken", "Tacos"],
        datetime.now().isoformat(): ["Duplicate Day Meal"],
    }
    monkey_calendar(monkeypatch, mapping)

    # Execution: Fetch the meals.
    meals = fetch_meals()

    # Verification: Ensure dates are normalized and titles are present.
    assert all(isinstance(m.date, date) for m in meals)
    titles = [m.title for m in meals]
    assert "Honey Sesame Chicken" in titles
    assert "Tacos" in titles


def test_week_filter_includes_today_and_limits(monkeypatch):
    """Tests that the date filtering in fetch_meals is inclusive."""
    # Setup: Create a mock mapping for today with multiple meals.
    today = date.today()
    mapping = {today.isoformat(): [f"Meal {i}" for i in range(1, 5)]}
    monkey_calendar(monkeypatch, mapping)

    # Execution: Fetch meals with a window that only includes today.
    meals = fetch_meals(start=today, end=today)

    # Verification: Ensure all meals for today are returned.
    assert len(meals) == 4  # De-duplication is not triggered for unique titles.
    assert all(m.date == today for m in meals)
