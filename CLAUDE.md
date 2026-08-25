# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Hot Seat is an AI interview preparation platform: FastAPI backend + React/Vite frontend + PostgreSQL, using Google Gemini for interview generation, answer evaluation, and resume-vs-job-description analysis. See `README.md` for the full feature list, `Future Features.md` for the roadmap, and `CONVENTIONS.md` for commit message conventions.

## Commands

### Backend (`backend/`)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000, docs at /docs
```

Requires `backend/.env` (see `backend/.env.example`) — the app raises `ValueError` at import time if `GOOGLE_CLIENT_ID` or `GEMINI_API_KEYS` is missing, so it will not start without them. Migrations use standard Alembic commands.

There is no test suite in this repo yet (no pytest config, no `tests/` directory).

### Frontend (`frontend/`)

Standard npm scripts (`install`/`dev`/`build`/`lint`, see `package.json`). Requires `frontend/.env` with `VITE_API_BASE_URL` and `VITE_GOOGLE_CLIENT_ID`.

### Full stack (Docker)

```bash
docker compose up --build
```

Starts Postgres, backend (`:8000`), and frontend (`:3000`, nginx-served build) together. The backend image also installs gcc/g++, a JDK, Node, and `iverilog` — these are runtime toolchains for the in-browser code execution feature (see below), not backend build dependencies.

## Architecture

**Backend** (`backend/app/`): FastAPI routers in `api/` (`auth`, `resume`, `interview`, `answer`, `dashboard`, `code`, `resume_analysis`), each paired with SQLAlchemy models in `models/` and Pydantic schemas in `schemas/`. Business logic lives in `services/`, not in the routers.

**Two independent Gemini-backed pipelines**, both funneling through `services/api_key_manager.py`:

1. **Interview generation & evaluation** (`ai_service.py`): `RoleClassifier` buckets a requested role into a domain (software / finance / consulting / sales / marketing, plus software sub-domains like VLSI/embedded in `services/prompts/`), then dispatches to a domain-specific prompt builder. Each domain has its own prompt module in `services/prompts/` — this is the "modular prompt architecture" the README refers to. Evaluation and adaptive follow-up questions (triggered when a score falls below `FOLLOW_UP_SCORE_THRESHOLD` in `core/config.py`) go through `build_evaluation_prompt` / `build_follow_up_prompt`.

2. **Resume-vs-job-description analysis** (`api/resume_analysis.py` + `services/resume_analysis_worker.py`): `POST /resume-analysis/start` parses the JD synchronously (needed before the request returns), creates a `ResumeAnalysis` row with `status="processing"`, then runs the actual analysis via FastAPI `BackgroundTasks`. The worker chains several single-purpose services in sequence — `job_description_parser` → `resume_analyzer` → `requirement_matcher` (the largest service in the codebase) → `evidence_validator` → `semantic_verifier` → `recommendation_engine` / `resume_optimizer` — updating `progress`/`current_stage` on the row as it goes so the frontend can poll `GET /resume-analysis/{id}/status`. `role_classifier.py` is shared between both pipelines.

`services/api_key_manager.py` rotates across multiple comma-separated `GEMINI_API_KEYS` and (via `contextvars`) tags every Gemini call with the resume-analysis job it belongs to, for per-analysis call-count telemetry — without threading an `analysis_id` through every function signature.

**Code execution** (`api/code.py` + `services/execution_service.py`): runs submitted C/C++/Java/Python/JavaScript/Verilog code via `subprocess` directly in the backend container (not a separate sandboxed container). `execution_service.py` passes subprocesses an explicit **environment allowlist** rather than the default inherited environment — without it, user-submitted code could read and print back `GEMINI_API_KEYS`, `SECRET_KEY`, `DATABASE_URL`, etc. Keep that allowlist model in mind (extend it, don't remove it) if you touch this file.

**Auth**: JWT (`utils/jwt_handler.py`) plus Google OAuth (`services/oauth_service.py`) with "smart account linking" — a Google login can attach to an existing local-password account by email. Email verification (`services/email_verification_service.py`, Brevo for delivery) gates login for local accounts only; Google accounts skip it. Password reset follows the same signed-token pattern (`models/password_reset_token.py`, `services/password_reset_service.py`).

**Frontend** (`frontend/src/`): routes defined centrally in `router.jsx`, not per-page. `context/AuthContext.jsx` holds auth state; `context/ResumeAnalysisContext.jsx` (wrapping the whole app in `App.jsx`) holds in-progress resume-analysis polling state so it survives navigation. API calls are grouped one-file-per-domain in `src/api/` (`authApi.js`, `interviewApi.js`, `resumeAnalysisApi.js`, ...), all built on the shared `axios` instance in `src/api/client.js` (`baseURL` from `VITE_API_BASE_URL`). The coding environment uses `@monaco-editor/react`.

## Notes for local dev

- The repo is currently checked out as a **shallow clone** — full history hasn't been fetched yet.
- Cloning/fetching over SSH (`git@github.com:...`) has been observed to hang indefinitely on some networks; HTTPS works reliably as a fallback.
- `frontend/.env.production` (committed) shows the real deployed API URL and Google OAuth client ID — useful as a reference for what `frontend/.env` needs locally.
- The Google OAuth client ID's authorized JavaScript origins are configured in Google Cloud Console, outside this repo; `localhost:5173` may not be registered on it, which would make "Sign in with Google" fail locally even against the live backend.
- The deployed backend (`interview-backend-5u2z.onrender.com`) is on Render's free tier, which spins the service down after a period of inactivity. The first request after it's been idle will be slow (the container has to cold-start) — this is expected, not a bug, when testing the frontend against the live backend instead of a local one.
