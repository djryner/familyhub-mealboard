from datetime import date
import pytest

from app import app
import routes


@pytest.fixture
def client(monkeypatch):
    class DummyMeal:
        def __init__(self, d, title):
            self.date = d
            self.title = title
    today = date.today()
    dummy_data = [
        DummyMeal(today, 'Meal A'),
        DummyMeal(today, 'Meal B'),  # same day second meal
    ]
    def fake_fetch_meals(start=None, end=None):
        return dummy_data
    # routes imported fetch_meals directly; patch there
    monkeypatch.setattr(routes, 'fetch_meals', fake_fetch_meals)
    return app.test_client()


def test_index_renders_meals(client):
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'Meal A' in html and 'Meal B' in html
    assert ' \u2022 ' in html or ' • ' in html  # ensure separator present
