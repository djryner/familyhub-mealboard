"""Legacy routes module.

Importing this module registers the kiosk blueprint for test contexts
and exposes common service helpers for monkeypatching.
"""

from services.meals_service import fetch_meals  # noqa: F401
from services.chores_service import fetch_chores  # noqa: F401

from app import app
from kiosk import bp as kiosk_bp

app.register_blueprint(kiosk_bp, name="")
