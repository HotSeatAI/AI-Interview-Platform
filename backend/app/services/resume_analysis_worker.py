import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis

from app.services.job_description_parser import (
    JobDescriptionParser,
)
from app.schemas.resume_analysis import (
    JDProfile,
    ResumeProfile,
)
from app.services.resume_analyzer import (
    ResumeAnalyzer,
)
from app.services.evidence_validator import (
    EvidenceValidator,
)
from app.services.requirement_matcher import (
    RequirementMatcher,
)
from app.services.resume_optimizer import (
    ResumeOptimizer,
)
from app.services.recommendation_engine import (
    RecommendationEngine,
)
from app.services.api_key_manager import (
    clear_gemini_context,
    get_gemini_call_count,
    set_gemini_context,
)


class ResumeAnalysisWorker:

    def __init__(
        self,
        analysis_id: int,
    ):
        self.analysis_id = analysis_id

    def run(self) -> None:

        db: Session = SessionLocal()

        set_gemini_context(self.analysis_id)

        try:

            analysis = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.id
                    == self.analysis_id
                )
                .first()
            )

            if not analysis:
                return

            self._update_progress(
                db,
                analysis,
                5,
                "Starting analysis",
            )

            resume = (
                db.query(Resume)
                .filter(
                    Resume.id
                    == analysis.resume_id
                )
                .first()
            )

            if not resume:

                self._fail(
                    db,
                    analysis,
                    "Resume not found.",
                )

                return

            # =================================================
            # FULL-RESULT CACHE — same resume + same JD, already
            # completed before. Reuse the entire prior result and
            # skip the pipeline entirely (zero Gemini calls).
            # =================================================

            full_cache = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.user_id
                    == analysis.user_id,
                    ResumeAnalysis.resume_id
                    == analysis.resume_id,
                    ResumeAnalysis.jd_text_hash
                    == analysis.jd_text_hash,
                    ResumeAnalysis.id
                    != analysis.id,
                    ResumeAnalysis.status
                    == "completed",
                    ResumeAnalysis.analysis_result_json.isnot(
                        None
                    ),
                )
                .order_by(
                    ResumeAnalysis.created_at.desc()
                )
                .first()
            )

            if (
                full_cache
                and analysis.jd_text_hash
            ):

                analysis.job_title = (
                    full_cache.job_title
                )

                analysis.jd_profile_json = (
                    full_cache.jd_profile_json
                )

                analysis.resume_profile_json = (
                    full_cache.resume_profile_json
                )

                analysis.analysis_result_json = (
                    full_cache.analysis_result_json
                )

                analysis.overall_score = (
                    full_cache.overall_score
                )

                analysis.status = "completed"

                analysis.progress = 100

                analysis.current_stage = (
                    "Analysis complete"
                )

                analysis.completed_at = (
                    datetime.utcnow()
                )

                analysis.error_message = None

                db.commit()

                return

            # =================================================
            # STEP 1 — Extract JD
            # =================================================

            self._update_progress(
                db,
                analysis,
                10,
                "Reading job description",
            )

            parser = JobDescriptionParser()

            jd_text = (
                analysis.job_description_text
            )

            if not jd_text:

                self._fail(
                    db,
                    analysis,
                    "Job description is empty.",
                )

                return

            # =================================================
            # STEP 2 — JD Intelligence
            # =================================================

            self._update_progress(
                db,
                analysis,
                20,
                "Understanding job requirements",
            )

            cached_jd = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.user_id
                    == analysis.user_id,
                    ResumeAnalysis.jd_text_hash
                    == analysis.jd_text_hash,
                    ResumeAnalysis.id
                    != analysis.id,
                    ResumeAnalysis.jd_profile_json.isnot(
                        None
                    ),
                )
                .order_by(
                    ResumeAnalysis.created_at.desc()
                )
                .first()
            )

            if cached_jd:

                jd_profile = (
                    JDProfile.model_validate(
                        json.loads(
                            cached_jd.jd_profile_json
                        )
                    )
                )

            else:

                jd_profile = (
                    parser.structure_job_description(
                        jd_text
                    )
                )

            analysis.job_title = (
                jd_profile.job_title
            )

            analysis.jd_profile_json = (
                jd_profile.model_dump_json()
            )

            db.commit()

            # =================================================
            # STEP 3 — Resume Intelligence
            # =================================================

            self._update_progress(
                db,
                analysis,
                35,
                "Analyzing resume",
            )

            cached_resume = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.resume_id
                    == analysis.resume_id,
                    ResumeAnalysis.id
                    != analysis.id,
                    ResumeAnalysis.resume_profile_json.isnot(
                        None
                    ),
                )
                .order_by(
                    ResumeAnalysis.created_at.desc()
                )
                .first()
            )

            if cached_resume:

                resume_profile = (
                    ResumeProfile.model_validate(
                        json.loads(
                            cached_resume.resume_profile_json
                        )
                    )
                )

            else:

                resume_analyzer = ResumeAnalyzer()

                resume_profile = (
                    resume_analyzer.analyze(
                        resume.extracted_text
                    )
                )

            analysis.resume_profile_json = (
                resume_profile.model_dump_json()
            )

            db.commit()

            # =================================================
            # STEP 4 — Evidence Validation
            # =================================================

            self._update_progress(
                db,
                analysis,
                48,
                "Verifying resume evidence",
            )

            validator = EvidenceValidator()

            resume_profile = (
                validator.validate(
                    resume_text=resume.extracted_text,
                    profile=resume_profile,
                )
            )

            # =================================================
            # STEP 5 — Requirement Matching
            # =================================================

            self._update_progress(
                db,
                analysis,
                60,
                "Matching resume against requirements",
            )

            matcher = RequirementMatcher()

            matching_report = matcher.match(
                jd_profile=jd_profile,
                resume_profile=resume_profile,
                resume_text=resume.extracted_text,
            )

            # =================================================
            # STEP 6 — Resume Optimization
            # =================================================

            self._update_progress(
                db,
                analysis,
                72,
                "Analyzing resume improvement opportunities",
            )

            optimizer = ResumeOptimizer()

            optimization_report = optimizer.analyze(
                jd_profile=jd_profile,
                resume_profile=resume_profile,
                matching_report=matching_report,
            )

            # =================================================
            # STEP 7 — Recommendations
            # =================================================

            self._update_progress(
                db,
                analysis,
                84,
                "Generating evidence-backed recommendations",
            )

            recommendation_engine = (
                RecommendationEngine()
            )

            recommendation_report = (
                recommendation_engine.generate(
                    jd_profile=jd_profile,
                    resume_profile=resume_profile,
                    matching_report=matching_report,
                    optimization_report=optimization_report,
                )
            )

            # =================================================
            # STEP 8 — Final validation
            # =================================================

            self._update_progress(
                db,
                analysis,
                94,
                "Validating recommendations",
            )

            analysis_result = {
                "resume_profile": (
                    resume_profile.model_dump()
                ),

                "matching_report": (
                    matching_report.model_dump()
                ),

                "optimization_report": (
                    optimization_report.model_dump()
                ),

                "recommendation_report": (
                    recommendation_report.model_dump()
                ),
            }

            analysis.analysis_result_json = (
                json.dumps(
                    analysis_result
                )
            )

            analysis.overall_score = round(
                matching_report.overall_score
            )

            analysis.status = "completed"

            analysis.progress = 100

            analysis.current_stage = (
                "Analysis complete"
            )

            analysis.completed_at = (
                datetime.utcnow()
            )

            analysis.error_message = None

            db.commit()

        except Exception as exc:

            db.rollback()

            analysis = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.id
                    == self.analysis_id
                )
                .first()
            )

            if analysis:

                self._fail(
                    db,
                    analysis,
                    str(exc),
                )

        finally:

            print(
                f"[ResumeAnalysis {self.analysis_id}] "
                f"Total Gemini calls: "
                f"{get_gemini_call_count()}"
            )

            clear_gemini_context()

            db.close()

    @staticmethod
    def _update_progress(
        db: Session,
        analysis: ResumeAnalysis,
        progress: int,
        stage: str,
    ) -> None:

        analysis.progress = progress

        analysis.current_stage = stage

        analysis.status = "processing"

        db.commit()

    @staticmethod
    def _fail(
        db: Session,
        analysis: ResumeAnalysis,
        message: str,
    ) -> None:

        analysis.status = "failed"

        analysis.error_message = message

        analysis.current_stage = (
            "Analysis failed"
        )

        db.commit()