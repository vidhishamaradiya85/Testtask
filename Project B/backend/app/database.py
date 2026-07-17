"""
database.py — SQLite connection management and schema initialisation.

Uses a thread-local connection strategy so each request thread gets its own
sqlite3.Connection (sqlite3 connections are not thread-safe by default).
The schema is applied once at startup via the lifespan hook in main.py.
"""

import os
import sqlite3
import threading
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH: str = os.getenv("DATABASE_PATH", "urls.db")

_local = threading.local()
_SCHEMA_SQL = Path(__file__).parent.parent / "schema.sql"


def _get_connection() -> sqlite3.Connection:
    """Return a thread-local sqlite3 connection, creating one if needed."""
    conn = getattr(_local, "connection", None)
    if conn is None:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row          # rows accessible by column name
        conn.execute("PRAGMA journal_mode=WAL") # better concurrent read perf
        conn.execute("PRAGMA foreign_keys=ON")
        _local.connection = conn
    return conn


def get_db() -> sqlite3.Connection:
    """FastAPI dependency: yield a DB connection for the current request."""
    return _get_connection()


def init_db() -> None:
    """
    Create all tables/indexes from schema.sql if they don't already exist.
    Called once at application startup.
    """
    schema = _SCHEMA_SQL.read_text(encoding="utf-8")
    conn = _get_connection()
    conn.executescript(schema)
    conn.commit()
