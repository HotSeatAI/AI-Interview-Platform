from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String,
        nullable=True
    )

    google_id = Column(
        String,
        unique=True,
        nullable=True
    )

    auth_provider = Column(
        String(20),
        nullable=False,
        default="local"
    )

    email_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    role = Column(
        String,
        nullable=False,
        default="user"
    )

    # Aggregate weak-topic-practice counters, driving the progress
    # circle on the Topics page. Live here (not on UserTopic) because
    # UserTopic rows are deleted the moment a topic is resolved -
    # these must survive that deletion. See api/topics.py.
    weak_topics_flagged_total = Column(
        Integer,
        nullable=False,
        default=0
    )

    weak_topics_resolved_total = Column(
        Integer,
        nullable=False,
        default=0
    )

    resumes = relationship(
        "Resume",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    interview_sessions = relationship(
        "InterviewSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    verification_tokens = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )