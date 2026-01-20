# 19 Labs: The Enterprise-Grade LIMS Platform

> **"The Operating System for Modern Diagnostics"**

**19 Labs** is a high-performance, ultra-low-latency Laboratory Information Management System (LIMS) engineered for high-throughput diagnostic centers. It rejects the traditional "black box" enterprise software model in favor of a **Modular Monolith** architecture that combines the speed of "Fast-Manual" data entry with the safety of deterministic clinical logic.

---

## 🏗️ Architectural Philosophy

The system is built on four non-negotiable pillars:

1.  **Strict Multi-Tenancy (Row-Level Security)**
    *   **Concept**: We do not rely on application-level `WHERE` clauses to separate tenant data.
    *   **Implemenation**: PostgreSQL **Row-Level Security (RLS)** is enforced at the database kernel level. Even if a developer forgets a filter in the API code, the database *physically prevents* Data Leakage between labs.
    *   **Context**: `current_setting('app.current_lab_id')` is set at the start of every request.

2.  **"Deterministic Intelligence"**
    *   **Concept**: AI is great for marketing, but dangerous for diagnosis. We use Hardcoded Clinical Logic for patient safety.
    *   **Implementation**: Formulas (e.g., `LDL = Total Cholesterol - HDL - (Trig/5)`) and Delta Checks (comparing current results vs. patient history) are implemented as immutable, version-controlled code blocks, not probabilistic models.

3.  **Keyboard-First UX (Sub-100ms Latency)**
    *   **Concept**: A mouse slows down a high-volume phlebotomist.
    *   **Implementation**: The entire "Technician Result Entry" interface is navigable via `Tab` and `Enter`. Dropdowns use fuzzy matching. Forms auto-save.

4.  **Immutable Audit Trails**
    *   **Concept**: In a medical setting, "Deletion" is a myth.
    *   **Implementation**: Critical tables (`test_results`, `bookings`) have shadow `_audit` logs or dedicated history tables (`result_amendments`) triggered by database events.

---

## 🛠️ The Technology Stack

| Layer | Technology | Key Features Used |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** (Python 3.10) | Async IO, Pydantic v2 Validation, Dependency Injection. |
| **Database** | **PostgreSQL 15** | PostGIS (Geo-search), `pg_trgm` (Fuzzy Search), RLS Policies. |
| **ORM** | **SQLAlchemy** (Async) | Declarative Models, Connection Pooling. |
| **Auth** | **OAuth2 + JWT** | Stateless Authentication, Scoped Permissions (`report:approve`). |
| **Frontend** | **Next.js 15** | App Router, Server Components. |
| **Styling** | **Tailwind CSS** | Medical-grade utility classes, Shadcn/UI primitives. |
| **State** | **React Query** | Server-State hydration, Optimistic UI updates. |
| **PDF Engine** | **Jinja2 + HTML** | Pixel-perfect layouts using CSS Paged Media. |

---

## 📦 The 10-Module Ecosystem

### � Phase 1: Commercial Onboarding
**Module 1: Smart Onboarding Engine**
*   **Problem**: Setting up a LIMS usually takes weeks.
*   **Solution**: A 4-step wizard that scrapes Google Places for address data and seeds the database with 500+ NABL-standard tests based on the lab's specialty.
*   **Tech**: Google Places API, Bulk Insert.

**Module 2: IAM & Staff RBAC**
*   **Problem**: Phlebotomists shouldn't see Billing data.
*   **Solution**: A Matrix-based permission system. Roles are defined by atoms (`billing:view`, `report:sign`).
*   **Tech**: Custom RBAC Middleware, Invite Tokens.

**Module 3: Zero-Trust Authentication**
*   **Problem**: Shared passwords are a security risk.
*   **Solution**: OTP-based or Strong Password enforcement. IP Logging for every session.
*   **Tech**: Argon2 Hashing, JWT Rotation.

---

### � Phase 2: Operations & Front Desk
**Module 5: Public Marketing Engine**
*   **Problem**: Labs have terrible websites.
*   **Solution**: Auto-generates a SEO-optimized profile (`19labs.com/lab/apollo-diagnostics`) with "Best Price" badges.
*   **Tech**: Next.js Dynamic Routes, JSON-LD Schema Injection.

**Module 6: Point of Sale (POS)**
*   **Problem**: Patient registration is slow.
*   **Solution**: "Flash Search" uses PostgreSQL GIN Indexes to find returning patients by name or phone in <20ms. Live Cart calculates taxes/discounts instantly.
*   **Tech**: `pg_trgm`, Optimistic React State.

**Module 7: Sample Logistics (Phlebotomy)**
*   **Problem**: Wrong tube usage (e.g., putting blood in a Urine cup).
*   **Solution**: The **Accession Splitter** automatically breaks a Booking into individual "Tube Cards" (Lavender for EDTA, etc.) on the mobile dashboard.
*   **Tech**: Logic Engine, ZPL Label Generation.

---

### � Phase 3: Clinical Execution
**Module 8: Result Entry Engine**
*   **Problem**: Typo errors (e.g., entering 140 instead of 14.0).
*   **Solution**:
    *   **Live Reference Checks**: Borders turn Red immediately if value is High/Low.
    *   **Delta Checks**: Fetches the patient's last 3 visits to flag anomalous jumps (>30%).
    *   **Formula Hook**: Auto-calculates derived parameters (Globulin, A/G Ratio, LDL).
*   **Tech**: TanStack Table (Virtualization), Python Formula Service.

**Module 9: The Pathologist's Cockpit**
*   **Problem**: Doctors waste time reviewing normal reports.
*   **Solution**: **Visual Triage**. The worklist auto-sorts by "Panic Values" and "STAT" urgency.
*   **Feature**: **Split-Screen Review** shows current results side-by-side with historical charts.
*   **Tech**: Recharts, Digital Signature Injection.

---

### � Phase 4: Delivery & Experience
**Module 10: The Reporting Engine**
*   **Problem**: PDFs look generic and are easily forged.
*   **Solution**:
    *   **Branding**: Dynamic header/footer injection with the Lab's specific Logo.
    *   **Tamper-Proofing**: A QR Code on every report links to a public `/verify/[hash]` URL.
*   **Patient Portal**: A password-less, OTP-secured vault for patients to view trends and download history.
*   **Tech**: HTML-to-PDF, OTP Auth.

---

## 🏃‍♂️ Developer Setup Guide

### 1. Database Initialization
Ensure PostgreSQL 15 is installed with PostGIS.
```sql
CREATE DATABASE lims_db;
CREATE EXTENSION postgis;
CREATE EXTENSION pg_trgm;
```

### 2. Backend Environment
Create a `.env` file in `/backend`:
```ini
DATABASE_URL=postgresql://user:pass@localhost:5432/lims_db
SECRET_KEY=super_secret_jwt_key
ALGORITHM=HS256
GOOGLE_ABI_KEY=your_key_here
AWS_ACCESS_KEY_ID=minio_or_aws
```

### 3. Running the Stack
**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### 4. Default Credentials (Seed Data)
*   **Admin Email**: `admin@19labs.demo`
*   **Password**: `Admin@123`

---

## 🗺️ Project Directory Structure

```
d:/19labs/
├── backend/
│   ├── app/
│   │   ├── modules/          # Domain Logic (Billing, Results, Reports)
│   │   ├── core/             # Framework Config (DB, Security)
│   │   ├── templates/        # Jinja2 HTML Templates for Reports
│   │   └── main.py           # App Entrypoint
│   ├── migrations/           # SQL Schema Files (001 to 007)
│   └── tests/                # Pytest Suite
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router Pages
│   │   │   ├── dashboard/    # Staff Interfaces (Reception, Tech, Path)
│   │   │   ├── portal/       # Patient Interfaces
│   │   │   └── (marketing)/  # Public Lab Profiles
│   │   ├── modules/          # React Components by Feature
│   │   └── lib/              # Utils (API Client, Formatters)
└── README.md                 # You are here
```

---
**19 Labs: Accuracy at the Speed of Light.**
*System Architected & Generated by Antigravity AI.*
