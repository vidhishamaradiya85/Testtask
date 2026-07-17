# Notes App

A simple full-stack notes application built with FastAPI and Next.js. 

This was put together to have a clean separation between the backend API and the frontend UI. It uses SQLite for storing notes, making it super easy to run locally without having to set up a dedicated database server.

## Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy, SQLite
* **Frontend:** Next.js (React), TypeScript, Tailwind CSS

## How to run it locally

You'll need to run the backend and the frontend in two separate terminal windows.

### 1. Start the Backend

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```bash
   uvicorn app.main:app --reload
   ```
   *The backend API will be running on `http://localhost:8000`*

### 2. Start the Frontend

1. Open a new terminal window and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install the node modules:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The app will be running on `http://localhost:3000`*

---

## Notes on sharing this project

If you need to ZIP this project and send it to someone, make sure to delete these folders first to keep the file size small:
- `frontend/node_modules/`
- `frontend/.next/`
- `backend/venv/`
- `backend/app/__pycache__/`

The person receiving the ZIP will just need to run `npm install` and `pip install` as shown in the steps above to get everything working again.
