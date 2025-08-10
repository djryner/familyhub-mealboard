-- Chore metadata: one row per recurring chore definition
CREATE TABLE IF NOT EXISTS chore_metadata (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    assigned_to TEXT,
    recurrence TEXT,
    points INTEGER DEFAULT 1
);

-- Chore occurrences: one row per due date/instance
CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    due_date DATE NOT NULL,
    status TEXT CHECK(status IN ('pending','completed','ignored')) DEFAULT 'pending',
    completed_at TIMESTAMP,
    ignored_at TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES chore_metadata(task_id)
);
