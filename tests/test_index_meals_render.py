"""Integration tests for the index page rendering logic."""

from datetime import date
import pytest

from app import app
import routes


@pytest.fixture
def client(monkeypatch):
    """A pytest fixture that provides a test client for the Flask app.

    It also mocks the `fetch_meals` function to return predictable data.
    """

    # A simple mock for the MealDTO object.
    class DummyMeal:
        def __init__(self, d, title):
            self.date = d
            self.title = title

    today = date.today()
    dummy_data = [
        DummyMeal(today, "Meal A"),
        DummyMeal(today, "Meal B"),  # A second meal on the same day.
    ]

    def fake_fetch_meals(start=None, end=None):
        return dummy_data

    def fake_fetch_chores(include_completed=False, limit=None):
        return []

    # The `routes` module imports these functions directly, so we patch them there.
    monkeypatch.setattr(routes, "fetch_meals", fake_fetch_meals)
    monkeypatch.setattr(routes, "fetch_chores", fake_fetch_chores)
    return app.test_client()


def test_index_renders_meals(client):
    """Tests that the index page correctly renders multiple meals for the same day."""
    # Execution: Make a GET request to the index page.
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode()

    # Verification: Check that both meal titles are present in the HTML.
    assert "Meal A" in html and "Meal B" in html
    # Check that a separator is rendered between the two meals.
    assert " \u2022 " in html or " • " in html
