import hashlib
import json
import re

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from app.services.resume_analysis_worker import (
    ResumeAnalysisWorker,
)
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.services.job_description_parser import (
    JobDescriptionParser,
)

router = APIRouter(
    prefix="/resume-analysis",
    tags=["Resume Analysis"],
)


def _normalize_for_hash(text: str) -> str:
    """
    Collapse whitespace/formatting noise (extra spaces, blank
    lines, CRLF vs LF) before hashing, so two pastes of the same
    JD that differ only in formatting still hit the JD cache.
    Never touches actual wording.
    """

    text = text.replace(
        "\r\n", "\n"
    ).replace(
        "\r", "\n"
    )

    text = re.sub(
        r"[ \t]+", " ", text
    )

    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    text = "\n".join(lines)

    text = re.sub(
        r"\n{2,}", "\n", text
    )

    return text.strip()


@router.post("/start")
async def start_resume_analysis(
    background_tasks: BackgroundTasks,

    resume_id: int = Form(...),

    job_description: str | None = Form(
        None
    ),

    job_description_file: UploadFile | None = File(
        None
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Creates a resume-JD analysis job.

    The heavy analysis runs in the background.
    """

    # --------------------------------------------------------
    # Validate resume ownership
    # --------------------------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    # --------------------------------------------------------
    # Validate JD input
    # --------------------------------------------------------

    if (
        not job_description
        and not job_description_file
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Provide either job description "
                "text or a job description file."
            ),
        )

    # --------------------------------------------------------
    # Extract JD immediately.
    #
    # We need the actual text stored in the database
    # before the request ends.
    # --------------------------------------------------------

    parser = JobDescriptionParser()

    try:

        extracted_jd = (
            await parser.extract_job_description(
                text=job_description,
                file=job_description_file,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------------
    # Create analysis record
    # --------------------------------------------------------

    jd_text_hash = hashlib.sha256(
        _normalize_for_hash(
            extracted_jd
        ).encode("utf-8")
    ).hexdigest()

    analysis = ResumeAnalysis(
        user_id=current_user.id,

        resume_id=resume.id,

        job_description_text=extracted_jd,

        jd_text_hash=jd_text_hash,

        status="processing",

        progress=0,

        current_stage=(
            "Analysis queued"
        ),
    )

    db.add(analysis)

    db.commit()

    db.refresh(analysis)

    # --------------------------------------------------------
    # Start background worker
    # --------------------------------------------------------

    background_tasks.add_task(
        ResumeAnalysisWorker(
            analysis.id
        ).run
    )

    return {
        "analysis_id": analysis.id,

        "status": analysis.status,

        "progress": analysis.progress,

        "current_stage": (
            analysis.current_stage
        ),

        "message": (
            "Resume analysis started."
        ),
    }

@router.get("/history")
def get_analysis_history(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Returns the current user's past resume-JD analyses,
    most recent first, for display on the resume page.
    """

    analyses = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id
            == current_user.id,
        )
        .order_by(
            ResumeAnalysis.created_at.desc()
        )
        .limit(50)
        .all()
    )

    resume_ids = {
        analysis.resume_id
        for analysis in analyses
    }

    resumes_by_id = {}

    if resume_ids:

        resumes = (
            db.query(Resume)
            .filter(
                Resume.id.in_(resume_ids)
            )
            .all()
        )

        resumes_by_id = {
            resume.id: resume.original_filename
            for resume in resumes
        }

    return [
        {
            "analysis_id": analysis.id,

            "resume_id": analysis.resume_id,

            "resume_filename": (
                resumes_by_id.get(
                    analysis.resume_id
                )
            ),

            "job_title": analysis.job_title,

            "overall_score": (
                analysis.overall_score
            ),

            "status": analysis.status,

            "created_at": analysis.created_at,

            "completed_at": (
                analysis.completed_at
            ),
        }
        for analysis in analyses
    ]

@router.get("/{analysis_id}/status")
def get_analysis_status(
    analysis_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.id
            == analysis_id,

            ResumeAnalysis.user_id
            == current_user.id,
        )
        .first()
    )

    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return {
        "analysis_id": analysis.id,

        "status": analysis.status,

        "progress": analysis.progress,

        "current_stage": (
            analysis.current_stage
        ),

        "error_message": (
            analysis.error_message
        ),

        "overall_score": (
            analysis.overall_score
        ),

        "created_at": (
            analysis.created_at
        ),

        "completed_at": (
            analysis.completed_at
        ),
    }

@router.get("/{analysis_id}/result")
def get_analysis_result(
    analysis_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.id
            == analysis_id,

            ResumeAnalysis.user_id
            == current_user.id,
        )
        .first()
    )

    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    if analysis.status == "processing":

        raise HTTPException(
            status_code=202,
            detail={
                "message": (
                    "Analysis is still processing."
                ),
                "progress": (
                    analysis.progress
                ),
            },
        )

    if analysis.status == "failed":

        raise HTTPException(
            status_code=500,
            detail=(
                analysis.error_message
                or "Analysis failed."
            ),
        )

    if not analysis.analysis_result_json:

        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis completed without "
                "a result."
            ),
        )

    try:

        result = json.loads(
            analysis.analysis_result_json
        )

    except json.JSONDecodeError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Stored analysis result is invalid."
            ),
        ) from exc

    return {
        "analysis_id": analysis.id,

        "status": analysis.status,

        "overall_score": (
            analysis.overall_score
        ),

        "job_title": analysis.job_title,

        "result": result,
    }
        