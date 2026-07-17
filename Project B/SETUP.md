# SETUP.md — URL Shortener Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- git

## 1. Clone the repo

```bash
git clone <repo-url>
cd <repo-directory>
```

## 2. Backend setup

### Install dependencies

```bash
cd backend        # adjust if your backend folder has a different name
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Set the API key

The backend reads the expected API key from an environment variable.

```bash
# macOS/Linux
export API_KEY="your-api-key"

# Windows (PowerShell)
$env:API_KEY="your-api-key"
```

Or create a `.env` file in the backend directory:

```
API_KEY=your-api-key
```

### Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Backend is now live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Run backend tests

```bash
pytest
```

Tests use an isolated/in-memory SQLite database — no setup needed.

## 3. Frontend setup

### Install dependencies

```bash
cd ../frontend     # adjust if your frontend folder has a different name
npm install
```

### Set the API key

Create `.env.local` in the frontend directory:

```
NEXT_PUBLIC_API_KEY=your-api-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> ⚠️ Must match the `API_KEY` set on the backend.

### Run the frontend

```bash
npm run dev
```

Frontend is now live at `http://localhost:3000`.

## 4. Verify it works

1. Open `http://localhost:3000`.
2. Paste a URL into the Shorten form and submit.
3. Confirm a short URL is returned.
4. Switch to the Dashboard tab — the new link and its click count should appear.
5. Visit the short URL directly and confirm it redirects, then refresh the Dashboard to see the click count increment.

## Troubleshooting

| Issue | Fix |
|---|---|
| `401` on `/shorten` | `NEXT_PUBLIC_API_KEY` (frontend) and `API_KEY` (backend) don't match |
| CORS errors in browser console | Confirm backend is running on the port referenced by `NEXT_PUBLIC_API_URL` |
| Dashboard shows no links | Links are stored in browser `localStorage` — only visible in the same browser/session that created them |
