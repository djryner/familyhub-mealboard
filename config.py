"""Application configuration helpers.

Centralizes environment variable lookups so other modules do not read os.environ
directly (easier to test and reason about). Keep this intentionally lightweight
instead of introducing Pydantic for now.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Defines the application's configuration settings, loaded from environment variables."""

    # Secret key for signing session cookies
    session_secret: str = os.getenv("SESSION_SECRET", "devcontainer-secret-key")
    # Database connection URL
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///familyhub.db")
    # Title of the Google Tasks list to use for chores
    google_tasks_list_title: str = os.getenv("TASKS_LIST_TITLE", "Family chores")
    # Timezone for the application (e.g., 'America/Chicago')
    timezone: str = os.getenv("FAMILYHUB_TZ", "America/Chicago")
    # ID of the Google Calendar to use for meal plans
    calendar_id: str | None = os.getenv("FAMILYHUB_CALENDAR_ID")
    # Path to the Google service account credentials file
    google_credentials_path: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_settings() -> Settings:
    """Returns a frozen instance of the application settings."""
    return Settings()
