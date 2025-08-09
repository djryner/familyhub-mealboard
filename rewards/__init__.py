from flask import Blueprint

bp = Blueprint('rewards', __name__, template_folder='../templates/rewards')

from . import routes  # noqa: E402,F401
