import types
from datetime import date, datetime
from services.chores_service import fetch_chores, complete_chore, ChoreDTO
import services.chores_service as cs

class DummyTaskService:
    def __init__(self, tasks):
        self._tasks = {t['id']: t for t in tasks}
        self._updated = {}
    def tasks(self):
        svc = self
        class TasksOps:
            def __init__(self, outer):
                self.outer = outer
            def get(self, tasklist, task):
                return types.SimpleNamespace(execute=lambda: self.outer._tasks[task])
            def update(self, tasklist, task, body):
                self.outer._tasks[task] = body
                self.outer._updated[task] = body
                return types.SimpleNamespace(execute=lambda: body)
        return TasksOps(self)


def monkey_google(monkeypatch, tasks):
    dummy = DummyTaskService(tasks)
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', 'dummy.json')
    monkeypatch.setenv('FAMILYHUB_CALENDAR_ID', 'dummy-cal')
    monkeypatch.setenv('CHORES_BACKEND', 'google')

    def fake_build():
        return dummy
    def fake_list_id(svc, title):
        return 'list123'
    def fake_get_tasks(svc, list_id):
        return tasks
    monkeypatch.setattr(cs, 'build_google_service', fake_build)
    monkeypatch.setattr(cs, 'get_or_create_task_list', fake_list_id)
    monkeypatch.setattr(cs, 'get_google_tasks', fake_get_tasks)

    return dummy


def test_fetch_chores_normalizes_dates(monkeypatch):
    tasks = [
        {'id': '1', 'title': 'Task A', 'assigned_to': 'Alex', 'due_date': date.today(), 'priority': 'high', 'completed': False},
        {'id': '2', 'title': 'Task B', 'assigned_to': None, 'due_date': None, 'priority': 'low', 'completed': True},
    ]
    monkey_google(monkeypatch, tasks)
    chores = fetch_chores()
    assert len(chores) == 2
    assert isinstance(chores[0].due_date, (date, type(None)))


def test_complete_chore_persists(monkeypatch):
    tasks = [
        {'id': '10', 'title': 'Wash Dishes', 'assigned_to': None, 'due_date': None, 'priority': 'low', 'completed': False},
    ]
    dummy = monkey_google(monkeypatch, tasks)
    complete_chore('10')
    assert dummy._tasks['10']['status'] == 'completed'
