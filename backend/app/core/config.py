import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 180)
)

# Rate limiter storage backend (see app/core/rate_limiter.py). Defaults
# to slowapi's in-process memory store - correct for a single backend
# instance. Only needs to become a redis://... URL if this ever runs
# as multiple instances at once, so limits stay shared across them.
RATE_LIMIT_STORAGE_URI = os.getenv(
    "RATE_LIMIT_STORAGE_URI", "memory://"
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    raise ValueError(
        "GOOGLE_CLIENT_ID must be set in the environment."
    )

GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

UPLOAD_DIR = BASE_DIR / "uploads"

RESUME_DIR = UPLOAD_DIR / "resumes"

RESUME_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# -----------------------------
# Gemini Configuration
# -----------------------------

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001",
)

# Structuring calls (JD -> JDProfile, resume -> ResumeProfile) are
# schema-constrained extraction, not the multi-step judgment calls
# semantic verification/recommendations are — capping the model's
# hidden "thinking" budget here cuts a large chunk of billed-but-
# invisible output tokens with no observed completeness/quality
# loss (verified via full field-level diff against default
# thinking on a real JD). gemini-3.6-flash requires a minimum of
# 1 — 0 is rejected outright as an invalid argument.
GEMINI_STRUCTURING_THINKING_BUDGET = int(
    os.getenv("GEMINI_STRUCTURING_THINKING_BUDGET", 128)
)

# Applied to answer_evaluation, interview_question_generation, and
# follow_up_question_generation. Validated live, side by side against
# the default (dynamic/uncapped) thinking budget: evaluate_answer
# matched default scoring/feedback on both a correct answer and a
# deliberately wrong one (same score, same errors caught); the
# follow-up generation cap produced an equally well-formed, on-topic
# question (finish_reason=STOP, not truncated). An earlier test run
# appeared to show a follow-up regression, but that was a confounded
# result from combining this cap with a separate max_output_tokens
# bug (since fixed/reverted) that let thinking tokens starve the
# visible output - re-tested in isolation afterward and it was fine.
# Deliberately NOT applied to generate_model_answer - untested in
# isolation, and no longer on the critical latency path anyway.
GEMINI_INTERVIEW_THINKING_BUDGET = int(
    os.getenv("GEMINI_INTERVIEW_THINKING_BUDGET", 128)
)

# Hard ceiling, in seconds, on how long POST /answer will wait for the
# BONUS Gemini calls (delivery feedback, speculative model answer) -
# measured from when they were fired, not from when this is read, so
# it bounds the whole wave regardless of how much of it evaluate_answer
# itself already used. If a bonus call isn't done by then, it's
# dropped (same "must never block" soft-fail already used for
# exceptions, just extended to timeouts) rather than left to run the
# response time up further - this is what stops a slow/rate-limited
# bonus call from turning one answer submission into a 60-second wait.
# evaluate_answer itself is NOT subject to this - a score can't be
# fabricated, so if Gemini itself is slow, the response is slow.
ANSWER_ENRICHMENT_TIMEOUT_SECONDS = int(
    os.getenv("ANSWER_ENRICHMENT_TIMEOUT_SECONDS", 12)
)

raw_keys = os.getenv("GEMINI_API_KEYS")

GEMINI_API_KEYS = [
    key.strip()
    for key in (raw_keys or "").split(",")
    if key.strip()
]

if not GEMINI_API_KEYS:
    raise ValueError(
        f"At least one Gemini API key must be provided in GEMINI_API_KEYS. Received: {repr(raw_keys)}"
    )

FOLLOW_UP_SCORE_THRESHOLD = 5

# -----------------------------
# LangFuse Configuration (optional)
# -----------------------------
# Tracing is disabled unless both keys are set — no import-time
# failure like GEMINI_API_KEYS/GOOGLE_CLIENT_ID, since observability
# should never block the app from starting.

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")

LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

LANGFUSE_BASE_URL = os.getenv(
    "LANGFUSE_BASE_URL",
    "https://cloud.langfuse.com",
)

GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE = int(
    os.getenv("GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE", 12)
)

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

SENDER_NAME = os.getenv(
    "SENDER_NAME",
    "Hot Seat"
)

SENDER_EMAIL = os.getenv(
    "SENDER_EMAIL"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)

# Base URL of this backend itself - needed for links that point at a
# FastAPI route directly (e.g. the unsubscribe link in reminder
# emails, GET /unsubscribe), as opposed to FRONTEND_URL links that
# point at a React route.
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

# -----------------------------
# CORS Configuration
# -----------------------------
# Comma-separated list of allowed frontend origins. Defaults to
# every origin this app has ever needed (local dev servers, the
# Vercel deploy, the custom domain) so nothing breaks if this is
# left unset - but each deployment should override it with only
# the origins that actually apply there. In particular, the real
# production backend (Render) should set this to just the real
# domains, with no localhost entries, once the custom domain is
# live - trusting localhost in CORS is a normal dev convenience,
# not something a production deployment needs.
_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "https://hotseatai.vercel.app,"
    "https://hotseatai.in,"
    "https://www.hotseatai.in"
)

_raw_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in (
        _raw_cors_origins if _raw_cors_origins else _DEFAULT_CORS_ORIGINS
    ).split(",")
    if origin.strip()
]
