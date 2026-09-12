from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from datetime import datetime

from app.database.database import Base


class InterviewSession(Base):

    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    difficulty = Column(
        String,
        nullable=False
    )

    # Which round of a Software Engineering interview this session is
    # scoped to (e.g. "round_1", "round_2", "round_3" - see
    # software_rounds.ROUND_KEYS), or "full" for the legacy
    # all-in-one interview. Null for any session created before this
    # column existed, and for every non-software domain.
    round = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Set only for a weak-topic practice round (see api/topics.py) -
    # links back to the UserTopic it's resolving. Null for normal
    # interviews. Read at finish time (finish_interview) to decide
    # pass/fail and delete the resolved topic.
    practice_topic_id = Column(
        Integer,
        ForeignKey("user_topics.id"),
        nullable=True
    )

    # Set only when the user actually clicks "Finish Interview" - not
    # derived from answered-question counts, since finishing with
    # unanswered/skipped questions left is an intentional, allowed
    # path (see InterviewSessionPage.handleFinishInterview's confirm
    # dialog). Used to warn on the results page when someone reaches
    # it (e.g. via History) without ever finishing.
    finished_at = Column(
        DateTime,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="interview_sessions"
    )
    questions = relationship(
    "Question",
    back_populates="session",
    cascade="all, delete-orphan"
    )