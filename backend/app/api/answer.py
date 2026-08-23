import re

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.answer import Answer
from app.models.question import Question
from app.models.interview_session import InterviewSession
from app.models.user import User

from app.schemas.answer import (
    AnswerCreate,
    AnswerResponse,
    AnswerDetail,
    SessionResultsResponse,
    SkippedQuestionInfo,
    FollowUpQuestionResponse,
)

from app.services.ai_service import AIService
from app.services.api_key_manager import (
    clear_gemini_context,
    set_gemini_context,
)

from app.api.auth import get_current_user

from app.core.config import FOLLOW_UP_SCORE_THRESHOLD


router = APIRouter(
    prefix="/answer",
    tags=["Answer Evaluation"]
)


@router.post(
    "",
    response_model=AnswerResponse
)
def submit_answer(
    payload: AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = (
        db.query(Question)
        .filter(Question.id == payload.question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found."
        )

    if question.session.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to answer this question."
        )

    existing_answer = (
        db.query(Answer)
        .filter(Answer.question_id == question.id)
        .first()
    )

    if existing_answer:
        raise HTTPException(
            status_code=400,
            detail="This question has already been answered."
        )

    ai_service = AIService()

    set_gemini_context(question.session_id)

    try:

        try:
            combined_answer = ai_service.build_combined_answer(
                voice_text=payload.voice_text,
                typed_text=payload.typed_text,
                code=payload.code
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        try:
            evaluation = ai_service.evaluate_answer(
                question_text=question.question_text,
                user_answer=combined_answer
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The answer evaluation service is temporarily "
                    "unavailable. Please try submitting again in a "
                    "moment."
                ),
            ) from exc

        answer = Answer(
            question_id=question.id,

            voice_text=payload.voice_text,
            typed_text=payload.typed_text,
            code=payload.code,
            combined_answer=combined_answer,

            score=evaluation["score"],
            feedback=evaluation["feedback"],
            strengths=evaluation["strengths"],
            improvements=evaluation["improvements"],
        )

        db.add(answer)
        db.commit()
        db.refresh(answer)

        follow_up = None
        follow_up_text = None

        if (
            answer.score >= FOLLOW_UP_SCORE_THRESHOLD
            and question.follow_up_depth < 2
        ):

            try:

                follow_up_text = (
                    ai_service.generate_follow_up_question(
                        original_question=question.question_text,
                        candidate_answer=combined_answer,
                        evaluation=evaluation,
                        follow_up_depth=question.follow_up_depth,
                    )
                    .strip()
                )

            except Exception as e:

                print("\n===== FOLLOW-UP GENERATION FAILED =====")
                print(e)

            if follow_up_text:

                follow_up = Question(
                    session_id=question.session_id,
                    question_text=follow_up_text.strip(),
                    is_follow_up=True,
                    parent_question_id=(
                        question.parent_question_id
                        if question.is_follow_up
                        else question.id
                    ),
                    follow_up_depth=question.follow_up_depth + 1,
                )

                db.add(follow_up)
                db.commit()
                db.refresh(follow_up)

                print("\n===== FOLLOW-UP CREATED =====")
                print(f"Parent Question : {question.id}")
                print(f"Depth           : {follow_up.follow_up_depth}")
                print(f"Question        : {follow_up.question_text}")

        return AnswerResponse(
            answer_id=answer.id,
            score=answer.score,
            feedback=answer.feedback,
            strengths=answer.strengths,
            improvements=answer.improvements,
            has_follow_up=follow_up is not None,
            follow_up=(
                FollowUpQuestionResponse(
                    question_id=follow_up.id,
                    question_text=follow_up.question_text,
                    follow_up_depth=follow_up.follow_up_depth,
                )
                if follow_up
                else None
            ),
        )

    finally:
        clear_gemini_context()
    
@router.get(
    "/{answer_id}",
    response_model=AnswerDetail
)
def get_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    answer = (
        db.query(Answer)
        .filter(Answer.id == answer_id)
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=404,
            detail="Answer not found."
        )

    if answer.question.session.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this answer."
        )

    return answer


@router.get(
    "/session/{session_id}/results",
    response_model=SessionResultsResponse
)
def get_session_results(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    questions = (
        db.query(Question)
        .filter(Question.session_id == session.id)
        .order_by(Question.id)
        .all()
    )

    # Main-question numbering must ignore follow-up questions,
    # so an inserted follow-up never shifts the number of the
    # main question that comes after it.
    main_questions = [
        question
        for question in questions
        if not question.is_follow_up
    ]

    # A skipped question is simply a main question the user
    # never submitted an answer for, evaluated at the moment the
    # report is requested - this is derived entirely from
    # existing data (no new "skipped" field needed) and is
    # naturally correct for every case in the spec: skip-then-
    # answer-later leaves an Answer row and so is no longer
    # skipped, and finishing the interview early simply leaves
    # the remaining questions unanswered, which is exactly what
    # "skipped" means once the report is being viewed. Follow-up
    # questions are excluded from this list, consistent with the
    # main-question-only numbering above.
    skipped_main_questions = [
        (index + 1, question)
        for index, question in enumerate(main_questions)
        if not question.answer
    ]

    skipped_questions = _build_skipped_questions(
        skipped_main_questions
    )

    answered_questions = [
        question
        for question in questions
        if question.answer
    ]

    if not answered_questions:
        return SessionResultsResponse(
            session_id=session.id,
            average_score=0.0,
            questions_attempted=0,
            strong_topics=[],
            weak_topics=[],
            skipped_questions=skipped_questions,
        )

    total_score = 0

    # Track each distinct concept (merging obviously identical
    # concepts that only differ by casing/whitespace) along with
    # how many times it was flagged and, for weaknesses, the
    # scores of the answers that flagged it — so the final report
    # can prioritize concepts the candidate repeatedly struggled
    # with, not just list whatever appeared first.
    strength_concepts = {}
    weak_concepts = {}

    for question in answered_questions:

        answer = question.answer

        total_score += answer.score

        for concept in (answer.strengths or []):

            entry = _track_concept(
                strength_concepts,
                concept,
            )

            if entry:
                entry["count"] += 1

        for concept in (answer.improvements or []):

            entry = _track_concept(
                weak_concepts,
                concept,
            )

            if entry:
                entry["count"] += 1
                entry["scores"].append(answer.score)

    # Strong topics: concepts the candidate demonstrated
    # repeatedly are surfaced first.
    strong_topics = [
        entry["display"]
        for entry in sorted(
            strength_concepts.values(),
            key=lambda entry: -entry["count"],
        )
    ]

    # Weak topics: concepts flagged repeatedly are prioritized
    # first; among concepts flagged an equal number of times,
    # the ones tied to lower-scoring answers are prioritized,
    # since they represent more urgent gaps.
    weak_topics = [
        entry["display"]
        for entry in sorted(
            weak_concepts.values(),
            key=lambda entry: (
                -entry["count"],
                sum(entry["scores"]) / len(entry["scores"]),
            ),
        )
    ]

    average_score = total_score / len(answered_questions)

    return SessionResultsResponse(
        session_id=session.id,
        average_score=round(average_score, 2),
        questions_attempted=len(answered_questions),
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        skipped_questions=skipped_questions,
    )


def _build_skipped_questions(
    skipped_main_questions: list[tuple[int, Question]],
) -> list[SkippedQuestionInfo]:
    """
    Turns (main_question_number, Question) pairs into
    SkippedQuestionInfo entries, with a specific study topic for
    each - determined in a single batched Gemini call covering
    every skipped question in the session (never one call per
    question).
    """

    if not skipped_main_questions:
        return []

    topics = AIService().generate_skipped_topics(
        [
            question.question_text
            for _, question in skipped_main_questions
        ]
    )

    return [
        SkippedQuestionInfo(
            question_number=question_number,
            topic=topic,
        )
        for (question_number, _), topic in zip(
            skipped_main_questions,
            topics,
        )
    ]


# Question stems that indicate a value is a leaked question or
# instruction rather than a concise concept label.
_QUESTION_STEM_PREFIXES = (
    "explain",
    "describe",
    "what",
    "how",
    "why",
    "define",
    "discuss",
    "elaborate",
)


def _looks_like_concept(raw_concept: str) -> bool:
    """
    The evaluation prompt already instructs Gemini to return only
    concise concept labels (2-5 words), never question text. This
    is a lightweight local safety net — not a replacement for the
    prompt — so a stray Gemini response that leaks question text
    or instructions can never surface as a "topic" in the final
    report, per the report's explicit requirement to never show
    question text, question numbers, or truncated questions.
    """

    text = raw_concept.strip()

    if not text:
        return False

    if re.fullmatch(
        r"question\s*#?\s*\d+",
        text,
        flags=re.IGNORECASE,
    ):
        return False

    if text.endswith("?"):
        return False

    if len(text.split()) > 8:
        return False

    first_word = text.split()[0].lower().strip(":,.")

    if first_word in _QUESTION_STEM_PREFIXES:
        return False

    return True


def _track_concept(
    concepts: dict,
    raw_concept: str,
) -> dict | None:
    """
    Normalizes a concept string (collapsed whitespace, case
    folded) so obviously identical concepts like "ACID
    Properties" and "acid properties" are merged into a single
    entry, while genuinely distinct concepts (e.g. "Isolation
    Levels" vs "Transaction Isolation") are kept separate.

    Returns the tracking entry for the concept, or None if the
    concept string was empty or does not look like a concise
    concept label (see _looks_like_concept).
    """

    if not raw_concept or not _looks_like_concept(raw_concept):
        return None

    key = " ".join(
        raw_concept.strip().split()
    ).lower()

    if key not in concepts:

        concepts[key] = {
            "display": raw_concept.strip(),
            "count": 0,
            "scores": [],
        }

    return concepts[key]