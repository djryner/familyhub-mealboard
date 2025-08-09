-- Per‑chore metadata (points, optional assignment/priority)
CREATE TABLE IF NOT EXISTS chore_metadata (
  task_id      TEXT PRIMARY KEY,
  assigned_to  TEXT,
  priority     TEXT,
  points       INTEGER NOT NULL DEFAULT 1
);

-- Immutable points ledger
CREATE TABLE IF NOT EXISTS points_ledger (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name    TEXT NOT NULL,
  task_id      TEXT,
  points       INTEGER NOT NULL,
  kind         TEXT CHECK(kind IN ('earn','redeem','adjust')) NOT NULL,
  occurred_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_name, task_id, kind)
);

-- Rewards catalog
CREATE TABLE IF NOT EXISTS rewards (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  cost_points  INTEGER NOT NULL,
  active       INTEGER NOT NULL DEFAULT 1
);

-- Redemptions audit
CREATE TABLE IF NOT EXISTS redemptions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name    TEXT NOT NULL,
  reward_id    INTEGER NOT NULL,
  points       INTEGER NOT NULL,
  status       TEXT CHECK(status IN ('pending','approved','denied','fulfilled')) NOT NULL DEFAULT 'pending',
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(reward_id) REFERENCES rewards(id)
);
