# API.md — URL Shortener API Reference

Base URL (local dev): `http://localhost:8000`

Auth: endpoints marked **Auth: required** expect header `X-API-Key: <your-key>`. Public endpoints need no header.

---

## POST /shorten

Create a short code for a long URL. Returns an existing code if the URL was already shortened (no duplicates).

**Auth:** required (`X-API-Key`)

**Request body**
```json
{
  "url": "https://example.com/some/very/long/path"
}
```

**curl**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com/some/very/long/path"}'
```

**Success response — 200/201**
```json
{
  "short_code": "aZ3kLp",
  "short_url": "http://localhost:8000/aZ3kLp",
  "original_url": "https://example.com/some/very/long/path"
}
```

**Status codes**

| Code | Meaning |
|------|---------|
| 200 / 201 | Created (or matched an existing short code for a duplicate URL) |
| 401 | Missing or invalid `X-API-Key` |
| 422 | Malformed / invalid URL in request body |

**Edge cases**

- **Duplicate URL:** submitting a URL that was already shortened returns the *existing* `short_code` instead of creating a new one.
- **Invalid URL:** e.g. `{"url": "not-a-url"}` → `422 Unprocessable Entity`
  ```json
  {
    "detail": [
      {
        "loc": ["body", "url"],
        "msg": "invalid or missing URL scheme",
        "type": "value_error.url"
      }
    ]
  }
  ```

---

## GET /{short_code}

Redirects to the original long URL and increments the click counter.

**Auth:** none (public)

**curl**
```bash
curl -i http://localhost:8000/aZ3kLp
```

**Status codes**

| Code | Meaning |
|------|---------|
| 301 / 302 | Redirect issued to the original URL (click counter incremented) |
| 404 | Short code does not exist |
| 410 | Short code exists but has expired |

**Edge cases**

- **Missing/unknown code:** `GET /doesNotExist` → `404 Not Found`
  ```json
  { "detail": "Short code not found" }
  ```
- **Expired code:** `GET /oldCode` → `410 Gone`
  ```json
  { "detail": "Short code has expired" }
  ```

---

## GET /stats/{short_code}

Returns the current click count for a short code.

**Auth:** none (public)

**curl**
```bash
curl http://localhost:8000/stats/aZ3kLp
```

**Success response — 200**
```json
{
  "short_code": "aZ3kLp",
  "original_url": "https://example.com/some/very/long/path",
  "click_count": 42
}
```

**Status codes**

| Code | Meaning |
|------|---------|
| 200 | Stats returned |
| 404 | Short code does not exist |

---

## Status code summary

| Code | Used by | Meaning |
|------|---------|---------|
| 200/201 | `/shorten`, `/stats/{code}` | Success |
| 301/302 | `/{code}` | Redirect to original URL |
| 401 | `/shorten` | Missing/invalid API key |
| 404 | `/{code}`, `/stats/{code}` | Short code not found |
| 410 | `/{code}` | Short code expired |
| 422 | `/shorten` | Invalid request body / malformed URL |
