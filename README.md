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


## Chores Source of Truth & Recurring Chore Behavior

Chores are sourced from Google Tasks via `services/chores_service.py`.

### Recurring Chores: How They Work

- When you create a recurring chore, the recurrence rule (RRULE) and the initial due date are sent to Google Tasks and also stored locally in the `chore_metadata` table (`recurrence`, `last_due_iso`).
- When you mark a recurring chore as complete, only the current occurrence is completed (using Google Tasks API `tasks.patch`). The series is never deleted or stripped of recurrence.
- After completion, the backend immediately refetches the task to get the new next due date (if any) and updates `last_due_iso` in the local DB.
- The UI will refresh and show the next occurrence on the appropriate day. If the next due is not today, the task will disappear from today's list (this is correct).
- Points are awarded only once per (task_id, due_iso) occurrence, ensuring you can't double-claim for the same instance of a recurring task.

#### Example RRULEs

- Daily: `["RRULE:FREQ=DAILY"]`
- School Days: `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]`
- Weekends: `["RRULE:FREQ=WEEKLY;BYDAY=SA,SU"]`
- Once per week (e.g., Friday): `["RRULE:FREQ=WEEKLY;BYDAY=FR"]`
- Once: no recurrence field

#### Local DB fields

- `chore_metadata.recurrence`: RRULE string (if recurring)
- `chore_metadata.last_due_iso`: Last seen due date (ISO, YYYY-MM-DD)

#### Completion Flow

1. UI sends the current due date (`due_iso`) with the complete request.
2. Backend marks only the current occurrence as complete in Google Tasks.
3. Points are awarded only if not already granted for (task_id, due_iso).
4. The next occurrence (if any) is shown on the correct day after refresh.

**This ensures recurring chores are robust, never disappear from the series, and points are occurrence-safe.**