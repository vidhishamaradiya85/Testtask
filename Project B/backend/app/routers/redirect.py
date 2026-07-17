"""
routers/redirect.py — GET /{short_code}

Public redirect endpoint. Resolves a short code to its long URL,
issues a 302 redirect, and atomically increments the click counter.

Error responses:
  404  — code not found (or soft-deleted)
  410  — code found but expired
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.database import get_db
from app.utils import is_expired, row_to_url_record

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to the original URL",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
def redirect_to_url(
    short_code: str,
    db: sqlite3.Connection = Depends(get_db),
) -> RedirectResponse:
    """
    Resolve `short_code` and redirect (302) to its long URL.
    Increments the click counter on every valid, non-expired hit.

    - 404 for unknown/deleted codes
    - 410 for expired codes (found but past expiry)
    """
    row = db.execute(
        "SELECT * FROM urls WHERE short_code = ? AND is_active = 1",
        (short_code,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found",
        )

    record = row_to_url_record(row)

    if is_expired(record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Short code '{short_code}' has expired",
        )

    # Atomically increment the click counter
    db.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
        (short_code,),
    )
    db.commit()

    return RedirectResponse(url=record.long_url, status_code=status.HTTP_302_FOUND)
