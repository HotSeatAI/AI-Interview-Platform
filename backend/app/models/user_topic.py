from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database.database import Base


class UserTopic(Base):
    """
    A weak topic currently flagged for this user, awaiting practice.
    Deliberately has no status/score history - a row is deleted the
    moment it's resolved (pass or fail), see api/interview.py's
    finish_interview. Long-term progress lives on User instead
    (weak_topics_flagged_total / weak_topics_resolved_total).
    """

    __tablename__ = "user_topics"

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

    topic = Column(
        String,
        nullable=False
    )

    times_flagged = Column(
        Integer,
        nullable=False,
        default=1
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship("User")
