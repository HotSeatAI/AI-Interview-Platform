from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import JSON

from sqlalchemy.orm import relationship

from app.database.database import Base


class Answer(Base):

    __tablename__ = "answers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        unique=True,
        nullable=False
    )

    # Hybrid Interview Inputs
    voice_text = Column(
        Text,
        nullable=True
    )

    # TODO(backend migration): always empty from the frontend now — see
    # the TODO on AnswerCreate.typed_text in schemas/answer.py. Drop this
    # column via Alembic once nothing relies on it.
    typed_text = Column(
        Text,
        nullable=True
    )

    code = Column(
        Text,
        nullable=True
    )

    # Final answer sent to Gemini
    combined_answer = Column(
        Text,
        nullable=False
    )

    score = Column(
        Integer,
        nullable=False
    )

    feedback = Column(
        Text,
        nullable=False
    )

    strengths = Column(
        JSON,
        nullable=False
    )

    improvements = Column(
        JSON,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    question = relationship(
        "Question",
        back_populates="answer"
    )