from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# JOB DESCRIPTION SCHEMAS
# ============================================================

class JDRequirement(BaseModel):
    name: str

    category: Literal[
        "technical_skill",
        "soft_skill",
        "responsibility",
        "experience",
        "education",
        "certification",
        "domain",
        "tool",
        "other",
    ]

    importance: Literal[
        "required",
        "preferred",
        "nice_to_have",
        "unclear",
    ]

    weight: int = Field(
        ge=1,
        le=10
    )

    evidence: list[str] = Field(
        default_factory=list
    )

    aliases: list[str] = Field(
        default_factory=list,
        description=(
            "Alternate names/spellings/abbreviations for this "
            "requirement that mean the SAME thing (e.g. "
            "'PostgreSQL' <-> 'Postgres', 'CRM' <-> 'Customer "
            "Relationship Management'). Do NOT include related-"
            "but-different terms here — use "
            "adjacent_alternatives for those."
        ),
    )

    components: list[str] = Field(
        default_factory=list,
        description=(
            "Atomic sub-concepts of a compound requirement "
            "(e.g. 'Frontend Technologies & Web Services' -> "
            "['frontend technologies', 'web services']). "
            "Empty when the requirement already names a single "
            "concept."
        ),
    )

    adjacent_alternatives: list[str] = Field(
        default_factory=list,
        description=(
            "Tools/platforms/frameworks/standards that are "
            "RELATED to this requirement but NOT equivalent or "
            "interchangeable substitutes for it — e.g. for "
            "'Salesforce': 'hubspot', 'zoho crm'; for 'AWS': "
            "'azure', 'gcp'; for 'GAAP': 'ifrs'. Used only to "
            "detect adjacent-but-not-matching resume "
            "experience, never to award credit for this "
            "requirement. Leave empty if no well-known adjacent "
            "alternative exists (e.g. for a general "
            "experience/years requirement)."
        ),
    )

    evidence_hints: list[str] = Field(
        default_factory=list,
        description=(
            "Short literal resume phrases (2-5 words) that "
            "would count as indirect/supporting evidence for "
            "this requirement even if the requirement's own "
            "name/aliases never appear verbatim — e.g. for "
            "'Client Relationship Management': 'account "
            "management', 'renewals', 'upsells', 'client "
            "retention'. These are SEARCH TERMS only; a resume "
            "must still contain the literal phrase to count as "
            "a match. Leave empty for requirements that are "
            "already a concrete named tool (e.g. 'Salesforce', "
            "'Python') where a direct-name match is sufficient."
        ),
    )

    is_dealbreaker: bool = Field(
        default=False,
        description=(
            "True only for a genuine hard gate a real recruiter "
            "would screen out on if missing — an explicit "
            "years-of-experience floor, a required license or "
            "certification, work authorization/clearance. False "
            "for every other 'required' requirement (most "
            "required skills are important but not a hard gate "
            "on their own)."
        ),
    )


class JDProfile(BaseModel):
    job_title: str | None = None

    seniority: str | None = None

    domain: str | None = None

    summary: str

    responsibilities: list[str] = Field(
        default_factory=list
    )

    requirements: list[JDRequirement] = Field(
        default_factory=list
    )

    keywords: list[str] = Field(
        default_factory=list
    )

    soft_skills: list[str] = Field(
        default_factory=list
    )

    education_requirements: list[str] = Field(
        default_factory=list
    )

    certification_requirements: list[str] = Field(
        default_factory=list
    )


# ============================================================
# RESUME EVIDENCE SCHEMAS
# ============================================================

class ResumeMetric(BaseModel):
    value: str

    metric_type: Literal[
        "percentage",
        "count",
        "time",
        "scale",
        "performance",
        "financial",
        "ranking",
        "other",
    ]

    context: str

    source_text: str


class ResumeEvidence(BaseModel):
    claim: str

    category: Literal[
        "skill",
        "technology",
        "responsibility",
        "achievement",
        "experience",
        "project",
        "education",
        "certification",
        "soft_skill",
        "other",
    ]

    source_text: str

    section: Literal[
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
        "other",
    ]

    confidence: float = Field(
        ge=0,
        le=1
    )


class ResumeSkill(BaseModel):
    name: str

    category: Literal[
        "programming_language",
        "framework",
        "library",
        "database",
        "cloud",
        "devops",
        "tool",
        "domain",
        "soft_skill",
        "platform_or_system",
        "methodology_or_standard",
        "other",
    ]

    aliases: list[str] = Field(
        default_factory=list
    )

    evidence: list[ResumeEvidence] = Field(
        default_factory=list
    )


class ResumeBullet(BaseModel):
    text: str

    action_verbs: list[str] = Field(
        default_factory=list
    )

    technologies: list[str] = Field(
        default_factory=list
    )

    metrics: list[ResumeMetric] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )

    jd_relevant_claims: list[str] = Field(
        default_factory=list
    )


class ResumeProject(BaseModel):
    name: str

    description: str | None = None

    technologies: list[str] = Field(
        default_factory=list
    )

    bullets: list[ResumeBullet] = Field(
        default_factory=list
    )


class ResumeExperience(BaseModel):
    role: str

    company: str | None = None

    duration: str | None = None

    bullets: list[ResumeBullet] = Field(
        default_factory=list
    )


class ResumeEducation(BaseModel):
    degree: str

    institution: str | None = None

    duration: str | None = None

    details: list[str] = Field(
        default_factory=list
    )


class ResumeProfile(BaseModel):
    summary: str | None = None

    skills: list[ResumeSkill] = Field(
        default_factory=list
    )

    experience: list[ResumeExperience] = Field(
        default_factory=list
    )

    projects: list[ResumeProject] = Field(
        default_factory=list
    )

    education: list[ResumeEducation] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )

    metrics: list[ResumeMetric] = Field(
        default_factory=list
    )

    evidence: list[ResumeEvidence] = Field(
        default_factory=list
    )
    
# ============================================================
# MATCHING SCHEMAS
# ============================================================

class RequirementMatch(BaseModel):
    requirement: str

    category: str

    importance: str

    weight: int

    match_type: Literal[
        "strong",
        "partial",
        "missing",
        "ambiguous",
    ]

    evidence_type: Literal[
        "direct",
        "indirect",
        "partial",
        "ambiguous",
        "unsupported",
        "adjacent",
    ] = "unsupported"

    match_strength: float = Field(
        ge=0,
        le=1,
    )

    evidence_confidence: float = Field(
        ge=0,
        le=1,
    )

    score: float = Field(
        ge=0,
        le=100,
    )

    matched_resume_evidence: list[str] = Field(
        default_factory=list
    )

    matched_resume_sections: list[str] = Field(
        default_factory=list
    )

    reason: str

    aliases_considered: list[str] = Field(
        default_factory=list
    )


class MatchingSummary(BaseModel):
    total_requirements: int

    strong_matches: int

    partial_matches: int

    ambiguous_matches: int

    missing_matches: int

    required_requirements: int

    required_matched: int

    preferred_requirements: int

    preferred_matched: int


class MatchingReport(BaseModel):
    overall_score: float = Field(
        ge=0,
        le=100,
    )

    summary: MatchingSummary

    matches: list[RequirementMatch] = Field(
        default_factory=list
    )

    dealbreaker_capped: bool = False

    dealbreaker_reason: str | None = None


# ============================================================
# SEMANTIC VERIFICATION SCHEMAS
# ============================================================

class SemanticVerification(BaseModel):
    requirement_name: str

    decision: Literal[
        "strong",
        "partial",
        "missing",
        "ambiguous",
        "adjacent",
    ]

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reasoning: str

    supporting_evidence: list[str] = Field(
        default_factory=list
    )

    unsupported_assumptions: list[str] = Field(
        default_factory=list
    )


class SemanticVerificationBatch(BaseModel):
    """
    Response schema for a single batched Gemini call that
    verifies every ambiguous requirement for one analysis
    at once, instead of one Gemini call per requirement.
    """

    verifications: list[SemanticVerification] = Field(
        default_factory=list
    )

# ============================================================
# RESUME OPTIMIZATION SCHEMAS
# ============================================================

class OptimizationFinding(BaseModel):
    finding_type: Literal[
        "missing_keyword",
        "weak_keyword_context",
        "weak_action_verb",
        "missing_metric",
        "weak_impact",
        "low_specificity",
        "keyword_stuffing",
        "redundancy",
        "formatting",
    ]

    priority: Literal[
        "critical",
        "high",
        "medium",
        "low",
    ]

    impact_score: float = Field(
        ge=0,
        le=100,
    )

    section: str

    original_text: str

    jd_requirement: str | None = None

    evidence: list[str] = Field(
        default_factory=list
    )

    explanation: str

    safe_to_rewrite: bool = True


class KeywordCoverage(BaseModel):
    keyword: str

    importance: str

    weight: int

    present: bool

    contextual: bool

    occurrences: int

    evidence: list[str] = Field(
        default_factory=list
    )


class BulletQuality(BaseModel):
    text: str

    section: str

    action_score: float = Field(
        ge=0,
        le=100,
    )

    quantification_score: float = Field(
        ge=0,
        le=100,
    )

    impact_score: float = Field(
        ge=0,
        le=100,
    )

    specificity_score: float = Field(
        ge=0,
        le=100,
    )

    jd_relevance_score: float = Field(
        ge=0,
        le=100,
    )

    overall_score: float = Field(
        ge=0,
        le=100,
    )


class OptimizationReport(BaseModel):
    optimization_score: float = Field(
        ge=0,
        le=100,
    )

    keyword_coverage: list[KeywordCoverage] = Field(
        default_factory=list
    )

    bullet_quality: list[BulletQuality] = Field(
        default_factory=list
    )

    findings: list[OptimizationFinding] = Field(
        default_factory=list
    )
    
# ============================================================
# TRUTH-SAFE RECOMMENDATION SCHEMAS
# ============================================================
class RecommendationDraft(BaseModel):
    """
    Untrusted recommendation produced by Gemini.

    This model intentionally does NOT contain:
    - safety_status
    - confidence

    Those fields are calculated locally by Python
    after independent validation.
    """

    original_text: str

    suggested_text: str

    change_type: Literal[
        "rewrite",
        "clarify",
        "quantify",
        "surface_keyword",
        "improve_action_verb",
        "improve_impact",
        "improve_specificity",
    ]

    jd_requirement: str | None = None

    reason: str

    evidence_used: list[str] = Field(
        default_factory=list
    )

    verified_facts_used: list[str] = Field(
        default_factory=list
    )

    added_facts: list[str] = Field(
        default_factory=list
    )

    removed_claims: list[str] = Field(
        default_factory=list
    )

    metric_added: bool = False

    metric_source: str | None = None
class RecommendationChange(BaseModel):
    original_text: str

    suggested_text: str

    change_type: Literal[
        "rewrite",
        "clarify",
        "quantify",
        "surface_keyword",
        "improve_action_verb",
        "improve_impact",
        "improve_specificity",
    ]

    jd_requirement: str | None = None

    reason: str

    evidence_used: list[str] = Field(
        default_factory=list
    )

    verified_facts_used: list[str] = Field(
        default_factory=list
    )

    added_facts: list[str] = Field(
        default_factory=list
    )

    removed_claims: list[str] = Field(
        default_factory=list
    )

    metric_added: bool = False

    metric_source: str | None = None

    safety_status: Literal[
        "safe",
        "needs_verification",
        "rejected",
    ]

    confidence: float = Field(
        ge=0,
        le=1,
    )


class KeepAsIs(BaseModel):
    original_text: str

    section: str

    reason: str

    supporting_evidence: list[str] = Field(
        default_factory=list
    )


class MissingRequirementRecommendation(BaseModel):
    requirement: str

    importance: str

    reason: str

    candidate_action: Literal[
        "do_not_add",
        "verify_experience",
        "add_if_true",
        "learn_skill",
    ]

    warning: str


class PartialMatchGuidanceDraft(BaseModel):
    """
    Untrusted wording guidance produced by Gemini for a single
    Partial Match requirement.

    Intentionally does NOT contain evidence_found, why_partial,
    or safety_note — those are always filled in locally by
    Python from already-validated deterministic data (evidence_
    found/why_partial come straight from the matcher's own
    RequirementMatch; safety_note is a fixed disclaimer Python
    always appends), so Gemini cannot omit or weaken them.
    """

    requirement: str

    how_to_strengthen: str

    example_wording: list[str] = Field(
        default_factory=list
    )


class RecommendationBatchResponse(BaseModel):
    """
    Response schema for the single combined Gemini call that
    generates both rewrite recommendations and Partial Match
    wording guidance for one analysis at once. Passed as
    response_schema so Gemini's structured-output mode enforces
    the exact field names/types below, instead of relying on
    the prompt's prose description alone.
    """

    recommendations: list[RecommendationDraft] = Field(
        default_factory=list
    )

    partial_match_guidance: list[PartialMatchGuidanceDraft] = Field(
        default_factory=list
    )


class PartialMatchGuidance(BaseModel):
    requirement: str

    evidence_found: list[str] = Field(
        default_factory=list
    )

    why_partial: str

    how_to_strengthen: str

    example_wording: list[str] = Field(
        default_factory=list
    )

    safety_note: str


class RecommendationReport(BaseModel):
    recommendations: list[RecommendationChange] = Field(
        default_factory=list
    )

    keep_as_is: list[KeepAsIs] = Field(
        default_factory=list
    )

    missing_requirement_actions: list[
        MissingRequirementRecommendation
    ] = Field(
        default_factory=list
    )

    # Additive field: older stored analysis results simply lack
    # this key, and default to an empty list rather than
    # failing validation, so existing records remain readable.
    partial_match_guidance: list[
        PartialMatchGuidance
    ] = Field(
        default_factory=list
    )

    safety_rejected_count: int = 0

    high_priority_count: int = 0

    medium_priority_count: int = 0