from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import text
from app import db
from services import points_service as ps

bp = Blueprint('rewards', __name__, template_folder='../templates/rewards')


@bp.get('/')
def rewards_home():
    with db.engine.begin() as conn:
        users = ps.list_users(conn)
        rewards = ps.list_rewards(conn, active_only=True)
        balances = {u.name: ps.user_balance(conn, u.name) for u in users}
    return render_template('rewards/index.html', users=users, rewards=rewards, balances=balances)


@bp.post('/redeem')
def redeem_reward():
    data = request.get_json() or request.form
    user = data['user']
    reward_id = int(data['reward_id'])
    try:
        with db.engine.begin() as conn:
            ps.redeem(conn, user=user, reward_id=reward_id)
        return ('', 204)
    except Exception as e:  # pragma: no cover - simple error pass-through
        return jsonify({'error': str(e)}), 400
