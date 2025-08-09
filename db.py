"""Database initialization for the Flask application.

This module sets up the SQLAlchemy instance and a declarative base for models.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# Global SQLAlchemy instance
db = SQLAlchemy(model_class=Base)
