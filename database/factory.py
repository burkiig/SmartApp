"""
Database adapter factory.

Two functions are provided:

get_db()
    Request-scoped adapter using flask.g.
    Use this inside route handlers and middleware.

get_scheduler_db()
    Creates a fresh adapter instance without flask.g.
    Use this inside APScheduler jobs and push_service (outside request context).
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import DatabaseAdapter


def _create_adapter() -> "DatabaseAdapter":
    """Instantiate the adapter selected by DB_DRIVER environment variable."""
    driver = os.getenv("DB_DRIVER", "json").lower()

    if driver == "sqlite":
        from .sqlite_adapter import SQLiteAdapter
        return SQLiteAdapter(db_path=os.getenv("SQLITE_PATH", "smart_attendance.db"))

    if driver == "mongodb":
        from .mongodb_adapter import MongoDBAdapter
        return MongoDBAdapter(
            connection_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
            database_name=os.getenv("MONGODB_DATABASE", "smart_attendance"),
        )

    # Default: JSON
    from .json_adapter import JSONAdapter
    return JSONAdapter(base_dir=os.getenv("JSON_BASE_DIR", "static"))


def get_db() -> "DatabaseAdapter":
    """
    Return the request-scoped database adapter (via flask.g).
    Call this inside route handlers and service functions invoked from routes.
    """
    from flask import g
    if "db" not in g:
        g.db = _create_adapter()
    return g.db


def get_scheduler_db() -> "DatabaseAdapter":
    """
    Return a fresh database adapter instance.
    Use inside APScheduler jobs and any code that runs outside a request context.
    """
    return _create_adapter()


# Backward-compatible alias used by legacy code in app.py
get_database_adapter = get_scheduler_db
