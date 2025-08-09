"""Unit tests for the legacy calendar_api module."""

import os
from calendar_api import get_meals


def test_get_meals_missing_credentials(monkeypatch):
    """Verifies that get_meals returns an error if credentials are not set."""
    # Setup: Ensure credentials and calendar ID environment variables are in a known state.
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setenv("FAMILYHUB_CALENDAR_ID", "dummy")

    # Execution: Call the function under test.
    data = get_meals()

    # Verification: Assert that an error is returned.
    assert "error" in data
    assert "Missing GOOGLE_APPLICATION_CREDENTIALS" in data["error"]


def test_get_meals_missing_calendar_id(monkeypatch, tmp_path):
    """Verifies that get_meals returns an error if the calendar ID is not set."""
    # Setup: Create a dummy credentials file and set the path, but unset the calendar ID.
    creds_file = tmp_path / "creds.json"
    creds_file.write_text("{}")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds_file))
    monkeypatch.delenv("FAMILYHUB_CALENDAR_ID", raising=False)

    # Execution: Call the function under test.
    data = get_meals()

    # Verification: Assert that an error is returned.
    assert "error" in data
    assert "Missing FAMILYHUB_CALENDAR_ID" in data["error"]
