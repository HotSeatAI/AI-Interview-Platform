from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
import re
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.api.auth import get_current_user

from app.models.user import User
from app.models.resume import Resume
from app.models.interview_session import InterviewSession
from app.models.question import Question

from app.schemas.interview import GenerateQuestionsRequest
from app.schemas.interview import InterviewDetailResponse
from app.schemas.interview import InterviewHistoryItem

from app.services.ai_service import AIService
from app.services.api_key_manager import (
    clear_gemini_context,
    set_gemini_context,
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


@router.post("/generate-questions")
def generate_questions(
    request: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    resume_text = None

    if request.resume_id is not None:

        resume = (
            db.query(Resume)
            .filter(
                Resume.id == request.resume_id,
                Resume.user_id == current_user.id
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Selected resume not found."
            )

        resume_text = resume.extracted_text

    # Session is created BEFORE generation (rather than after,
    # as it previously was) so its id exists in time to tag the
    # Gemini call for LangFuse session grouping. If generation
    # fails, the empty session row is deleted in the except
    # block below so a failed attempt never leaves orphaned
    # session clutter behind.
    session = InterviewSession(
        user_id=current_user.id,
        role=request.role,
        difficulty=request.difficulty
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    ai_service = AIService()

    set_gemini_context(session.id)

    try:
        questions = ai_service.generate_questions(
            resume_text=resume_text,
            role=request.role,
            difficulty=request.difficulty
        )
    except Exception as exc:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail=(
                "The interview AI service is temporarily "
                "unavailable. Please try again in a moment."
            ),
        ) from exc
    finally:
        clear_gemini_context()

    question_list = re.findall(
        r'^\d+\..*?(?=^\d+\.|\Z)',
        questions,
        flags=re.MULTILINE | re.DOTALL,
    )

    question_list = [
        question.strip()
        for question in question_list
    ]

    print("QUESTIONS FOUND:")
    print(len(question_list))

    for question_text in question_list:
        question = Question(
            session_id=session.id,
            question_text=question_text
        )
        db.add(question)

    db.commit()

    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "questions_saved": len(question_list),
        "questions": questions
    }


@router.get(
    "/history",
    response_model=list[InterviewHistoryItem]
)
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == current_user.id
        )
        .order_by(
            InterviewSession.created_at.desc()
        )
        .all()
    )

    history = []

    for session in sessions:
        history.append(
            {
                "session_id": session.id,
                "role": session.role,
                "difficulty": session.difficulty,
                "created_at": session.created_at
            }
        )

    return history


@router.get(
    "/{session_id}",
    response_model=InterviewDetailResponse
)
def get_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    questions = (
        db.query(Question)
        .filter(Question.session_id == session.id)
        .all()
    )

    question_list = []

    for question in questions:

        if question.answer:
            question_list.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "answered": True,
                    "score": question.answer.score,
                    "feedback": question.answer.feedback,
                    "strengths": question.answer.strengths,
                    "improvements": question.answer.improvements,
                }
            )

        else:
            question_list.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "answered": False,
                    "score": None,
                    "feedback": None,
                    "strengths": [],
                    "improvements": [],
                }
            )

    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "created_at": session.created_at,
        "questions": question_list,
    }