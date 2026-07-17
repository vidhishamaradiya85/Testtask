"""
conftest.py — Shared pytest fixtures for the URL shortener backend tests.

Isolation strategy
------------------
Each test gets a FRESH, independent SQLite in-memory database so that:
  - No test data ever touches the real urls.db file.
  - Tests are order-independent and can run in parallel safely.

How it works
------------
FastAPI uses a `get_db` dependency to inject the SQLite connection into every
route handler.  We override that dependency in `app.dependency_overrides` to
return a pre-initialised in-memory connection instead.  The override is scoped
to the duration of the test (function scope), so every test starts clean.

The `API_KEY` module-level constant in `auth.py` is read once at import time
from the environment.  We monkey-patch `app.auth._API_KEY` directly so auth
works without requiring a real .env file on the test runner.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.auth as auth_module
from app.database import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Constants used by tests
# ---------------------------------------------------------------------------

TEST_API_KEY = "test-api-key-fixture"
SCHEMA_PATH = Path(__file__).parent.parent / "schema.sql"
VALID_URL = "https://example.com/some/path"
VALID_URL_2 = "https://openai.com/blog/gpt-4"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_db() -> sqlite3.Connection:
    """
    Create and initialise a fresh in-memory SQLite database.

    We use `check_same_thread=False` so that Starlette's TestClient (which
    may dispatch requests on a worker thread) can reuse the same connection
    object.  This is safe here because pytest tests are single-threaded.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    return conn


def _insert_expired_url(conn: sqlite3.Connection, short_code: str, long_url: str) -> None:
    """
    Directly insert a row whose expires_at is 1 day in the PAST so we can
    test the 410 Gone response without waiting for real time to pass.
    """
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO urls (short_code, long_url, created_at, expires_at, click_count, is_active)
        VALUES (?, ?, ?, ?, 0, 1)
        """,
        (short_code, long_url, now, past),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_conn():
    """Yield a fresh in-memory SQLite connection; close it after the test."""
    conn = _make_test_db()
    yield conn
    conn.close()


@pytest.fixture()
def client(db_conn, monkeypatch):
    """
    Yield a FastAPI TestClient wired to an isolated in-memory database.

    Steps:
    1. Monkeypatch auth._API_KEY so tests have a known, stable API key.
    2. Override the get_db FastAPI dependency to return our test connection.
    3. Build a TestClient (which triggers lifespan startup/shutdown).
       We pass raise_server_exceptions=True (default) so test assertions can
       catch errors rather than swallowing them.
    4. Clear the dependency override after the test to avoid contaminating
       other test modules.
    """
    # Patch the module-level constant so verify_api_key uses the test key
    monkeypatch.setattr(auth_module, "_API_KEY", TEST_API_KEY)

    # Wire the FastAPI dependency to our test DB
    app.dependency_overrides[get_db] = lambda: db_conn

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    # Always clean up overrides after each test
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def auth_headers():
    """Return the X-API-Key header dict for authenticated requests."""
    return {"X-API-Key": TEST_API_KEY}


@pytest.fixture()
def created_url(client, auth_headers):
    """
    Create a short URL and return the full response JSON.

    Used as a building block by tests that need an existing short code
    (redirect, stats, duplicate, etc.) without repeating the creation call.
    """
    resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
    assert resp.status_code == 200, f"Fixture setup failed: {resp.text}"
    return resp.json()
