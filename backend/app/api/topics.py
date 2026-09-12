import re

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.database.database import get_db
from app.api.auth import get_current_user

from app.models.user import User
from app.models.user_topic import UserTopic
from app.models.interview_session import InterviewSession
from app.models.question import Question

from app.services.ai_service import AIService
from app.services.api_key_manager import (
    clear_gemini_context,
    set_gemini_context,
)

router = APIRouter(
    prefix="/topics",
    tags=["Weak Topic Practice"]
)


@router.get("")
def get_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topics = (
        db.query(UserTopic)
        .filter(UserTopic.user_id == current_user.id)
        .order_by(UserTopic.times_flagged.desc(), UserTopic.created_at.desc())
        .all()
    )

    flagged_total = current_user.weak_topics_flagged_total
    resolved_total = current_user.weak_topics_resolved_total

    progress_pct = (
        round((resolved_total / flagged_total) * 100)
        if flagged_total
        else 0
    )

    return {
        "topics": [
            {
                "id": topic.id,
                "topic": topic.topic,
                "times_flagged": topic.times_flagged,
            }
            for topic in topics
        ],
        "flagged_total": flagged_total,
        "resolved_total": resolved_total,
        "progress_pct": progress_pct,
    }


@router.post("/{topic_id}/practice")
@limiter.limit("15/minute")
def start_topic_practice(
    request: Request,
    response: Response,
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topic = (
        db.query(UserTopic)
        .filter(
            UserTopic.id == topic_id,
            UserTopic.user_id == current_user.id,
        )
        .first()
    )

    if not topic:
        raise HTTPException(
            status_code=404,
            detail="Topic not found."
        )

    # Session created before generation (same reasoning as
    # generate_questions - the id needs to exist in time to tag the
    # Gemini call, and a failed generation deletes the empty session
    # below rather than leaving orphaned clutter).
    session = InterviewSession(
        user_id=current_user.id,
        role=f"Practice: {topic.topic}",
        difficulty="medium",
        practice_topic_id=topic.id,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    ai_service = AIService()

    set_gemini_context(session.id)

    try:
        questions_text = ai_service.generate_topic_questions(topic.topic)
    except Exception as exc:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail=(
                "The practice question service is temporarily "
                "unavailable. Please try again in a moment."
            ),
        ) from exc
    finally:
        clear_gemini_context()

    # Identical parsing to api/interview.py's generate_questions - the
    # prompt is deliberately written to produce the same numbered-list
    # format so this stays in lockstep with zero new parsing logic.
    question_list = re.findall(
        r'^\d+\..*?(?=^\d+\.|\Z)',
        questions_text,
        flags=re.MULTILINE | re.DOTALL,
    )

    question_list = [question.strip() for question in question_list]

    coding_type_pattern = re.compile(
        r'[ \t]*TYPE:\s*CODING[ \t]*\n*',
        flags=re.IGNORECASE,
    )

    for question_text in question_list:

        match = coding_type_pattern.search(question_text)

        if match:
            question_type = "coding"
            question_text = coding_type_pattern.sub('\n', question_text, count=1)
            question_text = re.sub(r'\n{3,}', '\n\n', question_text).strip()
        else:
            question_type = None

        db.add(
            Question(
                session_id=session.id,
                question_text=question_text,
                question_type=question_type,
            )
        )

    db.commit()

    return {"session_id": session.id}
