# 🚀 How to Run 19 Labs

This guide will help you get the **19 Labs LIMS** platform running locally on your machine.

---

## 1. Prerequisites

Before you start, ensure you have the following installed:

*   **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
*   **Node.js 18+ (LTS)**: [Download Here](https://nodejs.org/)
*   **PostgreSQL 15+**: [Download Here](https://www.postgresql.org/download/)
    *   **Important**: During installation, install **Stack Builder** to add the **PostGIS** extension.

---

## 2. Database Setup

1.  Open your terminal or pgAdmin.
2.  Create a new database named `19labs`.
3.  Run the following SQL commands to enable required extensions:
    ```sql
    CREATE EXTENSION postgis;
    CREATE EXTENSION pg_trgm;
    ```
4.  **No migrations tool used?** We have SQL files in `backend/migrations/`. You can run them manually in order (001 to 007) to set up the tables, **OR** rely on the backend to initialize (if configured), but manual execution is safest for this MVP.
    *   *Tip: Copy contents of `backend/migrations/*.sql` and run them in your SQL Query tool.*

---

## 3. Backend Setup (Python FastAPI)

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```

3.  Activate the virtual environment:
    *   **Windows (PowerShell)**: `.\venv\Scripts\Activate`
    *   **Mac/Linux**: `source venv/bin/activate`

4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5.  Configure Environment:
    *   Copy `.env.example` to `.env`.
    *   Update `DATABASE_URL` with your Postgres credentials.
        *   Example: `postgresql+asyncpg://postgres:password@localhost:5432/19labs`

6.  Start the Server:
    ```bash
    uvicorn main:app --reload
    ```
    *   You should see: `Uvicorn running on http://127.0.0.1:8000`
    *   API Docs enabled at: `http://127.0.0.1:8000/docs`

---

## 4. Frontend Setup (Next.js)

1.  Navigate to the frontend directory (open a new terminal):
    ```bash
    cd frontend
    ```

2.  Install libraries:
    ```bash
    npm install
    ```

3.  Start the Development Server:
    ```bash
    npm run dev
    ```
    *   You should see: `Result: Ready on http://localhost:3000`

---

## 5. Using the System

Open your browser to `http://localhost:3000`.

### Key Workflows:
1.  **Onboarding**: The landing page will prompt you to set up your lab.
2.  **Reception**: Go to `/dashboard/reception` to book patients.
3.  **Phlebotomy**: Open `/dashboard/phlebotomy` on a mobile/tablet view to collect samples.
4.  **Technician**: Go to `/dashboard/technician` to enter results.
5.  **Pathologist**: Go to `/dashboard/pathologist` to sign reports.
6.  **Patient**: Go to `/portal/login` (Use phone `9999999999`, OTP `123456`).

---
**Troubleshooting**:
*   *DB Connection Error?* Check your `DATABASE_URL` in `backend/.env`.
*   *Missing Modules?* Ensure you ran `pip install` inside the active `venv`.
