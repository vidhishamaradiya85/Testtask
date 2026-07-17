-- URL Shortener Schema
-- Run this once to initialize the database, or let the app auto-run it via database.py

CREATE TABLE IF NOT EXISTS urls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code  TEXT    NOT NULL UNIQUE,
    long_url    TEXT    NOT NULL,
    created_at  TEXT    NOT NULL,           -- ISO 8601 UTC
    expires_at  TEXT,                       -- nullable; ISO 8601 UTC
    click_count INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1  -- 1 = active, 0 = soft-deleted
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_urls_short_code ON urls(short_code);
CREATE        INDEX IF NOT EXISTS idx_urls_long_url   ON urls(long_url);
