"""
routers/shorten.py — POST /shorten

Creates a new short URL (or returns the existing one for duplicate long URLs).
Protected by API key via the verify_api_key dependency.
"""

import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv

from app.auth import verify_api_key
from app.database import get_db
from app.schemas import ShortenRequest, ShortenResponse
from app.utils import (
    generate_short_code,
    utc_now_iso,
    expiry_iso,
    row_to_url_record,
    _MAX_RETRIES,
)

load_dotenv()

router = APIRouter()

_BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
_DEFAULT_EXPIRY_DAYS: int = int(os.getenv("DEFAULT_EXPIRY_DAYS", "30"))


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or retrieve a short URL",
    dependencies=[Depends(verify_api_key)],
)
def shorten_url(
    body: ShortenRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> ShortenResponse:
    """
    Create a short code for the given URL.

    - If the exact same long URL already has an active, non-expired short code,
      that existing record is returned (dedup behaviour) with `is_duplicate=true`.
    - Otherwise a new 7-char base62 code is generated and stored.
    - The optional `expires_in_days` field overrides the server default.
      Pass 0 to create a never-expiring link.
    """
    long_url = body.url

    # ------------------------------------------------------------------
    # 1. Dedup check — look for an active, non-expired record for this URL
    # ------------------------------------------------------------------
    existing_row = db.execute(
        """
        SELECT * FROM urls
        WHERE long_url = ? AND is_active = 1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (long_url,),
    ).fetchone()

    if existing_row:
        record = row_to_url_record(existing_row)
        # Only reuse if it's not expired
        from app.utils import is_expired
        if not is_expired(record.expires_at):
            return ShortenResponse(
                short_code=record.short_code,
                short_url=f"{_BASE_URL}/{record.short_code}",
                long_url=record.long_url,
                created_at=record.created_at,
                expires_at=record.expires_at,
                is_duplicate=True,
            )
        # Expired record found — fall through to create a fresh one

    # ------------------------------------------------------------------
    # 2. Determine expiry
    # ------------------------------------------------------------------
    expiry_days: Optional[int] = body.expires_in_days
    if expiry_days is None:
        expiry_days = _DEFAULT_EXPIRY_DAYS  # server default (30 days or env override)

    expires_at_str = expiry_iso(expiry_days)
    created_at_str = utc_now_iso()

    # ------------------------------------------------------------------
    # 3. Generate unique short code and insert
    # ------------------------------------------------------------------
    for attempt in range(_MAX_RETRIES):
        code = generate_short_code()
        try:
            db.execute(
                """
                INSERT INTO urls (short_code, long_url, created_at, expires_at, click_count, is_active)
                VALUES (?, ?, ?, ?, 0, 1)
                """,
                (code, long_url, created_at_str, expires_at_str),
            )
            db.commit()
            break
        except sqlite3.IntegrityError:
            # UNIQUE constraint violation on short_code — retry
            if attempt == _MAX_RETRIES - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate a unique short code. Please retry.",
                )
            continue

    return ShortenResponse(
        short_code=code,
        short_url=f"{_BASE_URL}/{code}",
        long_url=long_url,
        created_at=created_at_str,
        expires_at=expires_at_str,
        is_duplicate=False,
    )
