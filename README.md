# 🚀 Hot Seat – AI-Powered Interview Preparation Platform

<p align="center">
An AI-powered interview preparation platform that simulates real interviews using Generative AI — upload a resume, generate personalized questions, answer with voice, text, or code, and get evidence-grounded AI feedback.
</p>

<p align="center">

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Gemini](https://img.shields.io/badge/Google-Gemini-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

</p>

<p align="center">
<b>Live App:</b> <a href="https://hotseatai.vercel.app">HotSeat</a> &nbsp;|&nbsp;
<b>API Docs:</b> <a href="https://interview-backend-5u2z.onrender.com/docs">HotSeat-backend</a>
</p>

---

## 📸 Screenshots

| Dashboard | Generate Interview |
|---|---|
| ![Dashboard](assets/screenshots/dashboard.png) | ![Generate Interview](assets/screenshots/generate-interview.png) |

| Resume ↔ JD Matching | Interview History |
|---|---|
| ![Resume JD Matching](assets/screenshots/resume-jd.png) | ![Interview History](assets/screenshots/history.png) |

---

## 📖 Overview

Hot Seat behaves like an intelligent interviewer — generating role-specific interviews, asking adaptive follow-up questions, and evaluating responses with Generative AI — across **Software Engineering, Finance, Consulting, Sales, and Marketing**.

---

## ✨ Features

**Authentication** — JWT + Google OAuth, email verification, forgot/reset password, smart account linking.

**Resume Management** — PDF upload with layout-aware parsing (correct reading order across multi-column resumes), hidden-text/prompt-injection filtering, hyperlink extraction.

**Resume ↔ JD Matching (Resume Intelligence)** — a hybrid matching engine built to avoid the score volatility common in typical ATS tools:
- Deterministic first pass (exact/alias/fuzzy matching) — same input always gives the same result, no AI call needed.
- Scoped LLM second pass only for genuinely ambiguous requirements, in bounded batches with pinned temperature.
- Evidence-grounded citations — LLM claims are checked against real resume content before being trusted.
- Adjacency-aware scoring (e.g. Azure vs. AWS) and domain-general matching (not just tech roles).
- Truth-safe AI resume recommendations — never suggests unverifiable claims.
- JD input via text, PDF, or image (OCR).

**AI Interview Engine** — multi-domain generation, difficulty selection, context-aware follow-up questions when an answer scores low.

**Coding Environment** — Monaco editor, compile & run, sample + hidden test cases, AI code evaluation. Supports C, C++, Java, Python, JavaScript, Verilog.

**Hybrid Answers** — combine voice, text, and code into one AI-evaluated response.

**Interview History** — revisit past questions, answers, scores, and feedback.

---

## 🛠 Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React, Vite, React Router, Monaco Editor |
| Backend | FastAPI, SQLAlchemy, Alembic, JWT |
| AI | Google Gemini (`google-genai`) |
| Database | PostgreSQL (Neon) |
| Email | Brevo |
| DevOps | Docker, Docker Compose, Render, Vercel |

---

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/HotSeatAI/AI-Interview-Platform.git
cd AI-Interview-Platform/backend
touch .env
```

Fill in `.env`:

```env
DATABASE_URL=postgresql://interview_user_official:YOUR_PASSWORD@postgres:5432/interview_db
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=180

# Comma-separated — auto-rotates on rate limits (429) and retries on
# transient unavailability (503) before rotating, useful on free tier.
GEMINI_API_KEYS=YOUR_GEMINI_KEY_1,YOUR_GEMINI_KEY_2
GEMINI_MODEL=gemini-3.6-flash

GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
FRONTEND_URL=http://localhost:3000

BREVO_API_KEY=YOUR_BREVO_API_KEY
SENDER_NAME=Hot Seat
SENDER_EMAIL=YOUR_SENDER_EMAIL
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Get a Gemini key at [aistudio.google.com](https://aistudio.google.com/) and a Google OAuth client ID at [console.cloud.google.com](https://console.cloud.google.com/) (Authorized origins: `http://localhost:3000`).

Then, from the project root:

```bash
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend → http://localhost:8000
- API Docs → http://localhost:8000/docs

> Never commit your `.env` file or expose API keys publicly.

### Running without Docker

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

### Database Migrations

```bash
alembic revision --autogenerate -m "migration_name"   # create
alembic upgrade head                                   # apply
alembic downgrade -1                                    # rollback
```

---

## 🔌 API Overview

| Resource | Endpoints |
|---|---|
| Auth | `POST /signup` · `POST /login` · `POST /auth/google` · `GET /auth/verify-email` · `POST /auth/resend-verification` · `POST /auth/forgot-password` · `POST /auth/reset-password` · `GET /me` |
| Resume | `POST /resume/upload` · `GET /resume` · `DELETE /resume/{id}` |
| Resume ↔ JD Matching | `POST /resume-analysis/start` · `GET /resume-analysis/history` · `GET /resume-analysis/{id}/status` · `GET /resume-analysis/{id}/result` |
| Interview | `POST /interview/generate-questions` · `GET /interview/history` |
| Answers | `POST /answer` · `GET /answer/session/{id}/results` |
| Code | `POST /code/run` |

Full interactive docs: `/docs` (Swagger) or `/openapi.json`.

---

## 🌍 Deploying Your Own Instance

**Backend (Render)** — new Web Service, root dir `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and set the env vars listed above.

**Frontend (Vercel)** — import repo, root dir `frontend`, set `VITE_API_URL` and `VITE_GOOGLE_CLIENT_ID`.

---

## 🛣️ Roadmap

- [ ] Resume ↔ JD analysis caching (idempotent re-runs on unchanged input)
- [ ] Per-analysis model/prompt version tracking
- [ ] AI code review
- [ ] Skill dashboard & performance trends
- [ ] Company-specific interview packs
- [ ] Recruiter / institute dashboards

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature-name
git commit -m "Add feature"
git push origin feature/your-feature-name
```

Then open a Pull Request.

---

## 👨‍💻 Author

**Harshal Shah** — B.E. Computer Science, BITS Pilani, Hyderabad Campus

[GitHub](https://github.com/HarshalShah0508) · [LinkedIn](https://www.linkedin.com/in/harshal-anand-shah)

---

<p align="center">
⭐ Star this repo if you found it useful — built with React, FastAPI, PostgreSQL, Docker, and Google Gemini.
</p>
