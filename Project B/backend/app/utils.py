"""
utils.py — Shared utility functions.

  - Short code generation (random base62, CSPRNG-backed)
  - Expiry timestamp calculation
  - DB-row-to-dataclass helper
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
import sqlite3

from app.models import URLRecord

# ---------------------------------------------------------------------------
# Short code constants
# ---------------------------------------------------------------------------

_ALPHABET = string.ascii_letters + string.digits   # A-Za-z0-9 (62 chars)
_CODE_LENGTH = 7                                   # 62^7 ≈ 3.5 trillion codes
_MAX_RETRIES = 5                                   # collision guard (near-impossible at this scale)


def generate_short_code() -> str:
    """Return a cryptographically-random 7-character base62 string."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(_CODE_LENGTH))


# ---------------------------------------------------------------------------
# Timestamp utilities
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def expiry_iso(days: Optional[int]) -> Optional[str]:
    """
    Compute an expiry timestamp from `days` from now.
    Returns None if days is 0 or None (meaning never-expire).
    """
    if not days:
        return None
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def is_expired(expires_at: Optional[str]) -> bool:
    """Return True if expires_at is set and is in the past."""
    if expires_at is None:
        return False
    expiry = datetime.fromisoformat(expires_at)
    # Ensure offset-aware comparison
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > expiry


# ---------------------------------------------------------------------------
# DB row helper
# ---------------------------------------------------------------------------

def row_to_url_record(row: sqlite3.Row) -> URLRecord:
    """Convert a sqlite3.Row to a URLRecord dataclass."""
    return URLRecord(
        id=row["id"],
        short_code=row["short_code"],
        long_url=row["long_url"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        click_count=row["click_count"],
        is_active=row["is_active"],
    )
