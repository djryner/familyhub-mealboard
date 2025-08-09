# FamilyHub Mealboard

## Architecture & Decisions (Work in Progress)

Core layers:
* `app.py` – Flask app factory/initialization & DB setup.
* `routes.py` – HTTP routes (will be split into blueprints in future refactor).
* `calendar_api.py` – Google Calendar meal fetching (returns normalized mapping).
* `services/meals_service.py` – Normalizes meal events into `MealDTO` objects for both dashboard and meal plans pages.
* `tasks_api.py` – Low-level Google Tasks integration helpers.
* `services/chores_service.py` – Single source of truth for chores (Google Tasks backend) exposing DTOs.
* `models.py` – SQLAlchemy models (currently only `ChoreTemplate`).

Refactor improvements added:
* Logging standardization for calendar & dashboard flows.
* Defensive error handling around credentials / calendar id.
* Initial test coverage for calendar error paths (`tests/test_calendar_api.py`).
* Unified chores service + tests (`tests/test_chores_service.py`).
* Pre-commit with Black, Ruff, mypy for consistency.

## Local Development

Install dependencies:
```
pip install -r requirements.txt
```

Run app:
```
python main.py
```

Run tests:
```
pytest -q
```

## Pending Work
Planned next steps include:
* Introduce blueprints (`/api`, `/dashboard`).
* (Done) Added service layer for meals (`services/meals_service.py`).
* Expand tests for route responses (index, chores, meal-plans).
* Add type checking gate in CI.

# familyhub-mealboard

## Google Calendar dinner plans

The application fetches dinner plans from a shared Google Calendar. Raw events
are first retrieved by `services/calendar_service.get_meals()` (mapping of ISO
date -> list of titles). Both the Dashboard ("Meals This Week") and Meal Plans
pages consume the unified `services/meals_service.fetch_meals()` function which
emits a list of `MealDTO(date, title)` objects. This ensures consistent
normalization (dates always `datetime.date`, field name always `title`).

The legacy `/api/meals` endpoint still exposes the mapping form for backwards
compatibility.

### Setup
1. **Create a Google service account** and download its JSON key.
2. **Share the calendar** with the service account's e‑mail (read access is
   enough).
3. Set the following environment variables:

   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to the downloaded JSON key file.
   - `FAMILYHUB_CALENDAR_ID`: ID of the shared calendar.
   - Optional `FAMILYHUB_TZ`: Timezone name (defaults to `America/Chicago`).

With these variables configured, the `/api/meals` route returns the mapping
while the UI uses the DTO list. If multiple events share the same date and
title, only the last one is kept (deterministic de-duplication rule).

## Chores Source of Truth

Chores are currently sourced exclusively from Google Tasks via `services/chores_service.py`.

Environment flag `CHORES_BACKEND` (default `google`) is reserved for a future
DB-backed implementation. Routes and templates must not call `tasks_api` directly;
they should use the service to ensure consistent normalization and persistence.