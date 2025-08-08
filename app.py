import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from db import db  # <-- import db from db.py
from sqlalchemy.orm import DeclarativeBase  # <-- Add this import
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "devcontainer-secret-key")  # <-- Set a default
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///familyhub.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")

import routes  # <-- Add this line to register your routes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)