"""
models.py — Python dataclasses mirroring the DB schema.

These are used internally (DB row → Python object) and are separate from
the Pydantic schemas used for request/response serialisation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class URLRecord:
    id: int
    short_code: str
    long_url: str
    created_at: str          # ISO 8601 UTC string
    expires_at: Optional[str]  # ISO 8601 UTC string, or None
    click_count: int
    is_active: int            # 1 = active, 0 = soft-deleted
