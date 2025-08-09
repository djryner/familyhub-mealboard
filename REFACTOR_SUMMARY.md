# Refactoring Recommendations

This document provides a summary of recommended refactoring opportunities identified during the code review. These suggestions aim to improve the long-term maintainability, robustness, and scalability of the application.

### 1. Consolidate Google API Logic

**Observation:**
The `familyhub-mealboard` sub-project contains its own `app/api/calendar.py`, which is a simplified and slightly outdated version of the `services/calendar_service.py` found in the main application. This creates code duplication and a maintenance overhead.

**Recommendation:**
Refactor the `familyhub-mealboard` application to use the more robust and feature-complete `services/calendar_service.py` from the main application. This would involve adjusting its imports and potentially passing a configuration context from the main app to the sub-app. This change would centralize the Google Calendar logic, making it easier to update and manage.

### 2. Standardize Error Handling in Services

**Observation:**
The `services.calendar_service.get_meals` function has a mixed return type. On success, it returns a `Dict[str, List[str]]`, but on failure, it returns a `Dict[str, str]` (e.g., `{"error": "message"}`). This requires callers to perform type checking to handle errors, which can be cumbersome and error-prone.

**Recommendation:**
Adopt a consistent error handling strategy. Two common approaches are:
- **Raise Exceptions:** Modify the service function to raise a custom exception (e.g., `CalendarServiceError`) on failure. The calling code in `routes.py` can then use a `try...except` block to gracefully handle the error (e.g., by flashing a message or showing an error page). This is a standard and robust practice in Python.
- **Tuple Return:** Always return a tuple, such as `(data, error)`. For example, a successful call would return `(meal_data, None)`, and a failure would return `(None, error_message)`.

### 3. Improve Metadata Storage for Chores

**Observation:**
The `services/chores_service.py` cleverly encodes metadata like `assigned_to` and `priority` into the `notes` field of a Google Task. While this works, it is a brittle solution. If the format of the notes string changes, the parsing logic will break. It also tightly couples the application's metadata to the specific implementation of the Google Tasks backend.

**Recommendation:**
Consider introducing a local database table to store chore metadata. This table could be linked to the Google Task by its unique ID. The structure could be as simple as:

```sql
CREATE TABLE chore_metadata (
    task_id VARCHAR PRIMARY KEY,
    assigned_to VARCHAR,
    priority VARCHAR,
    -- other metadata fields --
    FOREIGN KEY (task_id) REFERENCES google_tasks(id) -- conceptual
);
```

This would decouple the application's metadata from the backend, make the system more robust, and simplify the logic for creating and parsing chores.

### 4. Simplify Application Entry Point

**Observation:**
The project contains both an `app.py` for Flask app initialization and a `main.py` that imports and runs the app. This is a common pattern but is not strictly necessary for an application of this size.

**Recommendation:**
For simplicity, consider combining the startup logic from `main.py` into the `if __name__ == "__main__":` block of `app.py`. This would consolidate the application's entry point into a single file, making it easier to understand and run.

### 5. Centralize Configuration

**Observation:**
Both the main application and the `familyhub-mealboard` sub-project appear to draw from the same set of environment variables. This implicit dependency can make the sub-project harder to test and run in isolation.

**Recommendation:**
Implement a more explicit configuration pattern. The main application's `Settings` object could be passed down to the sub-project's initialization functions. This would make dependencies clear and improve the modularity of the codebase.
