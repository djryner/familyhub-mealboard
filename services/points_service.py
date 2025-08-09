from datetime import date, datetime, timedelta
from sqlalchemy import text


def _to_date(x):
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, str):
        return date.fromisoformat(x[:10])
    return None


def get_chore_points(conn, task_id: str, fallback: int = 1) -> int:
    row = conn.execute(text("SELECT points FROM chore_metadata WHERE task_id=:id"), {"id": task_id}).fetchone()
    return int(row[0]) if row else fallback


def set_chore_points(conn, task_id: str, points: int):
    conn.execute(text(
        """
        INSERT INTO chore_metadata(task_id, points) VALUES(:id,:p)
        ON CONFLICT(task_id) DO UPDATE SET points=excluded.points
        """
    ), {"id": task_id, "p": points})


def grant_points_for_completion(conn, *, user: str, task_id: str, points: int):
    conn.execute(text(
        """
        INSERT OR IGNORE INTO points_ledger(user_name, task_id, points, kind)
        VALUES(:u, :t, :p, 'earn')
        """
    ), {"u": user, "t": task_id, "p": points})


def balance(conn, user: str) -> int:
    row = conn.execute(text("SELECT COALESCE(SUM(points),0) FROM points_ledger WHERE user_name=:u"), {"u": user}).fetchone()
    return int(row[0] or 0)


def leaderboard_week(conn, start: date, end: date):
    return conn.execute(text(
        """
      SELECT user_name, COALESCE(SUM(points),0) AS pts
      FROM points_ledger
      WHERE occurred_at >= :s AND occurred_at < :e AND kind='earn'
      GROUP BY user_name
      ORDER BY pts DESC, user_name ASC
        """
    ), {"s": start.isoformat(), "e": (end + timedelta(days=1)).isoformat()}).fetchall()


def redeem(conn, *, user: str, reward_id: int):
    r = conn.execute(text("SELECT cost_points FROM rewards WHERE id=:id AND active=1"), {"id": reward_id}).fetchone()
    if not r:
        raise ValueError("reward not found")
    cost = int(r[0])
    if balance(conn, user) < cost:
        raise ValueError("insufficient points")
    conn.execute(text("INSERT INTO redemptions(user_name, reward_id, points) VALUES(:u,:rid,:p)"),
                 {"u": user, "rid": reward_id, "p": cost})
    conn.execute(text("INSERT INTO points_ledger(user_name, points, kind) VALUES(:u, :neg, 'redeem')"),
                 {"u": user, "neg": -cost})
