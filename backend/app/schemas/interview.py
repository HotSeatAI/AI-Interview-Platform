from datetime import datetime
from typing import List
from typing import Optional
from pydantic import BaseModel


class GenerateQuestionsRequest(BaseModel):
    resume_id: Optional[int] = None
    role: str
    difficulty: str
    round: Optional[str] = None


class InterviewQuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str | None = None

    answered: bool

    score: int | None = None
    feedback: str | None = None

    strengths: List[str] = []
    improvements: List[str] = []

    class Config:
        from_attributes = True


class InterviewHistoryItem(BaseModel):
    session_id: int
    role: str
    difficulty: str
    round: Optional[str] = None
    created_at: datetime


class InterviewDetailResponse(BaseModel):
    session_id: int
    role: str
    difficulty: str
    round: Optional[str] = None
    created_at: datetime

    questions: List[InterviewQuestionResponse]


class RoundOption(BaseModel):
    key: str
    label: str
    description: str


class RoundDiscoveryResponse(BaseModel):
    domain: str
    subrole: Optional[str] = None
    rounds: List[RoundOption]