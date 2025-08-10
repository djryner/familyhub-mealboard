def test_award_points_once_per_occurrence(monkeypatch):
    """Test that points are only awarded once per (task_id, due_iso) occurrence."""
    from services import points_service
    import sqlite3
    import os
    db_path = 'test_points_occurrence.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS points_ledger (user_name TEXT, task_id TEXT, points INT, kind TEXT, occurred_at TEXT, UNIQUE(user_name, task_id, kind, occurred_at))")
    user = 'alex'
    task_id = 't1'
    points = 5
    due_iso = '2025-08-09'
    # First award
    conn.execute("INSERT OR IGNORE INTO points_ledger(user_name, task_id, points, kind, occurred_at) VALUES (?, ?, ?, 'earn', ?)", (user, task_id, points, due_iso))
    # Try to award again for same occurrence
    conn.execute("INSERT OR IGNORE INTO points_ledger(user_name, task_id, points, kind, occurred_at) VALUES (?, ?, ?, 'earn', ?)", (user, task_id, points, due_iso))
    # Only one row should exist
    rows = conn.execute("SELECT * FROM points_ledger WHERE user_name=? AND task_id=? AND kind='earn' AND occurred_at=?", (user, task_id, due_iso)).fetchall()
    assert len(rows) == 1
    conn.close()
    os.remove(db_path)
