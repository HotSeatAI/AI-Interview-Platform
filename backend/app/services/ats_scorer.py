from app.schemas.resume_analysis import (
    ATSFinding,
    ATSReport,
    BulletQuality,
    LayoutReport,
    ResumeProfile,
    StructureReport,
)
from app.services.resume_bullet_extractor import (
    extract_bullets_from_text,
)
from app.services.resume_layout_analyzer import ResumeLayoutAnalyzer
from app.services.resume_optimizer import ResumeOptimizer
from app.services.resume_structure_analyzer import (
    ResumeStructureAnalyzer,
)

_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

_REQUIRED_SECTIONS = ("experience", "education", "skills")


class ATSScorer:
    """
    Combines the layout/parseability check, section/contact
    completeness check, and bullet content-quality score into one
    ats_score — deterministic and LLM-free end to end, reusing
    ResumeOptimizer's existing JD-independent bullet sub-scores
    rather than recomputing them.
    """

    ATS_PARSEABILITY_CEILING = 55.0

    LAYOUT_WEIGHT_NO_JD = 0.40
    COMPLETENESS_WEIGHT_NO_JD = 0.20
    BULLET_WEIGHT_NO_JD = 0.40

    LAYOUT_WEIGHT_JD = 0.30
    COMPLETENESS_WEIGHT_JD = 0.10
    BULLET_WEIGHT_JD = 0.10
    JD_MATCH_WEIGHT_JD = 0.50

    LOW_QUANTIFICATION_THRESHOLD = 40.0
    LOW_ACTION_THRESHOLD = 40.0
    MAX_BULLET_FINDINGS = 5
    MAX_UNRECOGNIZED_HEADER_FINDINGS = 3

    def __init__(self):

        self._layout_analyzer = ResumeLayoutAnalyzer()
        self._structure_analyzer = ResumeStructureAnalyzer()
        self._optimizer = ResumeOptimizer()

    def score(
        self,
        resume_text: str,
        pdf_path: str,
        resume_profile: ResumeProfile | None = None,
        jd_match_score: float | None = None,
        precomputed_bullet_quality: (
            list[BulletQuality] | None
        ) = None,
    ) -> ATSReport:

        layout_report = self._layout_analyzer.analyze(pdf_path)
        structure_report = self._structure_analyzer.analyze(
            resume_text
        )

        bullet_scores = self._score_bullets(
            resume_text,
            resume_profile,
            precomputed_bullet_quality,
        )

        if bullet_scores:
            bullet_quality_avg = sum(
                bullet["content_quality_score"]
                for bullet in bullet_scores
            ) / len(bullet_scores)
        else:
            bullet_quality_avg = 0.0

        mode = "jd_aware" if jd_match_score is not None else "standalone"

        if mode == "standalone":
            weights = {
                "layout": self.LAYOUT_WEIGHT_NO_JD,
                "completeness": self.COMPLETENESS_WEIGHT_NO_JD,
                "bullet": self.BULLET_WEIGHT_NO_JD,
            }
        else:
            weights = {
                "layout": self.LAYOUT_WEIGHT_JD,
                "completeness": self.COMPLETENESS_WEIGHT_JD,
                "bullet": self.BULLET_WEIGHT_JD,
                "jd_match": self.JD_MATCH_WEIGHT_JD,
            }

        if not layout_report.file_available:
            # The original PDF is gone (e.g. an ephemeral hosting
            # filesystem lost it across a redeploy) — we have zero
            # evidence either way about parseability, so it's
            # excluded from the blend entirely rather than
            # defaulting to a fabricated pass or fail. The
            # remaining weights are renormalized to still sum to 1.
            del weights["layout"]

            weight_total = sum(weights.values())

            weights = {
                key: value / weight_total
                for key, value in weights.items()
            }

        ats_score = (
            structure_report.completeness_score
            * weights["completeness"]
            + bullet_quality_avg * weights["bullet"]
        )

        if "layout" in weights:
            ats_score += (
                layout_report.layout_score * weights["layout"]
            )

        if "jd_match" in weights:
            ats_score += jd_match_score * weights["jd_match"]

        parseability_capped = False

        if (
            layout_report.file_available
            and layout_report.parseability_gate_triggered
            and ats_score > self.ATS_PARSEABILITY_CEILING
        ):
            ats_score = self.ATS_PARSEABILITY_CEILING
            parseability_capped = True

        findings = self.build_findings(
            layout_report,
            structure_report,
            bullet_scores,
        )

        return ATSReport(
            ats_score=round(ats_score, 2),
            mode=mode,
            layout_report=layout_report,
            structure_report=structure_report,
            bullet_quality_avg=round(bullet_quality_avg, 2),
            jd_match_component=jd_match_score,
            parseability_capped=parseability_capped,
            findings=findings,
        )

    def _score_bullets(
        self,
        resume_text: str,
        resume_profile: ResumeProfile | None,
        precomputed_bullet_quality: (
            list[BulletQuality] | None
        ),
    ) -> list[dict]:

        if precomputed_bullet_quality is not None:

            return [
                {
                    "text": bullet.text,
                    "section": bullet.section,
                    "action_score": bullet.action_score,
                    "quantification_score": (
                        bullet.quantification_score
                    ),
                    "content_quality_score": bullet.overall_score,
                }
                for bullet in precomputed_bullet_quality
            ]

        if resume_profile is not None:
            bullets = self._optimizer._collect_bullets(
                resume_profile
            )
        else:
            bullets = extract_bullets_from_text(resume_text)

        return [
            self._optimizer.score_content_quality(bullet, section)
            for bullet, section in bullets
        ]

    def build_findings(
        self,
        layout_report: LayoutReport,
        structure_report: StructureReport,
        bullet_scores: list[dict],
    ) -> list[ATSFinding]:

        findings: list[ATSFinding] = []

        if not layout_report.file_available:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="high",
                    message=(
                        "We couldn't access your original resume "
                        "file to check its layout and formatting, "
                        "so this score doesn't include that check. "
                        "Re-upload your resume for a complete ATS "
                        "check."
                    ),
                )
            )

        if layout_report.multi_column:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="critical",
                    message=(
                        "Resume uses a multi-column layout, which "
                        "most ATS parsers read out of order. "
                        "Switch to a single-column layout."
                    ),
                )
            )

        if layout_report.has_tables:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="high",
                    message=(
                        "Tables detected — ATS parsers often drop "
                        "or scramble table content. Replace tables "
                        "with plain bullet lists."
                    ),
                )
            )

        if layout_report.was_ocr:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="high",
                    message=(
                        "This PDF has no selectable text layer "
                        "(looks scanned/image-based). Export "
                        "directly from Word/Google Docs as PDF "
                        "instead."
                    ),
                )
            )

        if layout_report.content_in_header_footer:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="medium",
                    message=(
                        "Contact info detected in the page "
                        "header/footer — many ATS parsers strip "
                        "these and will lose it. Move contact "
                        "details into the main body."
                    ),
                )
            )

        if layout_report.image_heavy_content:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="high",
                    message=(
                        "A large portion of this resume appears to "
                        "be an embedded image rather than "
                        "selectable text — ATS parsers can't read "
                        "image content. Re-create that content as "
                        "real text."
                    ),
                )
            )

        if layout_report.font_inconsistency:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="low",
                    message=(
                        "This resume mixes more than 3 different "
                        "fonts — stick to 1-2 font families for "
                        "reliable ATS parsing."
                    ),
                )
            )

        if layout_report.narrow_margins:
            findings.append(
                ATSFinding(
                    fix_type="layout",
                    priority="low",
                    message=(
                        "Margins are very tight — widen to at "
                        "least 0.5 inch for reliable parsing and "
                        "readability."
                    ),
                )
            )

        if not structure_report.has_email:
            findings.append(
                ATSFinding(
                    fix_type="contact",
                    priority="critical",
                    message="Add an email address to your resume.",
                )
            )

        if not structure_report.has_phone:
            findings.append(
                ATSFinding(
                    fix_type="contact",
                    priority="high",
                    message="Add a phone number to your resume.",
                )
            )

        for section in _REQUIRED_SECTIONS:

            if not structure_report.found_sections.get(
                section, False
            ):
                findings.append(
                    ATSFinding(
                        fix_type="section",
                        priority="medium",
                        message=(
                            f"No recognizable '{section}' section "
                            "header found. Add a standard heading "
                            f"(e.g. '{section.title()}')."
                        ),
                    )
                )

        unrecognized = structure_report.unrecognized_headers[
            : self.MAX_UNRECOGNIZED_HEADER_FINDINGS
        ]

        for header in unrecognized:
            findings.append(
                ATSFinding(
                    fix_type="section",
                    priority="low",
                    message=(
                        f"Section header '{header}' may not be "
                        "recognized by ATS parsers — if it's meant "
                        "as a section title, use a standard heading "
                        "for its content (e.g. Experience, "
                        "Education, Skills, Projects, "
                        "Certifications)."
                    ),
                )
            )

        findings.extend(
            self._bullet_findings(bullet_scores)
        )

        findings.sort(
            key=lambda finding: _PRIORITY_ORDER[finding.priority]
        )

        return findings

    def _bullet_findings(
        self,
        bullet_scores: list[dict],
    ) -> list[ATSFinding]:

        weak_bullets = [
            bullet
            for bullet in bullet_scores
            if (
                (
                    bullet.get("quantification_score", 100)
                    < self.LOW_QUANTIFICATION_THRESHOLD
                    and not self._optimizer.is_foundational_bullet(
                        bullet["text"]
                    )
                )
                or bullet.get("action_score", 100)
                < self.LOW_ACTION_THRESHOLD
            )
        ]

        weak_bullets.sort(
            key=lambda bullet: min(
                bullet.get("quantification_score", 100),
                bullet.get("action_score", 100),
            )
        )

        findings: list[ATSFinding] = []

        for bullet in weak_bullets[: self.MAX_BULLET_FINDINGS]:

            if (
                bullet.get("quantification_score", 100)
                < self.LOW_QUANTIFICATION_THRESHOLD
            ):
                findings.append(
                    ATSFinding(
                        fix_type="bullet_quality",
                        priority="medium",
                        message=(
                            "Bullet lacks a measurable result: "
                            f"\"{bullet['text']}\". Add a number "
                            "(team size, % improvement, time "
                            "saved, dollar amount)."
                        ),
                        original_text=bullet["text"],
                    )
                )
            elif (
                bullet.get("action_score", 100)
                < self.LOW_ACTION_THRESHOLD
            ):
                findings.append(
                    ATSFinding(
                        fix_type="bullet_quality",
                        priority="medium",
                        message=(
                            "Bullet starts with a weak verb: "
                            f"\"{bullet['text']}\". Start with a "
                            "strong action verb (e.g. Led, Built, "
                            "Reduced)."
                        ),
                        original_text=bullet["text"],
                    )
                )

        return findings
