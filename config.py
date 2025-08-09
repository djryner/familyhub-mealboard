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
    session_secret: str = os.getenv("SESSION_SECRET", "devcontainer-secret-key")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///familyhub.db")
    google_tasks_list_title: str = os.getenv("TASKS_LIST_TITLE", "Family chores")
    timezone: str = os.getenv("FAMILYHUB_TZ", "America/Chicago")
    calendar_id: str | None = os.getenv("FAMILYHUB_CALENDAR_ID")
    google_credentials_path: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_settings() -> Settings:
    return Settings()
