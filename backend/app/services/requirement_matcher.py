import re
from difflib import SequenceMatcher

from app.schemas.resume_analysis import (
    JDProfile,
    JDRequirement,
    RequirementMatch,
    MatchingReport,
    MatchingSummary,
    ResumeProfile,
    ResumeEvidence,
)
from app.services.semantic_verifier import (
    SemanticVerifier,
)

class RequirementMatcher:
    """
    Deterministic Resume ↔ JD matching engine.

    The matcher deliberately does NOT let an LLM
    arbitrarily decide the score.

    Matching is based on:

    1. Exact matches
    2. Controlled aliases
    3. Evidence context
    4. Conservative fuzzy matching
    5. Requirement importance
    6. Evidence confidence
    """
    def __init__(self):
        self.semantic_verifier = SemanticVerifier()
    # --------------------------------------------------------
    # Controlled aliases
    # --------------------------------------------------------

    COMMON_ALIASES = {
        "postgres": {
            "postgresql",
        },

        "postgresql": {
            "postgres",
        },

        "restful api": {
            "rest api",
            "rest apis",
            "restful apis",
        },

        "rest api": {
            "restful api",
            "rest apis",
            "restful apis",
        },

        "javascript": {
            "js",
            "ecmascript",
        },

        "typescript": {
            "ts",
        },

        "cplusplus": {
            "c++",
            "cpp",
        },

        "c++": {
            "cplusplus",
            "cpp",
        },

        "kubernetes": {
            "k8s",
        },

        "ci/cd": {
            "cicd",
            "continuous integration",
            "continuous deployment",
            "continuous integration and deployment",
        },

        "machine learning": {
            "ml",
        },

        "artificial intelligence": {
            "ai",
        },

        "application programming interface": {
            "api",
            "apis",
        },

        "react.js": {
            "react",
            "reactjs",
        },

        "react": {
            "react.js",
            "reactjs",
        },

        "node.js": {
            "node",
            "nodejs",
        },

        "vue.js": {
            "vue",
            "vuejs",
        },

        "next.js": {
            "nextjs",
        },
    }

    # --------------------------------------------------------
    # Known related-but-NOT-equivalent technology pairs.
    #
    # These are never treated as aliases — Pass 1 keyword/fuzzy
    # matching must never conflate them. They ARE used as a
    # deterministic hint fed into semantic verification: if the
    # resume shows one of a pair while the JD requires the
    # other (e.g. Azure when AWS is required), Gemini is told
    # this explicitly so its "adjacent" judgment is grounded in
    # a curated fact instead of a free-form guess.
    #
    # This table only covers software/tech pairs and is a free,
    # zero-cost baseline for that domain — for every other
    # domain (sales, finance, healthcare, etc.), the same
    # mechanism is extended per-JD by JDRequirement.
    # adjacent_alternatives (LLM-generated once during JD
    # structuring), unioned with this table wherever it's
    # consulted (_detect_adjacency_hints,
    # _retrieve_relevant_evidence).
    # --------------------------------------------------------

    ADJACENT_TECHNOLOGY_PAIRS = {
        frozenset(("aws", "azure")),
        frozenset(("aws", "gcp")),
        frozenset(("azure", "gcp")),
        frozenset(("docker", "kubernetes")),
        frozenset(("react", "angular")),
        frozenset(("react", "vue")),
        frozenset(("python", "java")),
        frozenset(("postgresql", "mysql")),
        frozenset(("postgres", "mysql")),
    }

    IMPORTANCE_MULTIPLIERS = {
        "required": 1.00,
        "preferred": 0.70,
        "nice_to_have": 0.50,
        "unclear": 0.50,
    }

    # A "required" match and a "missing" match don't move the
    # overall score the same amount for every category — a
    # missing named technical skill/tool should hurt more than a
    # missing degree requirement, since many roles waive the
    # latter when the actual skills are present. This multiplies
    # into effective_weight alongside IMPORTANCE_MULTIPLIERS
    # (see _calculate_overall_score) rather than changing what
    # match_type itself means.
    CATEGORY_MULTIPLIERS = {
        "technical_skill": 1.00,
        "tool": 1.00,
        "responsibility": 0.85,
        "domain": 0.75,
        "experience": 0.75,
        "certification": 0.60,
        "soft_skill": 0.55,
        "education": 0.50,
        "other": 0.50,
    }

    # A missing JDRequirement.is_dealbreaker requirement caps
    # the overall score at this ceiling, regardless of how well
    # everything else matches — mirrors a recruiter screening
    # out on a genuine hard gate rather than averaging it away.
    DEALBREAKER_SCORE_CEILING = 50.0

    # --------------------------------------------------------
    # Controlled concept -> evidence-keyword mapping.
    #
    # This lets the matcher recognize INDIRECT evidence for
    # abstract/soft JD concepts (e.g. "collaborative coding")
    # without resorting to open-ended semantic guessing. Every
    # entry is a fixed, human-curated list of literal phrases —
    # a match still requires one of these phrases to appear
    # verbatim in the resume evidence.
    #
    # This table's vocabulary is tech-flavored and is a free,
    # zero-cost baseline for that domain — _concept_hint_terms
    # unions it with JDRequirement.evidence_hints (LLM-generated
    # once per JD during structuring) so the same indirect-
    # evidence mechanism works for any domain this table has no
    # phrases for.
    #
    # "triggers" identify when a requirement/component name
    # refers to this concept. "evidence_terms" are the resume
    # phrases that would count as supporting (indirect) proof.
    # --------------------------------------------------------

    CONCEPT_EVIDENCE_HINTS = [
        {
            "triggers": {
                "collaborative coding",
                "collaborative development",
                "collaboration",
                "team development",
                "pair programming",
                "working with a team",
                "cross-functional",
                "cross functional",
            },
            "evidence_terms": {
                "git", "github", "gitlab", "bitbucket",
                "pull request", "pull requests", "pr review",
                "code review", "pair programming",
                "team of", "collaborated", "collaboration",
                "cross-functional", "cross functional",
                "worked with a team", "agile", "scrum",
                "open source",
            },
        },
        {
            "triggers": {
                "code review",
            },
            "evidence_terms": {
                "code review", "pull request", "pull requests",
                "pr review", "peer review", "reviewed code",
                "reviewed pull requests",
            },
        },
        {
            "triggers": {
                "production safety",
                "production readiness",
                "production support",
            },
            "evidence_terms": {
                "production", "deploy", "deployment",
                "incident", "rollback", "monitoring",
                "on-call", "oncall", "hotfix", "post-mortem",
                "postmortem",
            },
        },
        {
            "triggers": {
                "learn unfamiliar systems",
                "ability to learn",
                "learning unfamiliar systems",
                "ramp up",
                "ramp-up",
                "quickly learn",
                "adapt to new",
                "adaptability",
            },
            "evidence_terms": {
                "ramped up", "onboarded", "quickly learned",
                "new codebase", "unfamiliar", "self-taught",
                "learned independently", "picked up",
                "adapted to", "fast learner",
            },
        },
        {
            "triggers": {
                "large code base",
                "large codebase",
                "code base navigation",
                "codebase navigation",
                "legacy code",
                "legacy codebase",
            },
            "evidence_terms": {
                "large codebase", "large code base",
                "legacy code", "legacy codebase",
                "existing codebase", "navigated",
                "codebase", "monorepo",
            },
        },
        {
            "triggers": {
                "frontend technologies",
                "frontend",
                "front-end",
                "front end",
                "ui development",
                "client-side",
                "client side",
            },
            "evidence_terms": {
                "react", "angular", "vue", "svelte",
                "html", "css", "javascript", "typescript",
                "frontend", "front-end", "front end",
                "ui", "user interface", "dom",
            },
        },
        {
            "triggers": {
                "web services",
                "web service",
                "backend services",
                "backend service",
                "rest api",
                "restful",
                "http service",
                "api development",
            },
            "evidence_terms": {
                "rest api", "restful", "http service",
                "web service", "web services",
                "api endpoint", "backend service",
                "microservice", "graphql", "flask",
                "fastapi", "django", "express", "spring boot",
                "node.js", "nodejs", "http server",
            },
        },
    ]

    # Conservative score assigned per evidence tier. These feed
    # both the aggregate match_strength AND the confidence
    # ceilings below — neither is allowed to exceed what the
    # tier itself justifies, regardless of what raw confidence
    # value the resume-extraction step assigned to a single
    # piece of evidence.
    TIER_SCORES = {
        "direct": 1.00,
        "indirect": 0.70,
        "partial": 0.55,
        "ambiguous": 0.30,
        "unsupported": 0.0,
    }

    TIER_CONFIDENCE_CEILING = {
        "direct": 0.95,
        "indirect": 0.75,
        "partial": 0.55,
        "ambiguous": 0.40,
        "unsupported": 0.0,
    }

    COMPOUND_SPLIT_PATTERN = re.compile(
        r"\s*(?:,|&|/|\band\b)\s*",
        re.IGNORECASE,
    )

    # Requirement categories treated as contextual/semantic
    # (Part 3) rather than objective/technical. Zero keyword
    # overlap for these does not prove "missing" the way it
    # does for a technical skill name.
    CONTEXTUAL_CATEGORIES = {
        "soft_skill",
        "responsibility",
    }

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def match(
    self,
    jd_profile: JDProfile,
    resume_profile: ResumeProfile,
    resume_text: str = "",
) -> MatchingReport:

        # ----------------------------------------------------
        # Pass 1 — fully deterministic matching for every
        # requirement. No Gemini calls happen here.
        # ----------------------------------------------------

        preliminary_results = [
            self._match_requirement(
                requirement,
                resume_profile,
            )
            for requirement in jd_profile.requirements
        ]

        # ----------------------------------------------------
        # Pass 2 — every requirement now goes through a single
        # holistic Gemini pass (SemanticVerifier), not just the
        # ones Pass 1 flagged "ambiguous" or a narrower retrieval
        # search happened to find something loosely related to.
        # Gating on that narrower search meant a requirement
        # whose evidence sat in a resume section the structured
        # extraction step missed entirely (e.g. an Education
        # section that came back empty) could never earn a
        # second look, even though the real evidence was sitting
        # in the raw resume text the whole time. Every
        # requirement is verified via one or more batched Gemini
        # calls (chunked, not one call per requirement) to stay
        # within a bounded call budget. Pass 1's own confident
        # direct/strong matches still act as a floor in
        # _merge_verification — this pass can upgrade a
        # classification but never downgrade a confirmed literal
        # match.
        # ----------------------------------------------------

        candidate_requirements = list(
            jd_profile.requirements
        )

        # ----------------------------------------------------
        # Retrieval step: for each requirement, pull the top-K
        # most relevant resume evidence lines as a focused hint
        # alongside the complete raw resume text given below.
        # These are RETRIEVAL signals only — their presence
        # means "worth Gemini's attention", not proof. Gemini
        # still has to decide strong/partial/missing based on
        # what's actually here.
        # ----------------------------------------------------

        evidence_map: dict[str, list[str]] = {
            requirement.name: self._retrieve_relevant_evidence(
                requirement,
                resume_profile,
            )
            for requirement in candidate_requirements
        }

        # ----------------------------------------------------
        # Deterministic adjacency hints: for each candidate
        # requirement, check whether the resume shows evidence
        # of a known related-but-not-equivalent tool/technology
        # (e.g. Azure when AWS is required, or HubSpot when
        # Salesforce is required), via the static
        # ADJACENT_TECHNOLOGY_PAIRS table unioned with each
        # requirement's LLM-provided adjacent_alternatives. This
        # is a fixed lookup, not an LLM guess — it grounds
        # Gemini's "adjacent" judgment, and any evidence text it
        # finds is folded into the same evidence pool used for
        # grounding validation in _merge_verification.
        # ----------------------------------------------------

        adjacency_hints: dict[str, list[str]] = {}

        for requirement in candidate_requirements:

            technologies, evidence_lines = (
                self._detect_adjacency_hints(
                    requirement,
                    resume_profile,
                )
            )

            if not technologies:
                continue

            adjacency_hints[requirement.name] = technologies

            existing = evidence_map.setdefault(
                requirement.name,
                [],
            )

            for line in evidence_lines:
                if line not in existing:
                    existing.append(line)

        # ----------------------------------------------------
        # The per-requirement evidence_map above is a narrow,
        # retrieval-ranked subset — useful to focus Gemini's
        # attention, but retrieval (and even the structured
        # resume extraction itself) can miss real evidence
        # phrased in a way nothing anticipated. The complete
        # RAW resume text is also given as a shared reference
        # for the whole batch, so a genuinely relevant line
        # that never made it into the structured profile at all
        # can still be found and cited, instead of silently
        # causing a wrong "missing"/"ambiguous" outcome.
        # ----------------------------------------------------

        verifications = {}

        if candidate_requirements:

            verifications = (
                self.semantic_verifier.verify_batch(
                    requirements=candidate_requirements,
                    evidence_map=evidence_map,
                    adjacency_hints=adjacency_hints,
                    full_resume_text=resume_text,
                )
            )

        results: list[RequirementMatch] = []

        missing_dealbreakers: list[str] = []

        for requirement, preliminary_result in zip(
            jd_profile.requirements,
            preliminary_results,
        ):

            verification = verifications.get(
                requirement.name.strip().lower()
            )

            result = self._merge_verification(
                requirement,
                preliminary_result,
                verification,
                evidence_map.get(
                    requirement.name,
                    [],
                ),
                resume_text,
            )

            if (
                requirement.is_dealbreaker
                and result.match_type == "missing"
            ):

                missing_dealbreakers.append(
                    requirement.name
                )

            results.append(result)

        overall_score = self._calculate_overall_score(
            results
        )

        # ----------------------------------------------------
        # Dealbreaker gate: a real recruiter treats a missing
        # hard requirement (a required license, a hard years-
        # of-experience floor, work authorization) as an
        # override, not just one line item in a blended
        # average. If any JD-tagged dealbreaker requirement is
        # missing, cap the overall score regardless of how well
        # everything else matches, and surface why plainly
        # rather than leaving it as an unexplained low number.
        # ----------------------------------------------------

        dealbreaker_capped = bool(missing_dealbreakers)

        dealbreaker_reason = None

        if dealbreaker_capped:

            overall_score = min(
                overall_score,
                self.DEALBREAKER_SCORE_CEILING,
            )

            dealbreaker_reason = (
                "Score capped — missing required: "
                + "; ".join(missing_dealbreakers)
            )

        summary = self._build_summary(
            results
        )

        return MatchingReport(
            overall_score=round(
                overall_score,
                2,
            ),
            summary=summary,
            matches=results,
            dealbreaker_capped=dealbreaker_capped,
            dealbreaker_reason=dealbreaker_reason,
        )

    # --------------------------------------------------------
    # Requirement matching
    # --------------------------------------------------------

    def _match_requirement(
        self,
        requirement: JDRequirement,
        resume_profile: ResumeProfile,
    ) -> RequirementMatch:
        """
        Component-aware matching.

        A requirement is decomposed into one or more atomic
        components (either provided by the JD-structuring step,
        or derived deterministically by splitting compound
        names on "and"/"&"/"/"/","). Each component is searched
        independently across three controlled tiers — direct
        (exact/alias phrase), indirect (controlled concept ->
        evidence-keyword mapping), and fuzzy (conservative
        token overlap) — and the per-component results are
        aggregated conservatively: a compound requirement is
        never promoted to "strong" unless EVERY component has
        direct/indirect evidence.
        """

        components = self._resolve_components(
            requirement
        )

        component_results = [
            self._match_component(
                component,
                requirement,
                resume_profile,
            )
            for component in components
        ]

        return self._aggregate_component_results(
            requirement,
            components,
            component_results,
        )

    # --------------------------------------------------------
    # Component resolution
    # --------------------------------------------------------

    def _resolve_components(
        self,
        requirement: JDRequirement,
    ) -> list[str]:

        if requirement.components:

            resolved = [
                self._normalize(component)
                for component in requirement.components
                if component.strip()
            ]

            if resolved:
                return resolved

        parts = [
            part.strip()
            for part in self.COMPOUND_SPLIT_PATTERN.split(
                requirement.name
            )
            if part.strip()
        ]

        if len(parts) >= 2:

            return [
                self._normalize(part)
                for part in parts
            ]

        return [
            self._normalize(requirement.name)
        ]

    # --------------------------------------------------------
    # Per-component evidence tier search
    # --------------------------------------------------------

    def _match_component(
        self,
        component_name: str,
        requirement: JDRequirement,
        resume_profile: ResumeProfile,
    ) -> dict:
        """
        Returns {"tier", "score", "items", "terms"} for a
        single atomic component.

        Both the direct/alias/fuzzy search AND the controlled
        concept-hint search are evaluated, and the STRONGER of
        the two signals wins — a weak fuzzy hit (e.g. "web
        services" fuzzy-overlapping on the single word "web")
        must not block a much better controlled-concept hit
        (e.g. "REST API" appearing verbatim) from being used.
        """

        component_aliases = set(
            self.COMMON_ALIASES.get(
                component_name,
                set(),
            )
        )

        if len(
            self._resolve_components(requirement)
        ) == 1:

            component_aliases.update(
                self._normalize(alias)
                for alias in requirement.aliases
            )

        direct_terms = {
            component_name,
            *component_aliases,
        }

        direct_results = self._find_evidence(
            direct_terms,
            resume_profile,
        )

        candidates = []

        if direct_results:

            best = max(
                direct_results,
                key=lambda item: item["strength"],
            )

            if best["strength"] >= 1.0:
                tier = "direct"
            elif best["strength"] >= 0.70:
                tier = "partial"
            else:
                tier = "ambiguous"

            candidates.append(
                {
                    "tier": tier,
                    "score": self.TIER_SCORES[tier],
                    "items": direct_results,
                    "terms": direct_terms,
                }
            )

        # ------------------------------------------------
        # Controlled concept -> evidence-keyword mapping.
        # Only EXACT phrase hits against the controlled
        # evidence vocabulary count here; fuzzy matching
        # against a proxy term would be too noisy to trust
        # for an indirect signal.
        # ------------------------------------------------

        concept_terms = self._concept_hint_terms(
            component_name,
            requirement,
        )

        if concept_terms:

            concept_results = [
                item
                for item in self._find_evidence(
                    concept_terms,
                    resume_profile,
                )
                if item["strength"] >= 1.0
            ]

            if concept_results:

                candidates.append(
                    {
                        "tier": "indirect",
                        "score": self.TIER_SCORES["indirect"],
                        "items": concept_results,
                        "terms": concept_terms,
                    }
                )

        if not candidates:

            return {
                "tier": "unsupported",
                "score": self.TIER_SCORES["unsupported"],
                "items": [],
                "terms": direct_terms,
            }

        return max(
            candidates,
            key=lambda candidate: candidate["score"],
        )

    def _concept_hint_terms(
        self,
        normalized_component: str,
        requirement: JDRequirement,
    ) -> set[str]:

        matched_terms: set[str] = set()

        for entry in self.CONCEPT_EVIDENCE_HINTS:

            if any(
                trigger in normalized_component
                or normalized_component in trigger
                for trigger in entry["triggers"]
            ):

                matched_terms.update(
                    entry["evidence_terms"]
                )

        # ------------------------------------------------
        # Domain-general supplement: the JD-structuring LLM
        # call already generates per-requirement evidence_hints
        # (e.g. "renewals", "upsells" for a sales CRM
        # requirement) — this covers domains the static
        # CONCEPT_EVIDENCE_HINTS table above has no vocabulary
        # for. Gated to single-component requirements, mirroring
        # the requirement.aliases gating in _match_component, so
        # a compound requirement's hints don't leak uniformly
        # across sub-concepts they don't actually describe.
        # ------------------------------------------------

        if len(self._resolve_components(requirement)) == 1:

            matched_terms.update(
                self._normalize(hint)
                for hint in requirement.evidence_hints
            )

        return matched_terms

    # --------------------------------------------------------
    # Evidence retrieval (for ambiguous requirements only)
    # --------------------------------------------------------

    def _retrieve_relevant_evidence(
        self,
        requirement: JDRequirement,
        resume_profile: ResumeProfile,
        limit: int = 8,
    ) -> list[str]:
        """
        Retrieves the top-K most relevant resume evidence lines
        for a requirement, using a broader term pool than the
        tier-gated matching above (includes weak fuzzy hits).

        This is a RETRIEVAL step, not a matching decision — the
        goal is to hand Gemini a small, focused evidence set
        instead of the entire resume, so semantic verification
        stays cheap, grounded, and easy to validate. Presence in
        this list does not imply the requirement is satisfied.
        """

        components = self._resolve_components(
            requirement
        )

        search_terms: set[str] = set()

        for component in components:

            search_terms.add(component)

            search_terms.update(
                self.COMMON_ALIASES.get(
                    component,
                    set(),
                )
            )

            search_terms.update(
                self._concept_hint_terms(
                    component,
                    requirement,
                )
            )

            # --------------------------------------------------
            # Critical for adjacency detection to ever trigger:
            # without this, a "missing" requirement whose ONLY
            # resume overlap is an adjacent-but-different tool
            # (e.g. JD wants AWS, resume only has Azure) never
            # retrieves any evidence, never qualifies as a
            # candidate for semantic verification, and
            # _detect_adjacency_hints is never even called for
            # it — it stays hard-"missing" forever. This is
            # still pure retrieval breadth, not a matching
            # decision: zero LLM calls, zero effect on Pass 1
            # tier classification.
            # --------------------------------------------------

            for pair in self.ADJACENT_TECHNOLOGY_PAIRS:

                if component in pair:
                    search_terms.update(
                        pair - {component}
                    )

        search_terms.update(
            self._normalize(alternative)
            for alternative in requirement.adjacent_alternatives
        )

        if len(components) == 1:

            search_terms.update(
                self._normalize(alias)
                for alias in requirement.aliases
            )

        candidates = self._find_evidence(
            search_terms,
            resume_profile,
        )

        ranked = sorted(
            candidates,
            key=lambda item: -item["strength"],
        )

        seen: set[str] = set()
        results: list[str] = []

        for item in ranked:

            key = self._normalize(
                item["source_text"]
            )

            if key in seen:
                continue

            seen.add(key)

            results.append(
                item["source_text"]
            )

            if len(results) >= limit:
                break

        if results:
            return results

        # --------------------------------------------------------
        # No keyword-level signal at all. For CONTEXTUAL
        # requirements only, fall back to a small generic sample
        # of resume bullets as background context — genuinely
        # contextual evidence (e.g. "learned an unfamiliar
        # system") may not contain any of our controlled trigger
        # phrases, so Gemini still deserves a look at what the
        # resume actually says before this is called Missing.
        # This is still just RETRIEVAL, not a match decision.
        # --------------------------------------------------------

        if requirement.category not in self.CONTEXTUAL_CATEGORIES:
            return []

        generic_candidates: list[str] = []

        for experience in resume_profile.experience:

            for bullet in experience.bullets:
                generic_candidates.append(bullet.text)

        for project in resume_profile.projects:

            for bullet in project.bullets:
                generic_candidates.append(bullet.text)

        fallback_seen: set[str] = set()
        fallback_results: list[str] = []

        for text in generic_candidates:

            key = self._normalize(text)

            if key in fallback_seen:
                continue

            fallback_seen.add(key)
            fallback_results.append(text)

            if len(fallback_results) >= min(limit, 5):
                break

        return fallback_results

    # --------------------------------------------------------
    # Adjacency hint detection (for candidate requirements only)
    # --------------------------------------------------------

    def _detect_adjacency_hints(
        self,
        requirement: JDRequirement,
        resume_profile: ResumeProfile,
    ) -> tuple[list[str], list[str]]:
        """
        Checks whether the resume shows evidence of a tool or
        technology that is related-but-not-equivalent to one of
        this requirement's components, per
        ADJACENT_TECHNOLOGY_PAIRS (e.g. Azure evidence when the
        requirement is AWS) UNIONED with the JD-structuring
        LLM's own per-requirement adjacent_alternatives (e.g.
        HubSpot when the requirement is Salesforce) — the static
        table remains a free, zero-cost baseline for well-known
        tech pairs, while adjacent_alternatives extends the same
        mechanism to any domain the static table has no
        vocabulary for.

        Returns (technology_names_detected, evidence_lines). The
        technology names feed a hint line into the semantic-
        verification prompt; the evidence lines are merged into
        the requirement's evidence pool so any "adjacent"
        citation Gemini makes can survive grounding validation
        in _merge_verification.

        This is deterministic, code-computed evidence — not the
        LLM's own free-form inference at match time — which is
        what keeps the "adjacent" judgment grounded.
        """

        components = self._resolve_components(
            requirement
        )

        candidate_technologies: set[str] = set()

        for component in components:

            for pair in self.ADJACENT_TECHNOLOGY_PAIRS:

                if component in pair:
                    candidate_technologies.update(
                        pair - {component}
                    )

        candidate_technologies.update(
            self._normalize(alternative)
            for alternative in requirement.adjacent_alternatives
        )

        detected_technologies: list[str] = []
        evidence_lines: list[str] = []

        for technology in candidate_technologies:

            matches = [
                item
                for item in self._find_evidence(
                    {technology},
                    resume_profile,
                )
                if item["strength"] >= 1.0
            ]

            if not matches:
                continue

            if technology not in detected_technologies:
                detected_technologies.append(technology)

            for item in matches:

                if item["source_text"] not in evidence_lines:
                    evidence_lines.append(
                        item["source_text"]
                    )

        return detected_technologies, evidence_lines

    # --------------------------------------------------------
    # Aggregation across components
    # --------------------------------------------------------

    def _aggregate_component_results(
        self,
        requirement: JDRequirement,
        components: list[str],
        component_results: list[dict],
    ) -> RequirementMatch:

        tiers = [
            result["tier"]
            for result in component_results
        ]

        strong_tiers = {"direct", "indirect"}

        evidenced_tiers = {"direct", "indirect", "partial"}

        # ------------------------------------------------
        # No evidence anywhere, for any component, in any
        # tier — this is now a much stronger "missing"
        # signal than before, since the search itself
        # covers direct, alias, fuzzy AND controlled
        # concept evidence.
        # ------------------------------------------------

        if all(
            tier == "unsupported"
            for tier in tiers
        ):

            # ------------------------------------------------
            # For CONTEXTUAL requirements (soft skills,
            # responsibilities), zero keyword-level overlap
            # does NOT prove the requirement is unsupported —
            # per Part 3/4, these should not be decided by
            # keyword matching alone. Route them into the
            # batched semantic-verification pool instead of
            # deterministically declaring them missing. This
            # costs no extra Gemini calls (still one shared
            # batched call) — it only adds this requirement's
            # block to that call.
            #
            # Objective/technical requirements are NOT routed
            # here: for those, keyword absence genuinely does
            # mean the skill wasn't mentioned.
            # ------------------------------------------------

            if requirement.category in self.CONTEXTUAL_CATEGORIES:

                return self._build_match(
                    requirement=requirement,
                    match_type="ambiguous",
                    evidence_type="ambiguous",
                    strength=0.0,
                    confidence=0.0,
                    components=components,
                    component_results=component_results,
                    reason=(
                        "No keyword-level evidence was found "
                        f"for {requirement.name}, but this is a "
                        "contextual requirement, so it is being "
                        "reviewed for indirect or implied "
                        "evidence before being classified."
                    ),
                )

            return self._build_match(
                requirement=requirement,
                match_type="missing",
                evidence_type="unsupported",
                strength=0.0,
                confidence=0.0,
                components=components,
                component_results=component_results,
                reason=(
                    self._missing_reason(
                        requirement
                    )
                ),
            )

        # ------------------------------------------------
        # Every component has at least "partial" evidence
        # (no component is unsupported, and none is stuck
        # at the weak/fuzzy "ambiguous" tier) — a clean,
        # deterministic signal that needs no Gemini call.
        # ------------------------------------------------

        if all(
            tier in evidenced_tiers
            for tier in tiers
        ):

            strength = sum(
                result["score"]
                for result in component_results
            ) / len(component_results)

            confidence = self._aggregate_confidence(
                component_results
            )

            if all(
                tier in strong_tiers
                for tier in tiers
            ):

                match_type = "strong"

                evidence_type = (
                    "direct"
                    if all(
                        tier == "direct"
                        for tier in tiers
                    )
                    else "indirect"
                )

            else:

                match_type = "partial"
                evidence_type = "partial"

            return self._build_match(
                requirement=requirement,
                match_type=match_type,
                evidence_type=evidence_type,
                strength=strength,
                confidence=confidence,
                components=components,
                component_results=component_results,
                reason=self._matched_reason(
                    requirement,
                    components,
                    component_results,
                    match_type,
                ),
            )

        # ------------------------------------------------
        # Mixed signal: some components are fully
        # unsupported while others have real evidence, and
        # none of the evidenced components are only weak
        # fuzzy hits. This is deterministically explainable
        # (we know exactly which half is missing) so it
        # does not need Gemini either.
        # ------------------------------------------------

        if not any(
            tier == "ambiguous"
            for tier in tiers
        ):

            strength = sum(
                result["score"]
                for result in component_results
            ) / len(component_results)

            confidence = self._aggregate_confidence(
                component_results
            )

            return self._build_match(
                requirement=requirement,
                match_type="partial",
                evidence_type="partial",
                strength=strength,
                confidence=confidence,
                components=components,
                component_results=component_results,
                reason=self._matched_reason(
                    requirement,
                    components,
                    component_results,
                    "partial",
                ),
            )

        # ------------------------------------------------
        # At least one component's best evidence is only a
        # weak/fuzzy match. The deterministic layer found
        # something but cannot confidently classify it —
        # this is exactly the case the batched semantic
        # verifier exists for.
        # ------------------------------------------------

        strength = sum(
            result["score"]
            for result in component_results
        ) / len(component_results)

        return self._build_match(
            requirement=requirement,
            match_type="ambiguous",
            evidence_type="ambiguous",
            strength=strength,
            confidence=0.0,
            components=components,
            component_results=component_results,
            reason=(
                "The resume contains potentially related "
                f"evidence for {requirement.name}, but it "
                "is not sufficiently explicit."
            ),
        )

    def _aggregate_confidence(
        self,
        component_results: list[dict],
    ) -> float:

        supported = [
            result
            for result in component_results
            if result["tier"] != "unsupported"
        ]

        if not supported:
            return 0.0

        per_component_confidence = []

        for result in supported:

            raw_confidence = max(
                (
                    item["confidence"]
                    for item in result["items"]
                ),
                default=0.0,
            )

            ceiling = self.TIER_CONFIDENCE_CEILING[
                result["tier"]
            ]

            per_component_confidence.append(
                min(
                    raw_confidence,
                    ceiling,
                )
            )

        confidence = sum(
            per_component_confidence
        ) / len(
            per_component_confidence
        )

        # ------------------------------------------------
        # Breadth penalty: a broad requirement satisfied
        # by only ONE piece of evidence should not receive
        # the same confidence as one corroborated by
        # several independent bullets.
        #
        # Evidence extraction can record the same underlying
        # resume line more than once (e.g. once as a
        # top-level profile.evidence claim and once as a
        # synthesized experience/project bullet), so breadth
        # is measured by DISTINCT source text, not raw item
        # count — otherwise a single resume line could look
        # like multiple independent corroborations.
        # ------------------------------------------------

        distinct_sources = {
            self._normalize(item["source_text"])
            for result in component_results
            for item in result["items"]
        }

        total_evidence_items = len(
            distinct_sources
        )

        if total_evidence_items == 1:
            confidence *= 0.9

        return confidence

    def _build_match(
        self,
        requirement: JDRequirement,
        match_type: str,
        evidence_type: str,
        strength: float,
        confidence: float,
        components: list[str],
        component_results: list[dict],
        reason: str,
    ) -> RequirementMatch:

        all_terms: set[str] = set()

        for result in component_results:
            all_terms.update(result["terms"])

        matched_evidence = list(
            dict.fromkeys(
                item["source_text"]
                for result in component_results
                for item in result["items"]
            )
        )

        matched_sections = list(
            dict.fromkeys(
                item["section"]
                for result in component_results
                for item in result["items"]
            )
        )

        score = (
            strength
            * confidence
            * 100
        )

        return RequirementMatch(
            requirement=requirement.name,
            category=requirement.category,
            importance=requirement.importance,
            weight=requirement.weight,
            match_type=match_type,
            evidence_type=evidence_type,
            match_strength=round(
                strength,
                3,
            ),
            evidence_confidence=round(
                confidence,
                3,
            ),
            score=round(
                score,
                2,
            ),
            matched_resume_evidence=matched_evidence,
            matched_resume_sections=matched_sections,
            reason=reason,
            aliases_considered=sorted(
                all_terms
            ),
        )

    def _missing_reason(
        self,
        requirement: JDRequirement,
    ) -> str:

        return (
            "No direct, controlled-concept, or fuzzy "
            f"evidence for {requirement.name} was found "
            "anywhere in the structured resume evidence "
            "(summary, experience, projects, skills, "
            "education, certifications)."
        )

    def _matched_reason(
        self,
        requirement: JDRequirement,
        components: list[str],
        component_results: list[dict],
        match_type: str,
    ) -> str:

        if len(components) == 1:

            tier = component_results[0]["tier"]

            if match_type == "strong":

                return (
                    f"The resume provides {tier} evidence "
                    f"for {requirement.name}."
                )

            return (
                f"The resume provides {tier} evidence for "
                f"{requirement.name}, but it is not strong "
                "enough to classify as a full match."
            )

        supported = [
            component
            for component, result in zip(
                components,
                component_results,
            )
            if result["tier"] != "unsupported"
        ]

        unsupported = [
            component
            for component, result in zip(
                components,
                component_results,
            )
            if result["tier"] == "unsupported"
        ]

        if unsupported:

            return (
                f"{requirement.name} combines multiple "
                f"concepts. The resume supports "
                f"{', '.join(supported)}, but shows no "
                f"evidence for {', '.join(unsupported)}."
            )

        return (
            f"{requirement.name} combines multiple "
            "concepts, and the resume provides evidence "
            f"for all of them: {', '.join(supported)}."
        )

    # --------------------------------------------------------
    # Evidence search
    # --------------------------------------------------------

    def _find_evidence(
        self,
        candidate_terms: set[str],
        resume_profile: ResumeProfile,
    ) -> list[dict]:

        results = []

        all_evidence = list(
            resume_profile.evidence
        )

        for skill in resume_profile.skills:

            all_evidence.extend(
                skill.evidence
            )

        for experience in resume_profile.experience:

            for bullet in experience.bullets:

                all_evidence.append(
                    ResumeEvidence(
                        claim=bullet.text,
                        category="responsibility",
                        source_text=bullet.text,
                        section="experience",
                        confidence=0.90,
                    )
                )

        for project in resume_profile.projects:

            for bullet in project.bullets:

                all_evidence.append(
                    ResumeEvidence(
                        claim=bullet.text,
                        category="project",
                        source_text=bullet.text,
                        section="projects",
                        confidence=0.90,
                    )
                )

        for evidence in all_evidence:

            source = self._normalize(
                evidence.source_text
            )

            claim = self._normalize(
                evidence.claim
            )

            strength = self._calculate_match_strength(
                candidate_terms,
                source,
                claim,
            )

            if strength > 0:

                results.append(
                    {
                        "strength": strength,
                        "confidence": evidence.confidence,
                        "source_text": evidence.source_text,
                        "section": evidence.section,
                    }
                )

        return results

    # --------------------------------------------------------
    # Match strength
    # --------------------------------------------------------

    def _calculate_match_strength(
        self,
        candidate_terms: set[str],
        source_text: str,
        claim: str,
    ) -> float:

        # ----------------------------------------------------
        # Exact phrase match
        # ----------------------------------------------------

        for term in candidate_terms:

            if not term:
                continue

            if self._contains_phrase(
                source_text,
                term,
            ):
                return 1.0

            if self._contains_phrase(
                claim,
                term,
            ):
                return 1.0

        # ----------------------------------------------------
        # Token-based matching
        # ----------------------------------------------------

        source_tokens = set(
            self._tokenize(source_text)
        )

        claim_tokens = set(
            self._tokenize(claim)
        )

        best_similarity = 0.0

        for term in candidate_terms:

            term_tokens = set(
                self._tokenize(term)
            )

            if not term_tokens:
                continue

            source_overlap = (
                len(
                    term_tokens
                    & source_tokens
                )
                / len(term_tokens)
            )

            claim_overlap = (
                len(
                    term_tokens
                    & claim_tokens
                )
                / len(term_tokens)
            )

            overlap = max(
                source_overlap,
                claim_overlap,
            )

            best_similarity = max(
                best_similarity,
                overlap,
            )

        # ----------------------------------------------------
        # Conservative fuzzy matching
        # ----------------------------------------------------

        if best_similarity >= 0.8:

            return 0.70

        if best_similarity >= 0.5:

            return 0.45

        return 0.0

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    def _calculate_overall_score(
        self,
        results: list[RequirementMatch],
    ) -> float:

        if not results:
            return 0.0

        weighted_score = 0.0
        total_weight = 0.0

        for result in results:

            importance_multiplier = (
                self.IMPORTANCE_MULTIPLIERS.get(
                    result.importance,
                    0.50,
                )
            )

            if (
                result.category == "other"
                and result.importance == "required"
            ):
                category_multiplier = 1.00
            else:
                category_multiplier = (
                    self.CATEGORY_MULTIPLIERS.get(
                        result.category,
                        0.50,
                    )
                )

            effective_weight = (
                result.weight
                * importance_multiplier
                * category_multiplier
            )

            weighted_score += (
                result.match_strength
                * result.evidence_confidence
                * effective_weight
            )

            total_weight += effective_weight

        if total_weight == 0:

            return 0.0

        return (
            weighted_score
            / total_weight
        ) * 100

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def _build_summary(
        self,
        results: list[RequirementMatch],
    ) -> MatchingSummary:

        strong = sum(
            1
            for result in results
            if result.match_type == "strong"
        )

        partial = sum(
            1
            for result in results
            if result.match_type == "partial"
        )

        ambiguous = sum(
            1
            for result in results
            if result.match_type == "ambiguous"
        )

        missing = sum(
            1
            for result in results
            if result.match_type == "missing"
        )

        required_results = [
            result
            for result in results
            if result.importance == "required"
        ]

        preferred_results = [
            result
            for result in results
            if result.importance == "preferred"
        ]

        required_matched = sum(
            1
            for result in required_results
            if result.match_type == "strong"
        )

        preferred_matched = sum(
            1
            for result in preferred_results
            if result.match_type == "strong"
        )

        return MatchingSummary(
            total_requirements=len(
                results
            ),
            strong_matches=strong,
            partial_matches=partial,
            ambiguous_matches=ambiguous,
            missing_matches=missing,
            required_requirements=len(
                required_results
            ),
            required_matched=required_matched,
            preferred_requirements=len(
                preferred_results
            ),
            preferred_matched=preferred_matched,
        )

    # --------------------------------------------------------
    # Text utilities
    # --------------------------------------------------------

    @staticmethod
    def _normalize(text: str) -> str:

        text = text.lower().strip()

        text = (
            text
            .replace("–", "-")
            .replace("—", "-")
            .replace("_", " ")
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    @staticmethod
    def _tokenize(text: str) -> list[str]:

        return re.findall(
            r"[a-z0-9+#./-]+",
            text.lower(),
        )

    @staticmethod
    def _contains_phrase(
        text: str,
        phrase: str,
    ) -> bool:

        text = text.lower()
        phrase = phrase.lower()

        pattern = (
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)"
        )

        return bool(
            re.search(
                pattern,
                text,
            )
        )
    def _merge_verification(
        self,
        requirement: JDRequirement,
        preliminary_result: RequirementMatch,
        verification,
        retrieved_evidence: list[str],
        resume_text: str = "",
    ) -> RequirementMatch:
        """
        Merges a batched SemanticVerification result (or None,
        if Gemini did not return a verification for this
        requirement) back into a RequirementMatch.

        This performs no Gemini calls itself — verification is
        produced once, up front, for every ambiguous requirement
        in the analysis via SemanticVerifier.verify_batch().

        `retrieved_evidence` is the narrow per-requirement hint
        pool given to Gemini; `resume_text` is the complete raw
        resume text also given to Gemini for this requirement
        (see SemanticVerifier.verify_batch). Any
        "supporting_evidence" string Gemini returns that does
        NOT correspond to something in `retrieved_evidence` AND
        is NOT a real substring of `resume_text` is treated as
        hallucinated and dropped before it can influence the
        result (evidence-grounding validation).
        """

        # --------------------------------------------------------
        # Stage 1 floor: every requirement now goes through this
        # holistic pass, including ones Pass 1 already resolved
        # with high confidence via an exact literal phrase/alias
        # hit. That confirmed result can be upgraded by this pass
        # (a "strong" direct match can't get any stronger, but a
        # weaker preliminary result can still be improved below),
        # but it must never be downgraded by an inference — or,
        # worse, silently dropped to "missing" just because this
        # requirement's verification happened to go missing from
        # Gemini's response (a malformed chunk, a name-echo
        # mismatch). A confirmed literal match is a fact, not a
        # judgment call, and outranks anything Pass 2 says.
        # --------------------------------------------------------

        if (
            preliminary_result.evidence_type == "direct"
            and preliminary_result.match_type == "strong"
        ):

            return preliminary_result

        # --------------------------------------------------------
        # Conservative fallback: if Gemini did not return a
        # verification for this requirement at all, do not
        # silently upgrade it — treat it the same as
        # "insufficient evidence".
        # --------------------------------------------------------

        if verification is None:

            return RequirementMatch(
                requirement=requirement.name,
                category=requirement.category,
                importance=requirement.importance,
                weight=requirement.weight,
                match_type="missing",
                evidence_type="unsupported",
                match_strength=0.0,
                evidence_confidence=0.0,
                score=0.0,
                matched_resume_evidence=[],
                matched_resume_sections=[],
                reason=(
                    "Semantic verification did not return a "
                    "result for this requirement, so it is "
                    "conservatively treated as unsupported."
                ),
                aliases_considered=(
                    preliminary_result.aliases_considered
                ),
            )

        # --------------------------------------------------------
        # Evidence-grounding validation: every piece of
        # "supporting_evidence" Gemini cites must correspond to
        # something actually in the retrieved evidence pool we
        # gave it. Anything else is hallucinated and is dropped
        # before it can influence the result.
        # --------------------------------------------------------

        normalized_pool = {
            self._normalize(item)
            for item in retrieved_evidence
        }

        normalized_resume_text = self._normalize(
            resume_text
        )

        supporting_evidence = [
            item
            for item in verification.supporting_evidence
            if any(
                self._normalize(item) in pool_item
                or pool_item in self._normalize(item)
                for pool_item in normalized_pool
            )
            or (
                self._normalize(item)
                in normalized_resume_text
            )
        ]

        # --------------------------------------------------------
        # Safety rule:
        #
        # Gemini cannot promote a requirement to STRONG unless
        # it actually provides supporting evidence that survived
        # grounding validation above.
        # --------------------------------------------------------

        if not supporting_evidence:

            return RequirementMatch(
                requirement=requirement.name,
                category=requirement.category,
                importance=requirement.importance,
                weight=requirement.weight,
                match_type="missing",
                evidence_type="unsupported",
                match_strength=0.0,
                evidence_confidence=0.0,
                score=0.0,
                matched_resume_evidence=[],
                matched_resume_sections=[],
                reason=(
                    "The resume contains potentially related "
                    "information, but there is insufficient "
                    "evidence to establish this requirement."
                ),
                aliases_considered=(
                    preliminary_result.aliases_considered
                ),
            )

        # --------------------------------------------------------
        # Conservative semantic strength.
        #
        # A semantically-verified match is inherently an
        # inferred judgment call, not a literal phrase hit —
        # it is labeled "indirect" rather than "direct" even
        # when the decision is "strong".
        # --------------------------------------------------------

        if verification.decision == "strong":

            ceiling = 0.90

            match_type = "strong"
            evidence_type = "indirect"

        elif verification.decision == "partial":

            ceiling = 0.65

            match_type = "partial"
            evidence_type = "partial"

        elif verification.decision == "adjacent":

            # Real, grounded evidence of a DIFFERENT (but
            # related, per ADJACENT_TECHNOLOGY_PAIRS or a
            # well-established same-category adjacency)
            # technology than the one required — e.g. Azure
            # experience against an AWS requirement. Deliberately
            # mapped into match_type "partial" (so every existing
            # match_type-keyed consumer needs no changes) but
            # kept numerically well below same-skill partial
            # credit via a much lower ceiling, and distinguished
            # via evidence_type "adjacent" for anyone inspecting
            # the breakdown.

            ceiling = 0.35

            match_type = "partial"
            evidence_type = "adjacent"

        else:

            # Covers both an explicit "missing" decision and
            # Gemini's own "ambiguous" decision. Final match
            # classifications are only strong/partial/missing —
            # if even semantic verification can't confidently
            # place a requirement, the conservative outcome is
            # missing, not a further terminal state.

            ceiling = 0.0
            match_type = "missing"
            evidence_type = "unsupported"

        # ------------------------------------------------
        # Both the strength AND the confidence exposed to
        # the candidate are capped by the same ceiling — an
        # LLM-inferred judgment should never surface as a
        # falsely precise number (e.g. "92% confidence")
        # just because Gemini's raw response said so.
        # ------------------------------------------------

        strength = min(
            ceiling,
            verification.confidence,
        )

        confidence = min(
            ceiling,
            verification.confidence,
        )

        score = (
            strength
            * confidence
            * 100
        )

        return RequirementMatch(
            requirement=requirement.name,
            category=requirement.category,
            importance=requirement.importance,
            weight=requirement.weight,
            match_type=match_type,
            evidence_type=evidence_type,
            match_strength=round(
                strength,
                3,
            ),
            evidence_confidence=round(
                confidence,
                3,
            ),
            score=round(
                score,
                2,
            ),
            matched_resume_evidence=(
                supporting_evidence
            ),
            matched_resume_sections=[],
            reason=verification.reasoning,
            aliases_considered=(
                preliminary_result.aliases_considered
            ),
        )
