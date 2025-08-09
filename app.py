"""Flask application initialization.

Separated concerns:
* Configuration (config.Settings)
* Database initialization
* Logging bootstrap (single place)
"""

from __future__ import annotations

import logging
from logging import Logger
from typing import Any

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from db import db
from config import get_settings


def _bootstrap_logging() -> Logger:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    return logging.getLogger("startup")


settings = get_settings()
log = _bootstrap_logging()

app = Flask(__name__)
app.secret_key = settings.session_secret
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore
app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

db.init_app(app)

with app.app_context():  # pragma: no cover - startup side effects
    import models  # noqa: F401  # ensure models registered
    db.create_all()
    log.info("Database tables created")

if not settings:  # pragma: no cover safety check
    raise RuntimeError("Settings failed to load")

# Allow skipping routes when running maintenance scripts (seed/migrations)
import os as _os
if not _os.environ.get("SKIP_ROUTES"):
    import routes  # noqa: F401

if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=True)