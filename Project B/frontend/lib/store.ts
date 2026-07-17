/**
 * lib/store.ts — localStorage-backed session store for created short URLs.
 *
 * Persists across page refreshes (localStorage) but is isolated to the browser.
 * Each entry stores the short code + long URL so the dashboard can display them
 * and re-fetch stats without needing to remember the full response.
 */

const STORAGE_KEY = "url_shortener_session";

export interface SessionEntry {
  shortCode: string;
  shortUrl: string;
  longUrl: string;
  createdAt: string;
  expiresAt: string | null;
}

/** Read all session entries from localStorage. Returns [] if empty or on error. */
export function getSessionEntries(): SessionEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as SessionEntry[];
  } catch {
    return [];
  }
}

/** Add a new entry to the session store (prepends so newest is first). */
export function addSessionEntry(entry: SessionEntry): void {
  if (typeof window === "undefined") return;
  const existing = getSessionEntries();
  // Avoid duplicates — update in place if short_code already exists
  const filtered = existing.filter((e) => e.shortCode !== entry.shortCode);
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify([entry, ...filtered])
  );
}

/** Clear all session entries. */
export function clearSessionEntries(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
}
