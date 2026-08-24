from sqlalchemy.orm import Session

from app.models.resume_evidence_vector import ResumeEvidenceVector
from app.schemas.resume_analysis import JDRequirement, ResumeProfile
from app.services.api_key_manager import api_key_manager

# Meaning-based (RAG) retrieval on top of the existing keyword/
# alias/fuzzy matching in requirement_matcher.py. Purely additive:
# it only widens the candidate evidence pool handed to
# SemanticVerifier — every candidate it surfaces still has to pass
# the same evidence-grounding check in
# RequirementMatcher._merge_verification (must be a real, exact
# excerpt of the resume), so it can add recall but never bypass
# the grounding safety rail.

TOP_K = 5


def _resume_evidence_lines(
    resume_profile: ResumeProfile,
) -> list[tuple[str, str]]:
    """
    Every distinct (source_text, section) pair worth indexing —
    top-level evidence claims, per-skill evidence, and every
    experience/project bullet. Mirrors the evidence pool
    RequirementMatcher._find_evidence already searches, so RAG
    retrieval draws from the exact same universe of real resume
    text as the deterministic matcher does.
    """

    pairs: list[tuple[str, str]] = []

    for evidence in resume_profile.evidence:
        pairs.append((evidence.source_text, evidence.section))

    for skill in resume_profile.skills:
        for evidence in skill.evidence:
            pairs.append((evidence.source_text, evidence.section))

    for experience in resume_profile.experience:
        for bullet in experience.bullets:
            pairs.append((bullet.text, "experience"))

    for project in resume_profile.projects:
        for bullet in project.bullets:
            pairs.append((bullet.text, "projects"))

    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []

    for text, section in pairs:

        key = text.strip().lower()

        if not key or key in seen:
            continue

        seen.add(key)
        deduped.append((text, section))

    return deduped


def ensure_resume_evidence_vectors(
    db: Session,
    resume_id: int,
    resume_profile: ResumeProfile,
) -> None:
    """
    Populates resume_evidence_vectors for this resume if it
    hasn't been done yet. A no-op on every subsequent analysis of
    the same resume — mirrors the existing resume_profile_json
    cache-once-reuse-always pattern, so embedding cost is paid
    once per resume, not once per analysis.
    """

    already_indexed = (
        db.query(ResumeEvidenceVector.id)
        .filter(ResumeEvidenceVector.resume_id == resume_id)
        .first()
    )

    if already_indexed:
        return

    lines = _resume_evidence_lines(resume_profile)

    if not lines:
        return

    texts = [text for text, _ in lines]

    vectors = api_key_manager.embed_content(
        texts,
        task_type="RETRIEVAL_DOCUMENT",
        purpose="resume_evidence_embedding",
    )

    for (text, section), vector in zip(lines, vectors):

        db.add(
            ResumeEvidenceVector(
                resume_id=resume_id,
                source_text=text,
                section=section,
                embedding=vector,
            )
        )

    db.commit()


def build_embedding_evidence_map(
    db: Session,
    resume_id: int,
    requirements: list[JDRequirement],
) -> dict[str, list[str]]:
    """
    For each JD requirement, finds the TOP_K resume evidence lines
    whose MEANING is closest to it (via embedding cosine
    similarity) — catches real evidence phrased in different words
    than the requirement, which keyword/alias matching misses
    entirely (e.g. resume: "automated deployment pipeline", JD:
    "CI/CD experience").

    Returns {requirement.name: [evidence_text, ...]}, meant to be
    unioned with the keyword-based evidence_map in
    RequirementMatcher._retrieve_relevant_evidence — this is a
    retrieval signal only, not a match decision.
    """

    if not requirements:
        return {}

    query_texts = [
        " ".join(
            filter(
                None,
                [
                    requirement.name,
                    " ".join(requirement.aliases),
                    " ".join(requirement.evidence),
                ],
            )
        )
        for requirement in requirements
    ]

    query_vectors = api_key_manager.embed_content(
        query_texts,
        task_type="RETRIEVAL_QUERY",
        purpose="jd_requirement_embedding",
    )

    embedding_evidence_map: dict[str, list[str]] = {}

    for requirement, query_vector in zip(
        requirements,
        query_vectors,
    ):

        rows = (
            db.query(ResumeEvidenceVector.source_text)
            .filter(ResumeEvidenceVector.resume_id == resume_id)
            .order_by(
                ResumeEvidenceVector.embedding.cosine_distance(
                    query_vector
                )
            )
            .limit(TOP_K)
            .all()
        )

        embedding_evidence_map[requirement.name] = [
            row.source_text for row in rows
        ]

    return embedding_evidence_map
