import re

from app.schemas.resume_analysis import (
    JDProfile,
    ResumeBullet,
    ResumeProfile,
    KeywordCoverage,
    BulletQuality,
    OptimizationFinding,
    OptimizationReport,
)


class ResumeOptimizer:
    """
    Deterministic resume optimization engine.

    This service identifies opportunities for improving
    JD alignment and resume communication.

    It NEVER writes new candidate claims.

    It only identifies opportunities.
    """

    WEAK_ACTION_VERBS = {
        "worked",
        "helped",
        "assisted",
        "involved",
        "participated",
        "handled",
        "did",
        "made",
        "used",
        "responsible",
    }

    STRONG_ACTION_VERBS = {
        "developed",
        "designed",
        "implemented",
        "built",
        "architected",
        "optimized",
        "automated",
        "deployed",
        "integrated",
        "engineered",
        "analyzed",
        "created",
        "led",
        "managed",
        "delivered",
        "configured",
        "migrated",
        "refactored",
        "tested",
        "validated",
    }

    FOUNDATIONAL_VERBS = {
        "founded",
        "architected",
        "led",
        "partnered",
        "mentored",
        "oversaw",
        "spearheaded",
        "established",
        "directed",
        "supervised",
        "pioneered",
        "launched",
    }

    IMPACT_TERMS = {
        "improved",
        "increased",
        "reduced",
        "decreased",
        "optimized",
        "accelerated",
        "automated",
        "scaled",
        "saved",
        "achieved",
        "delivered",
        "enhanced",
        "generated",
        "supported",
        "enabled",
    }

    GENERIC_TERMS = {
        "thing",
        "stuff",
        "various",
        "multiple",
        "different",
        "some",
        "good",
        "great",
        "basic",
        "simple",
        "worked",
    }

    METRIC_PATTERNS = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\+?\s*(?:users|user|clients|customers)",
        r"\b\d+(?:\.\d+)?\+?\s*(?:apis|api|endpoints)",
        r"\b\d+(?:\.\d+)?\+?\s*(?:projects|applications|services)",
        r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds|seconds|minutes|hours)",
        r"\b\d+(?:\.\d+)?\+?\s*(?:records|rows|requests|transactions)",
        r"\b\d+(?:\.\d+)?\+?\s*(?:people|members|engineers|developers)",
        r"\b(?:top|ranked)\s+\d+",
        r"\b\d+(?:\.\d+)?\s*(?:x|times)\b",
        r"\$\s*\d+(?:\.\d+)?",
    ]

    def analyze(
        self,
        jd_profile: JDProfile,
        resume_profile: ResumeProfile,
        matching_report,
    ) -> OptimizationReport:

        keyword_coverage = (
            self._analyze_keyword_coverage(
                jd_profile,
                resume_profile,
                matching_report,
            )
        )

        bullets = self._collect_bullets(
            resume_profile
        )

        bullet_quality = []

        for bullet, section in bullets:

            quality = self._analyze_bullet(
                bullet,
                section,
                jd_profile,
            )

            bullet_quality.append(
                quality
            )

        findings = []

        findings.extend(
            self._keyword_findings(
                keyword_coverage,
                resume_profile,
            )
        )

        findings.extend(
            self._bullet_findings(
                bullet_quality,
                matching_report,
            )
        )

        findings.extend(
            self._metric_findings(
                bullet_quality,
                matching_report,
            )
        )

        findings = self._prioritize_findings(
            findings
        )

        optimization_score = (
            self._calculate_optimization_score(
                keyword_coverage,
                bullet_quality,
                findings,
            )
        )

        return OptimizationReport(
            optimization_score=round(
                optimization_score,
                2,
            ),
            keyword_coverage=keyword_coverage,
            bullet_quality=bullet_quality,
            findings=findings,
        )

    # ========================================================
    # Keyword Analysis
    # ========================================================

    def _analyze_keyword_coverage(
        self,
        jd_profile: JDProfile,
        resume_profile: ResumeProfile,
        matching_report,
    ) -> list[KeywordCoverage]:
        """
        Sources coverage directly from the already-computed
        RequirementMatcher output instead of re-deriving its
        own evidence search.

        Requirement matching (including compound-requirement
        decomposition and controlled concept/indirect evidence)
        is intentionally implemented ONCE, in RequirementMatcher.
        Re-implementing a second, weaker "does evidence exist"
        check here previously caused this method to silently
        disagree with the matching report — a JD requirement
        the matcher correctly found indirect evidence for could
        still show up here as "not present", suppressing the
        rewrite-eligible findings that feed recommendations.
        """

        matches_by_requirement = {
            match.requirement: match
            for match in matching_report.matches
        }

        results = []

        for requirement in jd_profile.requirements:

            match = matches_by_requirement.get(
                requirement.name
            )

            if match is None:

                results.append(
                    KeywordCoverage(
                        keyword=requirement.name,
                        importance=requirement.importance,
                        weight=requirement.weight,
                        present=False,
                        contextual=False,
                        occurrences=0,
                        evidence=[],
                    )
                )

                continue

            present = match.match_type in {
                "strong",
                "partial",
            }

            contextual = bool(
                set(match.matched_resume_sections)
                & {"experience", "projects"}
            )

            results.append(
                KeywordCoverage(
                    keyword=requirement.name,
                    importance=requirement.importance,
                    weight=requirement.weight,
                    present=present,
                    contextual=contextual,
                    occurrences=len(
                        match.matched_resume_evidence
                    ),
                    evidence=match.matched_resume_evidence,
                )
            )

        return results

    # ========================================================
    # Bullet Analysis
    # ========================================================

    def score_content_quality(
        self,
        bullet: ResumeBullet,
        section: str,
    ) -> dict:
        """
        The 4 bullet-quality sub-scores that do NOT require a job
        description — action-verb strength, quantification,
        impact language, specificity. Pulled out of
        _analyze_bullet() as the single source of truth so the
        standalone (no-JD) ATS scoring path can reuse the exact
        same verb lists/regexes instead of duplicating them.
        """

        text = bullet.text.strip()

        action_score = self._action_score(text)
        quantification_score = self._quantification_score(bullet)
        impact_score = self._impact_score(text)
        specificity_score = self._specificity_score(text)

        content_quality_score = (
            action_score
            + quantification_score
            + impact_score
            + specificity_score
        ) / 4

        return {
            "text": text,
            "section": section,
            "action_score": action_score,
            "quantification_score": quantification_score,
            "impact_score": impact_score,
            "specificity_score": specificity_score,
            "content_quality_score": content_quality_score,
        }

    def _analyze_bullet(
        self,
        bullet: ResumeBullet,
        section: str,
        jd_profile: JDProfile,
    ) -> BulletQuality:

        content_quality = self.score_content_quality(
            bullet,
            section,
        )

        text = content_quality["text"]
        action_score = content_quality["action_score"]
        quantification_score = (
            content_quality["quantification_score"]
        )
        impact_score = content_quality["impact_score"]
        specificity_score = content_quality["specificity_score"]

        jd_relevance_score = (
            self._jd_relevance_score(
                text,
                jd_profile,
            )
        )

        overall = (
            action_score * 0.20
            + quantification_score * 0.20
            + impact_score * 0.20
            + specificity_score * 0.20
            + jd_relevance_score * 0.20
        )

        return BulletQuality(
            text=text,
            section=section,
            action_score=round(
                action_score,
                2,
            ),
            quantification_score=round(
                quantification_score,
                2,
            ),
            impact_score=round(
                impact_score,
                2,
            ),
            specificity_score=round(
                specificity_score,
                2,
            ),
            jd_relevance_score=round(
                jd_relevance_score,
                2,
            ),
            overall_score=round(
                overall,
                2,
            ),
        )

    # ========================================================
    # Action Verb Analysis
    # ========================================================

    def _action_score(
        self,
        text: str,
    ) -> float:

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower(),
        )

        if not words:
            return 0

        first_word = words[0]

        if first_word in self.STRONG_ACTION_VERBS:
            return 100

        if first_word in self.WEAK_ACTION_VERBS:
            return 30

        if any(
            word in self.STRONG_ACTION_VERBS
            for word in words[:5]
        ):
            return 75

        return 55

    def is_foundational_bullet(
        self,
        text: str,
    ) -> bool:

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower(),
        )

        return any(
            word in self.FOUNDATIONAL_VERBS
            for word in words[:5]
        )

    # ========================================================
    # Quantification
    # ========================================================

    def _quantification_score(
        self,
        bullet: ResumeBullet,
    ) -> float:

        if bullet.metrics:
            return 100

        text = bullet.text.lower()

        for pattern in self.METRIC_PATTERNS:

            if re.search(
                pattern,
                text,
            ):
                return 100

        # A bullet does not always need a metric.
        # Give partial credit when it contains
        # concrete technical detail.

        technical_terms = (
            bullet.technologies
        )

        if technical_terms:
            return 55

        return 25

    # ========================================================
    # Impact
    # ========================================================

    def _impact_score(
        self,
        text: str,
    ) -> float:

        normalized = text.lower()

        impact_count = sum(
            1
            for term in self.IMPACT_TERMS
            if re.search(
                r"\b"
                + re.escape(term)
                + r"\b",
                normalized,
            )
        )

        has_metric = any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in self.METRIC_PATTERNS
        )

        if impact_count >= 2 and has_metric:
            return 100

        if impact_count >= 1 and has_metric:
            return 90

        if impact_count >= 1:
            return 65

        if has_metric:
            return 60

        return 30

    # ========================================================
    # Specificity
    # ========================================================

    def _specificity_score(
        self,
        text: str,
    ) -> float:

        words = re.findall(
            r"\b[a-zA-Z0-9+#./-]+\b",
            text.lower(),
        )

        if not words:
            return 0

        generic_count = sum(
            1
            for word in words
            if word in self.GENERIC_TERMS
        )

        technical_signals = (
            r"\b(?:api|database|backend|frontend|"
            r"framework|algorithm|model|service|"
            r"pipeline|deployment|application|"
            r"system|platform|architecture)\b"
        )

        technical_count = len(
            re.findall(
                technical_signals,
                text.lower(),
            )
        )

        score = 50

        score += min(
            technical_count * 10,
            30,
        )

        score -= min(
            generic_count * 10,
            30,
        )

        return max(
            0,
            min(
                score,
                100,
            ),
        )

    # ========================================================
    # JD Relevance
    # ========================================================

    def _jd_relevance_score(
        self,
        text: str,
        jd_profile: JDProfile,
    ) -> float:

        normalized = text.lower()

        matched = 0
        total = len(
            jd_profile.requirements
        )

        if total == 0:
            return 0

        for requirement in (
            jd_profile.requirements
        ):

            terms = [
                requirement.name,
                *requirement.aliases,
            ]

            if any(
                term.lower()
                in normalized
                for term in terms
            ):
                matched += requirement.weight

        total_weight = sum(
            requirement.weight
            for requirement in jd_profile.requirements
        )

        if total_weight == 0:
            return 0

        return (
            matched
            / total_weight
        ) * 100

    # ========================================================
    # Findings
    # ========================================================

    def _keyword_findings(
        self,
        coverage: list[KeywordCoverage],
        resume_profile: ResumeProfile,
    ) -> list[OptimizationFinding]:

        findings = []

        for item in coverage:

            if item.present and item.contextual:
                continue

            if not item.present:

                priority = (
                    "critical"
                    if item.importance == "required"
                    else "medium"
                )

                findings.append(
                    OptimizationFinding(
                        finding_type="missing_keyword",
                        priority=priority,
                        impact_score=(
                            item.weight * 10
                        ),
                        section="skills",
                        original_text="",
                        jd_requirement=item.keyword,
                        evidence=[],
                        explanation=(
                            f"{item.keyword} is an important "
                            f"JD requirement but no supporting "
                            f"resume evidence was found. "
                            f"Do not add it unless you genuinely "
                            f"have this experience."
                        ),
                        safe_to_rewrite=False,
                    )
                )

            elif not item.contextual:

                findings.append(
                    OptimizationFinding(
                        finding_type=(
                            "weak_keyword_context"
                        ),
                        priority=(
                            "high"
                            if item.importance == "required"
                            else "medium"
                        ),
                        impact_score=(
                            item.weight * 8
                        ),
                        section="resume",
                        original_text=(
                            item.evidence[0]
                            if item.evidence
                            else ""
                        ),
                        jd_requirement=item.keyword,
                        evidence=item.evidence,
                        explanation=(
                            f"{item.keyword} appears in the "
                            f"resume but is not strongly "
                            f"demonstrated in contextual "
                            f"experience or project evidence."
                        ),
                        safe_to_rewrite=True,
                    )
                )

        return findings

    def _bullet_findings(
        self,
        bullets: list[BulletQuality],
        matching_report,
    ) -> list[OptimizationFinding]:

        findings = []

        for bullet in bullets:

            if bullet.action_score < 50:

                findings.append(
                    OptimizationFinding(
                        finding_type="weak_action_verb",
                        priority="medium",
                        impact_score=60,
                        section=bullet.section,
                        original_text=bullet.text,
                        evidence=[bullet.text],
                        explanation=(
                            "This bullet does not begin with "
                            "a strong action-oriented verb. "
                            "Consider using a more precise verb "
                            "that accurately reflects what you "
                            "actually did."
                        ),
                        safe_to_rewrite=True,
                    )
                )

            if bullet.specificity_score < 50:

                findings.append(
                    OptimizationFinding(
                        finding_type="low_specificity",
                        priority="medium",
                        impact_score=55,
                        section=bullet.section,
                        original_text=bullet.text,
                        evidence=[bullet.text],
                        explanation=(
                            "This bullet contains relatively "
                            "generic wording. Consider making "
                            "the technology, responsibility, "
                            "scope, or result more specific "
                            "using information already supported "
                            "by your resume."
                        ),
                        safe_to_rewrite=True,
                    )
                )

            if bullet.impact_score < 50:

                findings.append(
                    OptimizationFinding(
                        finding_type="weak_impact",
                        priority="medium",
                        impact_score=50,
                        section=bullet.section,
                        original_text=bullet.text,
                        evidence=[bullet.text],
                        explanation=(
                            "This bullet describes work but "
                            "does not clearly communicate its "
                            "outcome or impact."
                        ),
                        safe_to_rewrite=True,
                    )
                )

        return findings

    def _metric_findings(
        self,
        bullets: list[BulletQuality],
        matching_report,
    ) -> list[OptimizationFinding]:

        findings = []

        for bullet in bullets:

            if bullet.quantification_score >= 80:
                continue

            if bullet.jd_relevance_score < 30:
                continue

            findings.append(
                OptimizationFinding(
                    finding_type="missing_metric",
                    priority="medium",
                    impact_score=65,
                    section=bullet.section,
                    original_text=bullet.text,
                    evidence=[bullet.text],
                    explanation=(
                        "This bullet is relevant to the "
                        "target role but does not contain "
                        "a measurable result. If you have a "
                        "verified metric, consider adding it."
                    ),
                    safe_to_rewrite=True,
                )
            )

        return findings

    # ========================================================
    # Finding prioritization
    # ========================================================

    def _prioritize_findings(
        self,
        findings: list[OptimizationFinding],
    ) -> list[OptimizationFinding]:

        priority_order = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }

        return sorted(
            findings,
            key=lambda item: (
                priority_order[
                    item.priority
                ],
                item.impact_score,
            ),
            reverse=True,
        )

    # ========================================================
    # Optimization Score
    # ========================================================

    def _calculate_optimization_score(
        self,
        keyword_coverage,
        bullet_quality,
        findings,
    ) -> float:

        if not keyword_coverage:
            keyword_score = 0

        else:
            total_weight = sum(
                item.weight
                for item in keyword_coverage
            )

            achieved_weight = sum(
                item.weight
                for item in keyword_coverage
                if item.present
                and item.contextual
            )

            keyword_score = (
                achieved_weight
                / total_weight
                * 100
                if total_weight
                else 0
            )

        if bullet_quality:

            bullet_score = sum(
                item.overall_score
                for item in bullet_quality
            ) / len(
                bullet_quality
            )

        else:
            bullet_score = 0

        critical_penalty = sum(
            15
            for finding in findings
            if finding.priority == "critical"
        )

        high_penalty = sum(
            7
            for finding in findings
            if finding.priority == "high"
        )

        score = (
            keyword_score * 0.55
            + bullet_score * 0.45
            - critical_penalty
            - high_penalty
        )

        return max(
            0,
            min(
                score,
                100,
            ),
        )

    # ========================================================
    # Helpers
    # ========================================================

    def _collect_bullets(
        self,
        resume_profile: ResumeProfile,
    ) -> list[tuple[ResumeBullet, str]]:

        bullets = []

        for experience in (
            resume_profile.experience
        ):

            for bullet in experience.bullets:

                bullets.append(
                    (
                        bullet,
                        "experience",
                    )
                )

        for project in (
            resume_profile.projects
        ):

            for bullet in project.bullets:

                bullets.append(
                    (
                        bullet,
                        "projects",
                    )
                )

        return bullets

