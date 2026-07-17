"use client";

import { useState, useEffect, useCallback } from "react";
import { getStats, StatsResponse } from "@/lib/api";
import { getSessionEntries, clearSessionEntries, SessionEntry } from "@/lib/store";

interface EnrichedEntry extends SessionEntry {
  clickCount: number | null;
  statsError: string | null;
  statsLoading: boolean;
}

export default function Dashboard() {
  const [entries, setEntries] = useState<EnrichedEntry[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  // Load session entries and seed click counts as null (not yet fetched)
  function loadFromStore() {
    const stored = getSessionEntries();
    setEntries(
      stored.map((e) => ({
        ...e,
        clickCount: null,
        statsError: null,
        statsLoading: false,
      }))
    );
  }

  useEffect(() => {
    loadFromStore();
  }, []);

  // Expose a method parent can call after a new URL is created
  // (Dashboard re-reads localStorage when it mounts, and on refresh)
  // The parent drives this via the `key` prop trick or a refresh signal.

  const fetchAllStats = useCallback(async (current: EnrichedEntry[]) => {
    if (current.length === 0) return;

    // Mark all as loading
    setEntries((prev) =>
      prev.map((e) => ({ ...e, statsLoading: true, statsError: null }))
    );

    // Fire all requests in parallel
    const results = await Promise.allSettled(
      current.map((e) => getStats(e.shortCode))
    );

    setEntries((prev) =>
      prev.map((e, i) => {
        const result = results[i];
        if (result.status === "fulfilled") {
          return { ...e, clickCount: result.value.click_count, statsLoading: false, statsError: null };
        } else {
          return {
            ...e,
            statsLoading: false,
            statsError:
              result.reason instanceof Error
                ? result.reason.message
                : "Failed to fetch stats",
          };
        }
      })
    );
    setLastRefreshed(new Date());
  }, []);

  async function handleRefresh() {
    setRefreshing(true);
    // Reload from store first (in case new URLs were added)
    const stored = getSessionEntries();
    const enriched: EnrichedEntry[] = stored.map((e) => ({
      ...e,
      clickCount: null,
      statsLoading: true,
      statsError: null,
    }));
    setEntries(enriched);
    await fetchAllStats(enriched);
    setRefreshing(false);
  }

  function handleClear() {
    clearSessionEntries();
    setEntries([]);
    setLastRefreshed(null);
  }

  // ─── Empty state ─────────────────────────────────────────────────────────────
  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 rounded-2xl bg-white/5 p-5">
          <svg
            className="h-10 w-10 text-slate-500"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z"
            />
          </svg>
        </div>
        <p className="text-slate-400 text-sm">No URLs shortened yet in this session.</p>
        <p className="text-slate-600 text-xs mt-1">
          Create a short URL using the Shorten tab.
        </p>
      </div>
    );
  }

  // ─── Table ───────────────────────────────────────────────────────────────────
  return (
    <div className="w-full">
      {/* Header row */}
      <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <div className="text-sm text-slate-400">
          <span className="text-white font-semibold">{entries.length}</span> URL
          {entries.length !== 1 ? "s" : ""} in this session
          {lastRefreshed && (
            <span className="ml-3 text-slate-600 text-xs">
              Last refreshed {lastRefreshed.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="
              flex items-center gap-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40
              border border-indigo-500/20 px-3 py-1.5 text-xs font-semibold text-indigo-300
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500
            "
          >
            <svg
              className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`}
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
              />
            </svg>
            {refreshing ? "Refreshing…" : "Refresh counts"}
          </button>
          <button
            onClick={handleClear}
            className="
              rounded-lg bg-red-900/20 hover:bg-red-900/40
              border border-red-500/20 px-3 py-1.5 text-xs font-semibold text-red-400
              transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500
            "
          >
            Clear session
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Original URL
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Short URL
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Expires
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">
                Clicks
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {entries.map((entry) => (
              <tr
                key={entry.shortCode}
                className="group hover:bg-white/5 transition-colors duration-150"
              >
                {/* Original URL */}
                <td className="px-4 py-3 max-w-xs">
                  <span
                    className="block truncate text-slate-300 text-xs"
                    title={entry.longUrl}
                  >
                    {entry.longUrl}
                  </span>
                </td>

                {/* Short URL */}
                <td className="px-4 py-3">
                  <a
                    href={entry.shortUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-mono text-indigo-400 hover:text-indigo-300 text-xs transition-colors"
                  >
                    {entry.shortUrl}
                  </a>
                </td>

                {/* Expires */}
                <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                  {entry.expiresAt
                    ? new Date(entry.expiresAt).toLocaleDateString()
                    : <span className="text-slate-600">Never</span>}
                </td>

                {/* Clicks */}
                <td className="px-4 py-3 text-right">
                  {entry.statsLoading ? (
                    <svg
                      className="inline animate-spin h-3.5 w-3.5 text-slate-500"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      />
                    </svg>
                  ) : entry.statsError ? (
                    <span
                      className="text-red-400 text-xs"
                      title={entry.statsError}
                    >
                      Error
                    </span>
                  ) : entry.clickCount !== null ? (
                    <span className="font-semibold text-white">
                      {entry.clickCount.toLocaleString()}
                    </span>
                  ) : (
                    <span className="text-slate-600 text-xs">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
