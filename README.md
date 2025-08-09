# FamilyHub Mealboard

## Architecture & Decisions (Work in Progress)

Core layers:
* `app.py` – Flask app factory/initialization & DB setup.
* `routes.py` – HTTP routes (will be split into blueprints in future refactor).
* `calendar_api.py` – Google Calendar meal fetching (returns normalized mapping).
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
* Add service layer for meal/chores logic.
* Expand tests for route responses (index, chores, meal-plans).
* Add type checking gate in CI.

# familyhub-mealboard

## Google Calendar dinner plans

The application can fetch upcoming dinner plans from a shared Google Calendar.
Events within a 7‑day window around today are returned by the `/api/meals`
endpoint as a dictionary keyed by ISO date strings.

### Setup
1. **Create a Google service account** and download its JSON key.
2. **Share the calendar** with the service account's e‑mail (read access is
   enough).
3. Set the following environment variables:

   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to the downloaded JSON key file.
   - `FAMILYHUB_CALENDAR_ID`: ID of the shared calendar.
   - Optional `FAMILYHUB_TZ`: Timezone name (defaults to `America/Chicago`).

With these variables configured, the `/api/meals` route will return the
meal plan as JSON and can be consumed by the frontend.

## Chores Source of Truth

Chores are currently sourced exclusively from Google Tasks via `services/chores_service.py`.

Environment flag `CHORES_BACKEND` (default `google`) is reserved for a future
DB-backed implementation. Routes and templates must not call `tasks_api` directly;
they should use the service to ensure consistent normalization and persistence.