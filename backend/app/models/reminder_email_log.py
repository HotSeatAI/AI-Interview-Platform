from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database.database import Base


class ReminderEmailLog(Base):
    """
    Records every reminder email sent to a user (inactivity tiers,
    unfinished-session/stalled-analysis nudges). Used by
    scripts/send_reminder_emails.py to cap sends to 1 per user per
    2 days and to avoid re-nudging the same unfinished session or
    stalled analysis more than once.
    """

    __tablename__ = "reminder_email_log"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    reminder_type = Column(
        String,
        nullable=False
    )

    # Only set for row-specific event nudges (unfinished_session ->
    # interview_sessions.id, stalled_resume_analysis ->
    # resume_analyses.id) - lets the script dedupe per stuck row
    # instead of per user+type. Null for the time-tier reminders,
    # which are deduped per user+type+streak instead.
    target_id = Column(
        Integer,
        nullable=True
    )

    sent_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    user = relationship("User")
