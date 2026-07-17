"""
auth.py — API key dependency for protected endpoints.

Checks the X-API-Key request header against the API_KEY environment variable.
Uses secrets.compare_digest to avoid timing-based side-channel attacks.
"""

import os
import secrets

from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

_API_KEY: str = os.getenv("API_KEY", "")


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    """
    FastAPI dependency injected into protected routes.

    Raises 401 if:
    - API_KEY env var is not set (misconfigured server)
    - Header is missing (FastAPI raises 422 automatically for missing required headers)
    - Header value doesn't match the configured key (constant-time compare)
    """
    if not _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API_KEY is not set",
        )
    if not secrets.compare_digest(x_api_key.encode(), _API_KEY.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
