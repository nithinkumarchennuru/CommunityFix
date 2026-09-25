# CommunityFix — Full-Stack Application

CommunityFix is a community issue tracking and resolution platform.

## Current Stage: Phase 1 — Project Setup & Environment Verification
Phase 1 establishes the full-stack foundation, configuration structures, and diagnostic endpoints. Business logic, authentication, worker assignment, and notifications are intentionally deferred to Phase 2.

---

## Architecture Overview

* **Frontend**: React 19, Tailwind CSS v4, Vite 8
* **Backend**: Python 3.13, Flask 3.1, Flask-SQLAlchemy, PyMySQL, Flask-CORS
* **Database**: MySQL 8.0 (`communityfix_db`)
* **Development Environment**: VS Code / Antigravity IDE

---

## Project Structure

```
communityfix/
├── .env.example               # Full-stack environment template
├── .gitignore                 # Excludes .env, venvs, node_modules, dist
├── README.md                  # Project documentation
├── backend/
│   ├── app/
│   │   ├── __init__.py        # Flask create_app factory with CORS
│   │   ├── config.py          # Config classes loaded from .env
│   │   ├── database.py        # SQLAlchemy instance & test_database_connection
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py      # /api/health, /api/ping, /api/db/test
│   ├── tests/
│   │   └── test_health.py     # Pytest unit tests for API endpoints
│   ├── pytest.ini             # Pytest configuration
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Development backend server
│   ├── test_db_connection.py  # Standalone CLI MySQL connection tester
│   ├── .env.example           # Backend environment template
│   └── .env                   # Local backend secrets (gitignored)
└── frontend/
    ├── public/
    ├── src/
    │   ├── App.jsx            # Interactive verification dashboard
    │   ├── index.css          # Tailwind CSS directives
    │   └── main.jsx           # React root
    ├── index.html             # HTML entry point with metadata
    ├── package.json           # Frontend dependencies & scripts
    ├── vite.config.js         # Vite configuration with Tailwind CSS plugin
    ├── .env.example           # Frontend environment template
    └── .env                   # Local frontend variables (gitignored)
```

---

## Getting Started

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your MySQL DB_PASSWORD

# Test MySQL connection
python test_db_connection.py

# Run unit tests
pytest

# Start Flask dev server (Port 5000)
python run.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start Vite dev server (Port 5173)
npm run dev
```

---

## Health & Diagnostic Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and endpoint directory |
| `GET` | `/api/health` | Comprehensive health check and MySQL status |
| `GET` | `/api/ping` | Fast latency ping endpoint (`{"message": "pong"}`) |
| `GET` | `/api/db/test` | Dedicated MySQL connection diagnostic |

---

## Security & Best Practices

* Passwords and credentials are never hardcoded.
* `.env` is excluded from version control via `.gitignore`.
* CORS is restricted to local frontend development origins (`http://localhost:5173`).
