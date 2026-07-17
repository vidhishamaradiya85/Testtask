# -*- coding: utf-8 -*-
"""
test_endpoints.py -- Integration test runner for the URL shortener backend.

Runs against a live server on http://127.0.0.1:8000.
Uses only stdlib (urllib) -- no requests/httpx required.
"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8001"
API_KEY = "supersecret-test-key"

DIVIDER = "=" * 58
PASS = "[PASS]"
FAIL = "[FAIL]"


def http(method: str, path: str, body=None, headers=None):
    """
    Make an HTTP request. Does NOT follow redirects.
    Returns (status_code, parsed_json_or_raw_string).
    """
    url = BASE + path
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)

    # Suppress redirect following so we can see the 302 directly
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    opener = urllib.request.build_opener(NoRedirect)

    try:
        resp = opener.open(req, timeout=10)
        status = resp.status
        raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  CONNECTION ERROR: {e}")
        sys.exit(1)

    try:
        return status, json.loads(raw)
    except Exception:
        return status, raw


def section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def show(label, status, body):
    print(f"  Request: {label}")
    print(f"  Status : {status}")
    if isinstance(body, (dict, list)):
        body_str = json.dumps(body, indent=4)
    else:
        body_str = str(body)
    # Trim long output
    if len(body_str) > 600:
        body_str = body_str[:600] + "..."
    print(f"  Body   :\n{body_str}")


def ok(msg):
    print(f"\n  {PASS} {msg}")


def fail(msg):
    print(f"\n  {FAIL} {msg}")
    sys.exit(1)


# ======================================================================
# TEST 1: Valid URL creation
# ======================================================================
section("TEST 1: Valid URL creation  POST /shorten")
s, b = http("POST", "/shorten",
            body={"url": "https://www.github.com/fastapi/fastapi"},
            headers={"X-API-Key": API_KEY})
show("POST /shorten", s, b)
if s != 200:
    fail(f"Expected 200, got {s}")
if "short_code" not in b:
    fail("Missing short_code in response")
if b.get("is_duplicate") != False:
    fail("Expected is_duplicate=false for new URL")
short_code = b["short_code"]
ok(f"Created short_code: {short_code}")

# ======================================================================
# TEST 2: Duplicate URL
# ======================================================================
section("TEST 2: Duplicate URL  POST /shorten (same URL again)")
s2, b2 = http("POST", "/shorten",
              body={"url": "https://www.github.com/fastapi/fastapi"},
              headers={"X-API-Key": API_KEY})
show("POST /shorten duplicate", s2, b2)
if s2 != 200:
    fail(f"Expected 200, got {s2}")
if b2.get("short_code") != short_code:
    fail(f"Expected same short_code {short_code!r}, got {b2.get('short_code')!r}")
if b2.get("is_duplicate") != True:
    fail("Expected is_duplicate=true")
ok(f"Deduped correctly, returned existing code: {short_code}")

# ======================================================================
# TEST 3: Invalid URL -- no scheme
# ======================================================================
section("TEST 3: Invalid URL -- no scheme  POST /shorten")
s3, b3 = http("POST", "/shorten",
              body={"url": "not-a-url-at-all"},
              headers={"X-API-Key": API_KEY})
show("POST /shorten bad URL", s3, b3)
if s3 not in (400, 422):
    fail(f"Expected 400 or 422, got {s3}")
ok(f"Rejected with HTTP {s3}")

# ======================================================================
# TEST 4: Invalid URL -- javascript: scheme
# ======================================================================
section("TEST 4: Invalid URL -- javascript: scheme  POST /shorten")
s4, b4 = http("POST", "/shorten",
              body={"url": "javascript:alert(1)"},
              headers={"X-API-Key": API_KEY})
show("POST /shorten js: scheme", s4, b4)
if s4 not in (400, 422):
    fail(f"Expected 400 or 422, got {s4}")
ok(f"Rejected with HTTP {s4}")

# ======================================================================
# TEST 5: Missing API key header
# ======================================================================
section("TEST 5: Missing API key header  POST /shorten")
s5, b5 = http("POST", "/shorten",
              body={"url": "https://example.com"})
show("POST /shorten no auth", s5, b5)
if s5 not in (401, 422):
    fail(f"Expected 401 or 422, got {s5}")
ok(f"Rejected with HTTP {s5}")

# ======================================================================
# TEST 6: Wrong API key
# ======================================================================
section("TEST 6: Wrong API key  POST /shorten")
s6, b6 = http("POST", "/shorten",
              body={"url": "https://example.com"},
              headers={"X-API-Key": "totally-wrong-key"})
show("POST /shorten wrong key", s6, b6)
if s6 != 401:
    fail(f"Expected 401, got {s6}")
ok("401 Unauthorized for wrong key")

# ======================================================================
# TEST 7: Valid redirect
# ======================================================================
section(f"TEST 7: Valid redirect  GET /{short_code}")
s7, b7 = http("GET", f"/{short_code}")
show(f"GET /{short_code}", s7, b7)
if s7 != 302:
    fail(f"Expected 302 redirect, got {s7}")
ok("302 redirect issued")

# ======================================================================
# TEST 8: Stats after redirect -- click_count should be 1
# ======================================================================
section(f"TEST 8: Stats after one redirect  GET /stats/{short_code}")
s8, b8 = http("GET", f"/stats/{short_code}")
show(f"GET /stats/{short_code}", s8, b8)
if s8 != 200:
    fail(f"Expected 200, got {s8}")
if b8.get("click_count") != 1:
    fail(f"Expected click_count=1, got {b8.get('click_count')}")
ok(f"click_count={b8['click_count']} -- counter incremented correctly")

# ======================================================================
# TEST 9: Missing short code -- 404
# ======================================================================
section("TEST 9: Missing short code  GET /NOTEXIST")
s9, b9 = http("GET", "/NOTEXIST")
show("GET /NOTEXIST", s9, b9)
if s9 != 404:
    fail(f"Expected 404, got {s9}")
ok("404 Not Found")

# ======================================================================
# TEST 10: Stats for missing code -- 404
# ======================================================================
section("TEST 10: Stats for missing code  GET /stats/NOTEXIST")
s10, b10 = http("GET", "/stats/NOTEXIST")
show("GET /stats/NOTEXIST", s10, b10)
if s10 != 404:
    fail(f"Expected 404, got {s10}")
ok("404 Not Found")

# ======================================================================
# TEST 11: Create URL with explicit expiry
# ======================================================================
section("TEST 11: Create URL with explicit expires_in_days=1")
s11, b11 = http("POST", "/shorten",
                body={"url": "https://docs.python.org/3/", "expires_in_days": 1},
                headers={"X-API-Key": API_KEY})
show("POST /shorten with expiry=1", s11, b11)
if s11 != 200:
    fail(f"Expected 200, got {s11}")
if not b11.get("expires_at"):
    fail("Expected expires_at to be set")
ok(f"expires_at={b11['expires_at']}")

# ======================================================================
# TEST 12: Create URL with expires_in_days=0 (never expire)
# ======================================================================
section("TEST 12: Create URL with expires_in_days=0 (never expire)")
s12, b12 = http("POST", "/shorten",
                body={"url": "https://fastapi.tiangolo.com/", "expires_in_days": 0},
                headers={"X-API-Key": API_KEY})
show("POST /shorten no-expiry", s12, b12)
if s12 != 200:
    fail(f"Expected 200, got {s12}")
if b12.get("expires_at") is not None:
    fail(f"Expected expires_at=null, got {b12.get('expires_at')}")
ok("expires_at=null -- never-expiring link created")

# ======================================================================
# TEST 13: Health check
# ======================================================================
section("TEST 13: Health check  GET /health")
s13, b13 = http("GET", "/health")
show("GET /health", s13, b13)
if s13 != 200 or (isinstance(b13, dict) and b13.get("status") != "ok"):
    fail("Health check failed")
ok("Server is healthy")

print(f"\n{DIVIDER}")
print("  ALL 13 TESTS PASSED")
print(DIVIDER)
