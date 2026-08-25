from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database.database import Base


class Question(Base):

    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        nullable=False
    )

    question_text = Column(
        Text,
        nullable=False
    )

    question_type = Column(
        Text,
        nullable=True
    )

    is_follow_up = Column(
        Boolean,
        nullable=False,
        default=False
    )

    parent_question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=True
    )

    follow_up_depth = Column(
        Integer,
        nullable=False,
        default=0
    )

    session = relationship(
        "InterviewSession",
        back_populates="questions"
    )

    answer = relationship(
        "Answer",
        back_populates="question",
        uselist=False
    )