from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
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

    # Post-login profile capture. Columns stay nullable at the DB
    # level (existing rows have none of these); "mandatory" fields
    # are enforced by the ProfileUpdate schema, not a DB constraint.
    # profile_completed flips true once that schema has been
    # satisfied once, via PUT /me/profile - it is what ProtectedRoute
    # checks to force the complete-profile page on next login.
    full_name = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    institute_name = Column(String, nullable=True)
    year_of_passout = Column(Integer, nullable=True)
    job_domains = Column(ARRAY(String), nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    years_of_experience = Column(Float, nullable=True)
    profile_completed = Column(Boolean, nullable=False, default=False)

    # Terms & Conditions acceptance, gated the same way as
    # profile_completed - required after the profile form, via
    # PUT /me/accept-terms. See ProtectedRoute on the frontend.
    terms_accepted = Column(Boolean, nullable=False, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)

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

    email_change_tokens = relationship(
        "EmailChangeToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )