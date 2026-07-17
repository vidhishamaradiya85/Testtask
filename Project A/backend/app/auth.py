import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    expected_api_key = os.getenv("API_KEY")
    if not x_api_key or x_api_key != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return x_api_key
