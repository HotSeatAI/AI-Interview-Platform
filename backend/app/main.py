from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ALLOWED_ORIGINS
from app.database.database import Base, engine

from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.interview import router as interview_router
from app.api.answer import router as answer_router
from app.api.dashboard import router as dashboard_router
from app.api import code
from app.api.resume_analysis import (
    router as resume_analysis_router
)
from app.api.topics import router as topics_router
from app.models.resume_analysis import (
    ResumeAnalysis
)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(answer_router)
app.include_router(dashboard_router)
app.include_router(code.router)
app.include_router(resume_analysis_router)
app.include_router(topics_router)