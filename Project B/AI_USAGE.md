# AI Usage Log

This document records which AI tools were used at each step of building the URL shortener, and why.

## Summary

Two AI tools were used for different tasks. Backend implementation, tests, and frontend implementation were done with **Google Antigravity (agent mode, Gemini-based)**, since its ability to run code and verify output in a real terminal/browser made it better suited for iterative implementation and debugging than a text-only assistant. **Claude (chat)** was used for planning docs, API documentation, and this usage log, since it's stronger for structured reasoning and clear technical writing than for autonomous code execution. Tool choice was based on task fit — execution and verification work went to Antigravity, and reasoning/writing work went to Claude.

**Transcript methodology:** Prompts and key responses were manually logged into `/prompts/` as work progressed, since Antigravity doesn't export a linear chat transcript the way a chat-based tool does.

## AI usage by step

| Step | Tool used | Why |
|---|---|---|
| Planning / design docs | Claude (chat) | Structured reasoning about API design, edge cases, and status codes benefits from a dedicated planning/writing pass rather than an agent loop. |
| Backend implementation (FastAPI routes, models, storage) | Google Antigravity (agent mode) | Needed to write, run, and iterate on real code against a live server. |
| Backend tests (pytest, in-memory SQLite) | Google Antigravity (agent mode) | Tests were run and re-run in a real terminal to confirm pass/fail, not just generated as text. |
| Frontend implementation (Shorten form, Dashboard) | Google Antigravity (agent mode) | Needed to run the dev server and verify behavior in an actual browser (form submission, redirects, click counts). |
| API documentation (`API.md`) | Claude (chat) | Clear, consistent technical writing across endpoints, request/response examples, and status codes. |
| Setup guide (`SETUP.md`) | Claude (chat) | Same reasoning — structured, readable documentation rather than code execution. |
| This usage log (`AI_USAGE.md`) | Claude (chat) | Same reasoning as above. |

## Transcript methodology

Antigravity does not export a linear chat transcript the way a chat-based tool does, since it runs in agent mode against a terminal/browser rather than a single conversational thread. To keep a record, prompts given to Antigravity and their key responses (code changes, test results, decisions made) were manually logged into `/prompts/` as the work progressed.
