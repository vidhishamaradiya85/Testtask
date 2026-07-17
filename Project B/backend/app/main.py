"""
main.py — FastAPI application factory and startup logic.

Router registration order matters here:
  - /stats/{short_code} must be registered BEFORE /{short_code}
    so FastAPI matches /stats/abc as the stats route, not the redirect route.
  - /shorten is registered first (it's under a distinct path prefix).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import shorten, redirect, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run schema initialisation on startup; nothing special on shutdown."""
    init_db()
    yield


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="URL Shortener API",
    description=(
        "A minimal URL shortening service.\n\n"
        "**Auth**: `POST /shorten` requires an `X-API-Key` header.\n"
        "All other endpoints are public."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Alternatively ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router registration
# ORDER MATTERS — must register exact/prefixed paths before wildcard /{short_code}:
#   1. /shorten   (POST — distinct path, no conflict)
#   2. /stats/... (GET — must come before /{short_code} catch-all)
#   3. /health    (GET — registered as a plain route before the wildcard)
#   4. /{short_code}  (GET — wildcard catch-all, must be last)
# ---------------------------------------------------------------------------
app.include_router(shorten.router, tags=["shorten"])
app.include_router(stats.router, tags=["stats"])


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """
    Reformat Pydantic validation errors into a consistent { detail: str } shape
    for URL validation failures so the client gets a readable error message.
    """
    from fastapi.exceptions import RequestValidationError
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
        # Flatten multiple validation errors into a single readable string
        messages = "; ".join(
            e.get("msg", "Validation error") for e in errors
        )
        return JSONResponse(
            status_code=422,
            content={"detail": messages},
        )
    return JSONResponse(status_code=422, content={"detail": "Unprocessable Entity"})


# ---------------------------------------------------------------------------
# Health check — registered BEFORE the /{short_code} wildcard router
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"], summary="Health check")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Redirect router — MUST be last (wildcard /{short_code} catches all GET)
# ---------------------------------------------------------------------------
app.include_router(redirect.router, tags=["redirect"])
