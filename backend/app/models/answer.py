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

    # Delivery/body-language signals - numeric only (pause counts,
    # eye-contact percentage, etc), computed client-side from raw
    # audio/video characteristics. Deliberately NEVER derived from
    # or containing transcript text - see delivery_feedback_prompt.py
    # for why (a past bug let mis-transcribed accented speech poison
    # technical-correctness scoring; this column and the prompt that
    # reads it must never repeat that by mixing in transcript content).
    delivery_signals = Column(
        JSON,
        nullable=True
    )

    # Plain-language coaching generated from delivery_signals alone
    # (see ai_service.generate_delivery_feedback) - persisted here so
    # GET /answer/{id} doesn't need to regenerate it.
    delivery_feedback = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    question = relationship(
        "Question",
        back_populates="answer"
    )