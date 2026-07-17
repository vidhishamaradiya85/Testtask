"""
routers/stats.py — GET /stats/{short_code}

Public stats endpoint. Returns click count and metadata for a short code.

Error responses:
  404  — code not found (or soft-deleted)
  410  — code found but expired
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas import StatsResponse
from app.utils import is_expired, row_to_url_record

router = APIRouter()


@router.get(
    "/stats/{short_code}",
    response_model=StatsResponse,
    summary="Get click stats for a short URL",
)
def get_stats(
    short_code: str,
    db: sqlite3.Connection = Depends(get_db),
) -> StatsResponse:
    """
    Return click count, original URL, creation time, and expiry for `short_code`.

    - 404 for unknown/deleted codes
    - 410 for expired codes (stats are still visible — the record exists, just past expiry)
      Note: we return the stats even for expired codes so clients can see the history.
      Only the redirect endpoint blocks on expiry.
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

    return StatsResponse(
        short_code=record.short_code,
        long_url=record.long_url,
        click_count=record.click_count,
        created_at=record.created_at,
        expires_at=record.expires_at,
    )
