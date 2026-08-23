from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False,
        index=True,
    )

    job_description_text = Column(
        Text,
        nullable=True,
    )

    job_title = Column(
        String,
        nullable=True,
    )

    jd_profile_json = Column(
        Text,
        nullable=True,
    )

    jd_text_hash = Column(
        String,
        nullable=True,
        index=True,
    )

    resume_profile_json = Column(
        Text,
        nullable=True,
    )

    analysis_result_json = Column(
        Text,
        nullable=True,
    )

    overall_score = Column(
        Integer,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="processing",
        index=True,
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0,
    )

    current_stage = Column(
        String,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )