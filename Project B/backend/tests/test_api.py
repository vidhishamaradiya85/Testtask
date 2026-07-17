"""
test_api.py — pytest test suite for the URL shortener backend.

Each test is independent: it receives a fresh in-memory SQLite database via
the `client` fixture, so tests can run in any order without side effects.

Coverage
--------
- POST /shorten: valid creation, duplicate dedup, bad URL, auth failures
- GET /{short_code}: valid redirect (302) + click count increment
- GET /stats/{short_code}: click count accuracy across multiple redirects
- GET /{short_code}: 404 for unknown codes, 410 for expired codes
- GET /stats/{short_code}: 404 for unknown codes
"""

import pytest

from tests.conftest import (
    VALID_URL,
    VALID_URL_2,
    TEST_API_KEY,
    _insert_expired_url,
)


# ===========================================================================
# POST /shorten — creation
# ===========================================================================

class TestShortenCreate:
    """Tests for the POST /shorten endpoint (valid creation)."""

    def test_create_returns_200_with_expected_fields(self, client, auth_headers):
        """A well-formed URL with a valid API key returns 200 and all required fields."""
        resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert "short_code" in body
        assert "short_url" in body
        assert "long_url" in body
        assert "created_at" in body
        assert "expires_at" in body
        assert body["long_url"] == VALID_URL
        assert body["is_duplicate"] is False

    def test_short_code_is_7_chars_alphanumeric(self, client, auth_headers):
        """Generated short code must be exactly 7 base62 characters."""
        resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        code = resp.json()["short_code"]
        assert len(code) == 7
        assert code.isalnum(), f"Expected alphanumeric code, got: {code!r}"

    def test_short_url_contains_short_code(self, client, auth_headers):
        """short_url must embed the short_code."""
        resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        body = resp.json()
        assert body["short_code"] in body["short_url"]

    def test_default_expiry_is_set(self, client, auth_headers):
        """With no explicit expires_in_days, server applies the default (non-null)."""
        resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert resp.json()["expires_at"] is not None

    def test_explicit_expiry_days_is_respected(self, client, auth_headers):
        """expires_in_days=3 must produce a non-null expires_at in the response."""
        resp = client.post(
            "/shorten",
            json={"url": VALID_URL, "expires_in_days": 3},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["expires_at"] is not None

    def test_expires_in_days_zero_creates_never_expiring_link(self, client, auth_headers):
        """expires_in_days=0 must produce expires_at=null (never expires)."""
        resp = client.post(
            "/shorten",
            json={"url": VALID_URL, "expires_in_days": 0},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["expires_at"] is None

    def test_two_different_urls_produce_different_codes(self, client, auth_headers):
        """Two distinct long URLs must get distinct short codes."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r2 = client.post("/shorten", json={"url": VALID_URL_2}, headers=auth_headers)
        assert r1.json()["short_code"] != r2.json()["short_code"]


# ===========================================================================
# POST /shorten — authentication
# ===========================================================================

class TestShortenAuth:
    """Tests that creation is properly gated behind the API key."""

    def test_missing_api_key_returns_422(self, client):
        """Omitting X-API-Key entirely → 422 (field required by FastAPI)."""
        resp = client.post("/shorten", json={"url": VALID_URL})
        assert resp.status_code == 422

    def test_wrong_api_key_returns_401(self, client):
        """Supplying an incorrect key → 401 Unauthorized."""
        resp = client.post(
            "/shorten",
            json={"url": VALID_URL},
            headers={"X-API-Key": "this-is-definitely-wrong"},
        )
        assert resp.status_code == 401
        assert "detail" in resp.json()

    def test_empty_api_key_returns_401(self, client):
        """An empty string key → 401 (not a server error)."""
        resp = client.post(
            "/shorten",
            json={"url": VALID_URL},
            headers={"X-API-Key": ""},
        )
        assert resp.status_code == 401

    def test_correct_api_key_is_accepted(self, client, auth_headers):
        """Sanity: correct key must not be rejected."""
        resp = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# POST /shorten — URL validation
# ===========================================================================

class TestShortenUrlValidation:
    """Tests that malformed / disallowed URLs are rejected."""

    @pytest.mark.parametrize("bad_url", [
        "not-a-url-at-all",
        "ftp://example.com/file",        # non-http/https scheme
        "javascript:alert(1)",           # script injection scheme
        "data:text/html,<h1>hi</h1>",    # data: scheme
        "//example.com/no-scheme",       # protocol-relative (no scheme)
        "",                              # empty string
    ])
    def test_invalid_url_rejected(self, client, auth_headers, bad_url):
        """Each invalid URL must be rejected with a 4xx response."""
        resp = client.post(
            "/shorten",
            json={"url": bad_url},
            headers=auth_headers,
        )
        assert resp.status_code in (400, 422), (
            f"Expected 400/422 for URL {bad_url!r}, got {resp.status_code}"
        )

    def test_http_url_is_accepted(self, client, auth_headers):
        """http:// (non-HTTPS) is a valid scheme and must be accepted."""
        resp = client.post(
            "/shorten",
            json={"url": "http://example.com/plain-http"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_https_url_is_accepted(self, client, auth_headers):
        """https:// URLs must be accepted."""
        resp = client.post(
            "/shorten",
            json={"url": "https://secure.example.com/"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_url_too_long_is_rejected(self, client, auth_headers):
        """URLs longer than 2048 characters must be rejected."""
        long_url = "https://example.com/" + "a" * 2050
        resp = client.post(
            "/shorten",
            json={"url": long_url},
            headers=auth_headers,
        )
        assert resp.status_code in (400, 422)

    def test_missing_body_returns_error(self, client, auth_headers):
        """Sending no JSON body at all must return a 4xx."""
        resp = client.post("/shorten", headers=auth_headers)
        assert resp.status_code in (400, 422)


# ===========================================================================
# POST /shorten — duplicate dedup
# ===========================================================================

class TestShortenDuplicate:
    """Tests that the same long URL returns the existing short code (dedup)."""

    def test_duplicate_returns_same_short_code(self, client, auth_headers):
        """Submitting the same URL twice must return the same short_code both times."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r2 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["short_code"] == r2.json()["short_code"]

    def test_duplicate_response_has_is_duplicate_true(self, client, auth_headers):
        """Second call for the same URL must set is_duplicate=true."""
        client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r2 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert r2.json()["is_duplicate"] is True

    def test_first_creation_has_is_duplicate_false(self, client, auth_headers):
        """First call for a URL must set is_duplicate=false."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert r1.json()["is_duplicate"] is False

    def test_different_urls_are_not_deduped(self, client, auth_headers):
        """Two distinct URLs must each get their own unique code."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r2 = client.post("/shorten", json={"url": VALID_URL_2}, headers=auth_headers)
        assert r2.json()["is_duplicate"] is False
        assert r1.json()["short_code"] != r2.json()["short_code"]

    def test_triple_submission_returns_same_code(self, client, auth_headers):
        """Third (and Nth) submission of the same URL still returns the original code."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r3 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        assert r1.json()["short_code"] == r3.json()["short_code"]
        assert r3.json()["is_duplicate"] is True


# ===========================================================================
# GET /{short_code} — redirect
# ===========================================================================

class TestRedirect:
    """Tests for the redirect endpoint."""

    def test_redirect_returns_302(self, client, created_url):
        """A valid short code must produce a 302 redirect."""
        code = created_url["short_code"]
        # TestClient does NOT follow redirects by default
        resp = client.get(f"/{code}", follow_redirects=False)
        assert resp.status_code == 302

    def test_redirect_location_is_original_url(self, client, created_url):
        """The Location header of the 302 must point to the original long URL."""
        code = created_url["short_code"]
        resp = client.get(f"/{code}", follow_redirects=False)
        assert resp.headers["location"] == VALID_URL

    def test_redirect_increments_click_count(self, client, created_url):
        """After one redirect hit, click_count in stats must equal 1."""
        code = created_url["short_code"]
        client.get(f"/{code}", follow_redirects=False)
        stats = client.get(f"/stats/{code}").json()
        assert stats["click_count"] == 1

    def test_redirect_click_count_before_any_hit_is_zero(self, client, created_url):
        """click_count must start at 0 before any redirect is made."""
        code = created_url["short_code"]
        stats = client.get(f"/stats/{code}").json()
        assert stats["click_count"] == 0

    def test_unknown_short_code_returns_404(self, client):
        """A short code that was never created must return 404."""
        resp = client.get("/NOTEXIST", follow_redirects=False)
        assert resp.status_code == 404

    def test_404_response_has_detail_field(self, client):
        """404 response body must include a 'detail' key."""
        resp = client.get("/NOTEXIST", follow_redirects=False)
        assert "detail" in resp.json()

    def test_expired_short_code_returns_410(self, client, db_conn):
        """A code whose expires_at is in the past must return 410 Gone."""
        _insert_expired_url(db_conn, short_code="EXP1234", long_url="https://old.example.com")
        resp = client.get("/EXP1234", follow_redirects=False)
        assert resp.status_code == 410

    def test_expired_code_does_not_increment_click_count(self, client, db_conn):
        """Hitting an expired code must NOT increment its click_count."""
        _insert_expired_url(db_conn, short_code="EXP5678", long_url="https://old2.example.com")
        client.get("/EXP5678", follow_redirects=False)   # expect 410
        row = db_conn.execute(
            "SELECT click_count FROM urls WHERE short_code = ?", ("EXP5678",)
        ).fetchone()
        assert row["click_count"] == 0, "Expired URL click_count should not be incremented"


# ===========================================================================
# GET /stats/{short_code} — stats
# ===========================================================================

class TestStats:
    """Tests for the stats endpoint."""

    def test_stats_returns_200_for_valid_code(self, client, created_url):
        """A valid short code must return 200 from the stats endpoint."""
        code = created_url["short_code"]
        resp = client.get(f"/stats/{code}")
        assert resp.status_code == 200

    def test_stats_response_has_all_required_fields(self, client, created_url):
        """Stats response must contain: short_code, long_url, click_count, created_at, expires_at."""
        code = created_url["short_code"]
        body = client.get(f"/stats/{code}").json()
        assert "short_code" in body
        assert "long_url" in body
        assert "click_count" in body
        assert "created_at" in body
        assert "expires_at" in body

    def test_stats_long_url_matches_original(self, client, created_url):
        """Stats must echo back the correct original long URL."""
        code = created_url["short_code"]
        body = client.get(f"/stats/{code}").json()
        assert body["long_url"] == VALID_URL

    def test_stats_click_count_zero_before_any_redirects(self, client, created_url):
        """click_count must be 0 immediately after creation, before any redirects."""
        code = created_url["short_code"]
        body = client.get(f"/stats/{code}").json()
        assert body["click_count"] == 0

    def test_stats_click_count_after_one_redirect(self, client, created_url):
        """click_count must be 1 after a single redirect hit."""
        code = created_url["short_code"]
        client.get(f"/{code}", follow_redirects=False)
        body = client.get(f"/stats/{code}").json()
        assert body["click_count"] == 1

    def test_stats_click_count_after_multiple_redirects(self, client, created_url):
        """click_count must match the exact number of redirect hits made."""
        code = created_url["short_code"]
        n_hits = 5
        for _ in range(n_hits):
            client.get(f"/{code}", follow_redirects=False)
        body = client.get(f"/stats/{code}").json()
        assert body["click_count"] == n_hits

    def test_stats_click_counts_are_per_code_not_global(self, client, auth_headers):
        """Click counts must be tracked independently per short code."""
        r1 = client.post("/shorten", json={"url": VALID_URL}, headers=auth_headers)
        r2 = client.post("/shorten", json={"url": VALID_URL_2}, headers=auth_headers)
        code1 = r1.json()["short_code"]
        code2 = r2.json()["short_code"]

        # Hit code1 three times, code2 once
        for _ in range(3):
            client.get(f"/{code1}", follow_redirects=False)
        client.get(f"/{code2}", follow_redirects=False)

        stats1 = client.get(f"/stats/{code1}").json()
        stats2 = client.get(f"/stats/{code2}").json()
        assert stats1["click_count"] == 3
        assert stats2["click_count"] == 1

    def test_stats_unknown_code_returns_404(self, client):
        """Stats for a non-existent short code must return 404."""
        resp = client.get("/stats/NOTEXIST")
        assert resp.status_code == 404

    def test_stats_404_has_detail_field(self, client):
        """Stats 404 response body must include a 'detail' key."""
        resp = client.get("/stats/NOTEXIST")
        assert "detail" in resp.json()

    def test_stats_available_for_expired_code(self, client, db_conn):
        """
        Stats must still return 200 for an expired URL.
        The redirect blocks on expiry, but the stats endpoint should remain
        accessible so users can see historical click data.
        """
        _insert_expired_url(db_conn, short_code="EXPSTATS", long_url="https://old3.example.com")
        resp = client.get("/stats/EXPSTATS")
        assert resp.status_code == 200
        body = resp.json()
        assert body["short_code"] == "EXPSTATS"


# ===========================================================================
# GET /health — sanity
# ===========================================================================

class TestHealth:
    """Smoke test for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
