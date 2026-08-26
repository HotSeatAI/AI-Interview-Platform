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