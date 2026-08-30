from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.auth import get_current_user

from app.models.user import User
from app.models.resume import Resume
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.models.resume_analysis import ResumeAnalysis

ACTIVITY_WINDOW_DAYS = 371  # 53 full weeks, for a clean heatmap grid

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    latest_resume = (
        resumes[0].original_filename
        if resumes
        else None
    )

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

    completed = 0
    in_progress = 0

    for session in sessions:

        total_questions = len(session.questions)

        answered = sum(
            1
            for question in session.questions
            if question.answer
        )

        if total_questions > 0 and answered == total_questions:
            completed += 1
        else:
            in_progress += 1

    latest_interview = None

    if sessions:
        latest_interview = {
            "role": sessions[0].role,
            "difficulty": sessions[0].difficulty,
            "created_at": sessions[0].created_at,
        }

    cutoff = datetime.utcnow() - timedelta(days=ACTIVITY_WINDOW_DAYS)

    interview_counts = (
        db.query(
            cast(InterviewSession.created_at, Date).label("day"),
            func.count(),
        )
        .filter(
            InterviewSession.user_id == current_user.id,
            InterviewSession.created_at >= cutoff,
        )
        .group_by("day")
        .all()
    )

    tailoring_counts = (
        db.query(
            cast(ResumeAnalysis.created_at, Date).label("day"),
            func.count(),
        )
        .filter(
            ResumeAnalysis.user_id == current_user.id,
            ResumeAnalysis.created_at >= cutoff,
        )
        .group_by("day")
        .all()
    )

    # "Activity" is deliberately just these two actions (generating an
    # interview, running a resume-JD tailoring) - not every possible
    # user action (e.g. answering individual questions).
    activity_by_day = defaultdict(int)

    for day, count in interview_counts:
        activity_by_day[day] += count

    for day, count in tailoring_counts:
        activity_by_day[day] += count

    activity = [
        {"date": day.isoformat(), "count": count}
        for day, count in sorted(activity_by_day.items())
    ]

    return {
        "username": current_user.username,
        "email": current_user.email,
        "latest_resume": latest_resume,
        "total_interviews": len(sessions),
        "completed_interviews": completed,
        "in_progress_interviews": in_progress,
        "latest_interview": latest_interview,
        "activity": activity,
    }