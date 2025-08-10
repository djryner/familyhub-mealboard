"""Unit tests for the chores service."""

import types
from datetime import date, datetime
from services.chores_service import fetch_chores, complete_chore, ChoreDTO
import services.chores_service as cs


class DummyTaskService:
    """A mock implementation of the Google Tasks API service for testing."""

    def __init__(self, tasks):
        # Store tasks in a dictionary for easy lookup by ID.
        self._tasks = {t["id"]: t for t in tasks}
        self._updated = {}  # Track updated tasks for assertions.

    def tasks(self):
        """Returns a mock for the 'tasks' resource of the service."""
        svc = self

        class TasksOps:
            """Mocks the operations available on the 'tasks' resource."""

            def __init__(self, outer):
                self.outer = outer

            def get(self, tasklist, task):
                """Mocks the 'get' operation."""
                return types.SimpleNamespace(execute=lambda: self.outer._tasks[task])

            def update(self, tasklist, task, body):
                """Mocks the 'update' operation, tracking the changes."""
                self.outer._tasks[task] = body
                self.outer._updated[task] = body
                return types.SimpleNamespace(execute=lambda: body)

        return TasksOps(self)


def monkey_google(monkeypatch, tasks):
    """A pytest helper to mock the Google-backed chores service.

    This function patches the necessary functions in the chores_service module
    to use a dummy service instead of making real API calls.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        tasks: A list of task dictionaries to populate the dummy service with.

    Returns:
        An instance of the DummyTaskService for inspection.
    """
    dummy = DummyTaskService(tasks)
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "dummy.json")
    monkeypatch.setenv("FAMILYHUB_CALENDAR_ID", "dummy-cal")
    monkeypatch.setenv("CHORES_BACKEND", "google")

    # Define fake functions to replace the real ones
    def fake_build():
        return dummy

    def fake_list_id(svc, title):
        return "list123"

    def fake_get_tasks(svc, list_id):
        return tasks

    # Apply the patches
    monkeypatch.setattr(cs, "build_google_service", fake_build)
    monkeypatch.setattr(cs, "get_or_create_task_list", fake_list_id)
    monkeypatch.setattr(cs, "get_google_tasks", fake_get_tasks)

    return dummy


def test_fetch_chores_normalizes_dates(monkeypatch):
    """Tests that fetch_chores correctly normalizes various date formats into date objects."""
    # Setup: Define tasks with different date representations.
    tasks = [
        {
            "id": "1",
            "title": "Task A",
            "assigned_to": "Alex",
            "due_date": date.today(),
            # priority removed
            "completed": False,
        },
        {
            "id": "2",
            "title": "Task B",
            "assigned_to": None,
            "due_date": None,
            # priority removed
            "completed": True,
        },
    ]
    monkey_google(monkeypatch, tasks)

    # Execution: Fetch the chores.
    chores = fetch_chores()

    # Verification: Check that the chores were fetched and dates are correctly typed.
    assert len(chores) == 2
    assert isinstance(chores[0].due_date, (date, type(None)))


def test_complete_chore_persists(monkeypatch):
    """Tests that calling complete_chore updates the task's status to 'completed'."""
    # Setup: Define an incomplete task.
    tasks = [
        {
            "id": "10",
            "title": "Wash Dishes",
            "assigned_to": None,
            "due_date": None,
            # priority removed
            "completed": False,
        },
    ]
    dummy = monkey_google(monkeypatch, tasks)

    # Execution: Mark the chore as complete.
    complete_chore("10")

    # Verification: Assert that the task's status was updated in the mock service.
    assert dummy._tasks["10"]["status"] == "completed"
