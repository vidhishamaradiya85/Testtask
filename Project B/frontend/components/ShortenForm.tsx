"use client";

import { useState } from "react";
import { shortenUrl, ShortenResponse } from "@/lib/api";
import { addSessionEntry } from "@/lib/store";

interface Props {
  onCreated?: () => void; // callback to notify Dashboard to refresh
}

export default function ShortenForm({ onCreated }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ShortenResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setCopied(false);

    try {
      const data = await shortenUrl(url.trim());
      setResult(data);

      // Persist to session store so Dashboard can show it
      addSessionEntry({
        shortCode: data.short_code,
        shortUrl: data.short_url,
        longUrl: data.long_url,
        createdAt: data.created_at,
        expiresAt: data.expires_at,
      });

      onCreated?.();
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!result?.short_url) return;
    try {
      await navigator.clipboard.writeText(result.short_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback for browsers that block clipboard API
      const ta = document.createElement("textarea");
      ta.value = result.short_url;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* ── Form ── */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="long-url"
            className="text-sm font-semibold text-slate-300 tracking-wide uppercase"
          >
            Long URL
          </label>
          <input
            id="long-url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/very/long/url/that/needs/shortening"
            required
            disabled={loading}
            className="
              w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3
              text-white placeholder-slate-500 text-sm
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          />
        </div>

        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="
            relative flex items-center justify-center gap-2
            rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700
            px-6 py-3 text-sm font-semibold text-white
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-200 shadow-lg shadow-indigo-900/40
            focus:outline-none focus:ring-2 focus:ring-indigo-400
          "
        >
          {loading ? (
            <>
              {/* Spinner */}
              <svg
                className="animate-spin h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
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
              Shortening…
            </>
          ) : (
            <>
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M10.172 13.828a4 4 0 015.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
              </svg>
              Shorten URL
            </>
          )}
        </button>
      </form>

      {/* ── Error ── */}
      {error && (
        <div
          role="alert"
          className="
            mt-5 flex items-start gap-3 rounded-xl border border-red-500/30
            bg-red-950/40 px-4 py-3 text-sm text-red-300
          "
        >
          <svg
            className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-400"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* ── Result ── */}
      {result && (
        <div className="mt-5 rounded-xl border border-emerald-500/20 bg-emerald-950/30 p-4">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            {result.is_duplicate ? "Already shortened — existing link" : "Short URL created!"}
          </p>

          {/* Short URL row */}
          <div className="mt-2 flex items-center gap-2 rounded-lg bg-white/5 border border-white/10 px-3 py-2">
            <a
              href={result.short_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 truncate text-sm font-mono text-indigo-300 hover:text-indigo-200 transition-colors"
            >
              {result.short_url}
            </a>
            <button
              onClick={handleCopy}
              title="Copy to clipboard"
              className="
                flex-shrink-0 rounded-md px-3 py-1 text-xs font-semibold
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-indigo-400
                bg-indigo-600/40 hover:bg-indigo-600/70 text-indigo-200
              "
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>

          {/* Metadata */}
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
            <span>
              <span className="text-slate-500">Original: </span>
              <span className="truncate max-w-xs inline-block align-bottom">
                {result.long_url}
              </span>
            </span>
            {result.expires_at && (
              <span>
                <span className="text-slate-500">Expires: </span>
                {new Date(result.expires_at).toLocaleDateString()}
              </span>
            )}
            {!result.expires_at && (
              <span className="text-slate-500">Never expires</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
