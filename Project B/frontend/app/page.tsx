"use client";

import { useState, useCallback } from "react";
import ShortenForm from "@/components/ShortenForm";
import Dashboard from "@/components/Dashboard";

type Tab = "shorten" | "dashboard";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("shorten");
  // Increment this to force Dashboard to re-read localStorage after a new URL is created
  const [dashboardKey, setDashboardKey] = useState(0);

  const handleUrlCreated = useCallback(() => {
    // If already on dashboard, bump key to trigger re-mount and refresh
    if (activeTab === "dashboard") {
      setDashboardKey((k) => k + 1);
    }
    // Optionally auto-switch to dashboard after creation:
    // setActiveTab("dashboard");
  }, [activeTab]);

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    {
      id: "shorten",
      label: "Shorten",
      icon: (
        <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m0 0l1.1-1.1m-1.1 1.1a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
    },
    {
      id: "dashboard",
      label: "Dashboard",
      icon: (
        <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      {/* Background glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-violet-600/10 blur-3xl" />
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        {/* ── Header ── */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center rounded-2xl bg-indigo-600/20 border border-indigo-500/20 p-3 mb-4">
            <svg
              className="h-7 w-7 text-indigo-400"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            URL Shortener
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Shorten long URLs and track clicks in real time
          </p>
        </div>

        {/* ── Card ── */}
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm shadow-2xl shadow-black/40">
          {/* Tab Bar */}
          <div className="flex border-b border-white/10 px-2 pt-2 gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === "dashboard") {
                    setDashboardKey((k) => k + 1);
                  }
                }}
                className={`
                  flex items-center gap-2 px-5 py-3 rounded-t-lg text-sm font-medium
                  border-b-2 -mb-px transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-transparent
                  ${
                    activeTab === tab.id
                      ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
                      : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600"
                  }
                `}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6 sm:p-8">
            {activeTab === "shorten" && (
              <ShortenForm onCreated={handleUrlCreated} />
            )}
            {activeTab === "dashboard" && (
              <Dashboard key={dashboardKey} />
            )}
          </div>
        </div>

        {/* ── Footer ── */}
        <p className="mt-8 text-center text-xs text-slate-600">
          Backend:{" "}
          <code className="text-slate-500">
            {process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001"}
          </code>
        </p>
      </div>
    </div>
  );
}
