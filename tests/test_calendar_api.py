import os
from calendar_api import get_meals


def test_get_meals_missing_credentials(monkeypatch):
    monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS', raising=False)
    monkeypatch.setenv('FAMILYHUB_CALENDAR_ID', 'dummy')
    data = get_meals()
    assert 'error' in data
    assert 'Missing GOOGLE_APPLICATION_CREDENTIALS' in data['error']


def test_get_meals_missing_calendar_id(monkeypatch, tmp_path):
    # create dummy creds file path
    creds_file = tmp_path / 'creds.json'
    creds_file.write_text('{}')
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', str(creds_file))
    monkeypatch.delenv('FAMILYHUB_CALENDAR_ID', raising=False)
    data = get_meals()
    assert 'error' in data
    assert 'Missing FAMILYHUB_CALENDAR_ID' in data['error']
