CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  color TEXT,
  avatar TEXT
);

CREATE TABLE IF NOT EXISTS rewards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  cost_points INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  emoji TEXT
);

CREATE TABLE IF NOT EXISTS points_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name TEXT NOT NULL,
  task_id TEXT,
  points INTEGER NOT NULL,
  kind TEXT CHECK(kind IN ('earn','redeem','adjust')) NOT NULL,
  occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_ledger_once
ON points_ledger(user_name, task_id, kind)
WHERE task_id IS NOT NULL AND kind='earn';
