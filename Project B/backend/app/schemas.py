"""
schemas.py — Pydantic models for request validation and response serialisation.

Kept separate from DB models (models.py) so the API contract is independently
evolvable from the storage layer.
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ShortenRequest(BaseModel):
    url: str
    expires_in_days: Optional[int] = None  # None → use DEFAULT_EXPIRY_DAYS from env

    @field_validator("url")
    @classmethod
    def must_be_http_or_https(cls, v: str) -> str:
        """
        Validate URL structure and scheme.
        - Must parse as a valid URL (pydantic HttpUrl handles this).
        - Scheme must be http or https (no javascript:, data:, ftp:, etc.)
        - Max length: 2048 chars (matches common browser limits).
        """
        v = v.strip()
        if len(v) > 2048:
            raise ValueError("URL exceeds maximum allowed length of 2048 characters")
        from urllib.parse import urlparse
        try:
            parsed = urlparse(v)
        except Exception:
            raise ValueError("Malformed URL")
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        if not parsed.netloc:
            raise ValueError("URL is missing a host/domain")
        return v


# ---------------------------------------------------------------------------
# Response bodies
# ---------------------------------------------------------------------------

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
    created_at: str
    expires_at: Optional[str]
    is_duplicate: bool  # True when returning an existing record rather than a new one


class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    created_at: str
    expires_at: Optional[str]


class ErrorResponse(BaseModel):
    detail: str
