/**
 * lib/api.ts — typed API client for the URL Shortener backend.
 *
 * All requests go to NEXT_PUBLIC_BACKEND_URL.
 * The shorten endpoint requires NEXT_PUBLIC_API_KEY in the X-API-Key header.
 */

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ShortenResponse {
  short_code: string;
  short_url: string;
  long_url: string;
  created_at: string;
  expires_at: string | null;
  is_duplicate: boolean;
}

export interface StatsResponse {
  short_code: string;
  long_url: string;
  click_count: number;
  created_at: string;
  expires_at: string | null;
}

export interface ApiError {
  detail: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function parseResponse<T>(res: Response): Promise<T> {
  const text = await res.text();
  let json: unknown;
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(`Server returned non-JSON response (${res.status}): ${text.slice(0, 200)}`);
  }

  if (!res.ok) {
    const err = json as ApiError;
    throw new Error(err?.detail || `Request failed with status ${res.status}`);
  }

  return json as T;
}

// ─── API calls ────────────────────────────────────────────────────────────────

/**
 * POST /shorten — create or retrieve a short URL.
 * Throws an Error with a human-readable message on any failure.
 */
export async function shortenUrl(
  longUrl: string,
  expiresInDays?: number
): Promise<ShortenResponse> {
  const body: Record<string, unknown> = { url: longUrl };
  if (expiresInDays !== undefined) {
    body.expires_in_days = expiresInDays;
  }

  const res = await fetch(`${BACKEND_URL}/shorten`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify(body),
  });

  return parseResponse<ShortenResponse>(res);
}

/**
 * GET /stats/{short_code} — fetch click count and metadata.
 * Throws an Error with a human-readable message on any failure.
 */
export async function getStats(shortCode: string): Promise<StatsResponse> {
  const res = await fetch(`${BACKEND_URL}/stats/${shortCode}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  return parseResponse<StatsResponse>(res);
}
