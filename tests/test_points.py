from datetime import date, timedelta
from sqlalchemy import create_engine, text
from services import points_service as ps
from pathlib import Path


def setup_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    sql = Path('migrations/001_points.sql').read_text()
    with engine.begin() as conn:
        conn.connection.executescript(sql)
    return engine


def test_idempotent_completion_no_double_earn():
    engine = setup_engine()
    with engine.begin() as conn:
        ps.grant_points_for_completion(conn, user='alice', task_id='t1', points=5)
        ps.grant_points_for_completion(conn, user='alice', task_id='t1', points=5)
        rows = conn.execute(text("SELECT COUNT(*) FROM points_ledger WHERE user_name='alice'")).fetchone()
        assert rows[0] == 1


def test_leaderboard_week_filters_dates():
    engine = setup_engine()
    today = date(2024, 1, 4)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO points_ledger(user_name, points, kind, occurred_at) VALUES('a',5,'earn', :d)"), {"d": start.isoformat()})
        conn.execute(text("INSERT INTO points_ledger(user_name, points, kind, occurred_at) VALUES('b',3,'earn', :d)"), {"d": (end + timedelta(days=1)).isoformat()})
        rows = ps.leaderboard_week(conn, start, end)
    assert [r.user_name for r in rows] == ['a']


def test_redeem_deducts_points_and_records_redemption():
    engine = setup_engine()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO rewards(title, cost_points) VALUES('Toy',5)"))
        ps.grant_points_for_completion(conn, user='bob', task_id='t1', points=10)
        ps.redeem(conn, user='bob', reward_id=1)
        bal = ps.balance(conn, 'bob')
        assert bal == 5
        red = conn.execute(text('SELECT user_name, reward_id, points FROM redemptions')).fetchone()
        assert red.user_name == 'bob' and red.reward_id == 1 and red.points == 5


def test_set_chore_points_upsert():
    engine = setup_engine()
    with engine.begin() as conn:
        ps.set_chore_points(conn, 'task1', 3)
        assert ps.get_chore_points(conn, 'task1') == 3
        ps.set_chore_points(conn, 'task1', 7)
        assert ps.get_chore_points(conn, 'task1') == 7
        count = conn.execute(text('SELECT COUNT(*) FROM chore_metadata')).fetchone()[0]
        assert count == 1
