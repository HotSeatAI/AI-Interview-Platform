from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
import re
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.database.database import get_db

from app.api.auth import get_current_user

from app.models.user import User
from app.models.resume import Resume
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.models.user_topic import UserTopic

from app.schemas.interview import GenerateQuestionsRequest
from app.schemas.interview import InterviewDetailResponse
from app.schemas.interview import InterviewHistoryItem
from app.schemas.interview import RoundDiscoveryResponse

from app.services.ai_service import AIService
from app.services.api_key_manager import (
    clear_gemini_context,
    set_gemini_context,
)
from app.services.role_classifier import (
    RoleClassifier,
    classify_software_subrole,
    classify_finance_subrole,
    classify_consulting_subrole,
)
from app.services.prompts.software_rounds import (
    get_rounds_for_subrole as get_software_rounds_for_subrole,
)
from app.services.prompts.finance_rounds import (
    get_rounds_for_subrole as get_finance_rounds_for_subrole,
)
from app.services.prompts.consulting_rounds import (
    get_rounds_for_subrole as get_consulting_rounds_for_subrole,
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


@router.post("/generate-questions")
@limiter.limit("15/minute")
def generate_questions(
    request: Request,
    response: Response,
    payload: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    resume_text = None

    if payload.resume_id is not None:

        resume = (
            db.query(Resume)
            .filter(
                Resume.id == payload.resume_id,
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
        role=payload.role,
        difficulty=payload.difficulty
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    ai_service = AIService()

    set_gemini_context(session.id)

    try:
        questions, applied_round = ai_service.generate_questions(
            resume_text=resume_text,
            role=payload.role,
            difficulty=payload.difficulty,
            round=payload.round,
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

    session.round = applied_round
    db.add(session)

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

    # Gemini is instructed to place "TYPE: CODING" immediately
    # after the question number, but in practice sometimes writes
    # a lead-in sentence first and puts the tag on its own line
    # further down. Searching for the tag anywhere in the chunk
    # (rather than anchoring to the start) tolerates that drift.
    # The matched span is replaced with a single newline (not
    # deleted outright) so the text on either side of the tag
    # never gets glued together, then any resulting run of blank
    # lines is collapsed back down.
    coding_type_pattern = re.compile(
        r'[ \t]*TYPE:\s*CODING[ \t]*\n*',
        flags=re.IGNORECASE,
    )

    for question_text in question_list:

        match = coding_type_pattern.search(question_text)

        if match:
            question_type = "coding"
            question_text = coding_type_pattern.sub(
                '\n', question_text, count=1
            )
            question_text = re.sub(
                r'\n{3,}', '\n\n', question_text
            ).strip()
        else:
            question_type = None

        question = Question(
            session_id=session.id,
            question_text=question_text,
            question_type=question_type,
        )
        db.add(question)

    db.commit()

    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "round": session.round,
        "questions_saved": len(question_list),
        "questions": questions
    }


@router.get(
    "/rounds",
    response_model=RoundDiscoveryResponse
)
@limiter.limit("30/minute")
def get_interview_rounds(
    request: Request,
    response: Response,
    role: str,
    current_user: User = Depends(get_current_user),
):
    """
    Given a free-text role, returns the interview rounds a candidate
    can choose from - only for domains that have round support
    (currently Software Engineering, Finance, and Consulting). Every
    other domain returns an empty rounds list.
    """

    domain = RoleClassifier().classify_role(role)

    if domain == "software":
        subrole = classify_software_subrole(role)
        return {
            "domain": domain,
            "subrole": subrole,
            "rounds": get_software_rounds_for_subrole(subrole),
        }

    if domain == "finance":
        subrole = classify_finance_subrole(role)
        return {
            "domain": domain,
            "subrole": subrole,
            "rounds": get_finance_rounds_for_subrole(subrole),
        }

    if domain == "consulting":
        subrole = classify_consulting_subrole(role)
        return {
            "domain": domain,
            "subrole": subrole,
            "rounds": get_consulting_rounds_for_subrole(subrole),
        }

    return {"domain": domain, "subrole": None, "rounds": []}


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
                "round": session.round,
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
        .order_by(Question.id)
        .all()
    )

    question_list = []

    for question in questions:

        if question.answer:
            question_list.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
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
                    "question_type": question.question_type,
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
        "round": session.round,
        "created_at": session.created_at,
        "questions": question_list,
    }


@router.post("/{session_id}/finish")
def finish_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marks a session as finished - called when the user clicks
    "Finish Interview". Deliberately NOT derived from answered-question
    counts (finishing with unanswered questions left is an intentional,
    allowed path) - see InterviewSession.finished_at. Idempotent.

    If this session is a weak-topic practice round
    (practice_topic_id set - see api/topics.py), this is also where
    it gets resolved: pass or fail, the linked UserTopic row is
    deleted either way; a pass additionally credits the user's
    lifetime resolved counter (the progress circle on the Topics
    page). Resolution only runs on the first finish (guarded by the
    same finished_at is None check) so re-finishing never double-counts.
    """

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

    if session.finished_at is None:
        session.finished_at = datetime.utcnow()

        if session.practice_topic_id is not None:

            questions = (
                db.query(Question)
                .filter(Question.session_id == session.id)
                .all()
            )

            answers = [q.answer for q in questions if q.answer]

            # Per-question, not averaged - every one of the 3 must
            # score above 5 to pass.
            passed = len(answers) == 3 and all(
                answer.score > 5 for answer in answers
            )

            if passed:
                current_user.weak_topics_resolved_total += 1

            topic = (
                db.query(UserTopic)
                .filter(UserTopic.id == session.practice_topic_id)
                .first()
            )

            if topic:
                db.delete(topic)

        db.commit()

    return {"finished": True}