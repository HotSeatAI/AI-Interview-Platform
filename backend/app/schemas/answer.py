from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel


class AnswerCreate(BaseModel):
    question_id: int

    voice_text: Optional[str] = None
    # TODO(backend migration): the frontend's "Additional Notes" box was
    # merged into the voice/explanation textarea, so this is always sent
    # empty now. Drop this field (and the matching Answer.typed_text
    # column, via Alembic) once nothing relies on it.
    typed_text: Optional[str] = None
    code: Optional[str] = None


class FollowUpQuestionResponse(BaseModel):
    question_id: int
    question_text: str
    follow_up_depth: int


class AnswerResponse(BaseModel):
    answer_id: int

    score: int
    feedback: str
    strengths: List[str]
    improvements: List[str]

    has_follow_up: bool
    follow_up: Optional[FollowUpQuestionResponse] = None


class AnswerDetail(BaseModel):
    id: int
    question_id: int

    voice_text: Optional[str]
    typed_text: Optional[str]  # TODO(backend migration): see AnswerCreate.typed_text above.
    code: Optional[str]

    combined_answer: str

    score: int
    feedback: str
    strengths: List[str]
    improvements: List[str]

    created_at: datetime

    class Config:
        from_attributes = True


class SkippedQuestionInfo(BaseModel):
    question_number: int
    topic: str


class SessionResultsResponse(BaseModel):
    session_id: int
    average_score: float
    questions_attempted: int
    strong_topics: List[str]
    weak_topics: List[str]
    skipped_questions: List[SkippedQuestionInfo] = []