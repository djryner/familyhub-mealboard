# app.py
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from db import db

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "devcontainer-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///familyhub.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

db.init_app(app)

with app.app_context():
    import models  # ensure models are registered
    db.create_all()
    logging.info("Database tables created")



# ✅ Allow skipping routes when running maintenance scripts (seed/migrations)
if not os.environ.get("SKIP_ROUTES"):
    import routes



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)