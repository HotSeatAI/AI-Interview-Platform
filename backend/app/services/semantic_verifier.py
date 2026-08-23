import json
from google.genai import types

from app.core.config import (
    GEMINI_MODEL,
    GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE,
)

from app.services.api_key_manager import (
    api_key_manager,
)
from app.schemas.resume_analysis import (
    JDRequirement,
    SemanticVerification,
    SemanticVerificationBatch,
)


class SemanticVerifier:
    """
    Holistic recruiter-style verification of EVERY JD
    requirement against the candidate's complete resume —
    the way an experienced technical recruiter reads a resume
    against a JD, not a narrow per-line keyword check.

    This is no longer gated to only "ambiguous" or loosely-
    retrieved "missing" requirements — every requirement in
    the analysis goes through this pass, given the complete
    raw resume text (not narrow retrieval snippets), so a real
    match phrased in a way nothing anticipated — or sitting in
    a resume section the structured extraction step happened
    to miss — still gets a genuine look instead of being
    silently skipped by an upstream retrieval filter.

    RequirementMatcher._merge_verification still floors this
    against Pass 1's deterministic result: an exact literal
    phrase/alias hit from Pass 1 can be upgraded by this pass
    but never downgraded, so a confirmed literal match can't be
    second-guessed away by an inference.

    IMPORTANT:
    This service is not allowed to create resume evidence.

    Requirements for one analysis are verified in chunked
    batched Gemini calls (see verify_batch), at most
    GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE requirements per
    call, rather than one call per requirement, to keep each
    call's structured response small and reliable while still
    keeping the overall analysis within a bounded call budget.
    If one chunk's call fails, only that chunk's requirements
    fall back to the conservative "missing" handling in
    RequirementMatcher._merge_verification — it does not fail
    the whole analysis.

    Each requirement is given its own retrieved evidence (a
    small, ranked list of relevant resume lines chosen by
    RequirementMatcher._retrieve_relevant_evidence) as a
    focused hint, PLUS the candidate's complete raw resume text
    as a shared reference for the whole call — retrieval, and
    even the structured resume extraction itself, can miss real
    evidence phrased in a way nothing anticipated, so the
    complete text lets Gemini still find and cite it. Every
    "supporting_evidence" item Gemini cites is still validated
    against what it was actually given
    (RequirementMatcher._merge_verification), so it can never
    cite text that doesn't genuinely exist in the resume.
    """

    def verify_batch(
        self,
        requirements: list[JDRequirement],
        evidence_map: dict[str, list[str]],
        adjacency_hints: dict[str, list[str]] | None = None,
        full_resume_text: str | None = None,
    ) -> dict[str, SemanticVerification]:
        """
        Splits `requirements` into chunks of at most
        GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE and verifies
        each chunk via its own Gemini call, merging results.
        """

        if not requirements:
            return {}

        adjacency_hints = adjacency_hints or {}
        full_resume_text = full_resume_text or ""

        chunk_size = GEMINI_SEMANTIC_VERIFICATION_BATCH_SIZE

        chunks = [
            requirements[start:start + chunk_size]
            for start in range(
                0,
                len(requirements),
                chunk_size,
            )
        ]

        results: dict[str, SemanticVerification] = {}

        for chunk_index, chunk in enumerate(
            chunks,
            start=1,
        ):

            try:

                chunk_results = self._verify_batch_chunk(
                    chunk,
                    evidence_map,
                    adjacency_hints,
                    full_resume_text,
                    chunk_index,
                    len(chunks),
                )

                results.update(chunk_results)

            except Exception:

                # Conservative degrade: this chunk's
                # requirements simply stay absent from
                # `results`. _merge_verification already
                # treats a missing verification as "no result
                # returned" -> falls back to
                # match_type="missing", score 0. One
                # malformed/failed chunk must not fail the
                # whole analysis.
                continue

        return results

    def _verify_batch_chunk(
        self,
        requirements: list[JDRequirement],
        evidence_map: dict[str, list[str]],
        adjacency_hints: dict[str, list[str]],
        full_resume_text: str,
        chunk_index: int,
        total_chunks: int,
    ) -> dict[str, SemanticVerification]:

        requirement_blocks = []

        for index, requirement in enumerate(
            requirements,
            start=1,
        ):
            evidence_lines = evidence_map.get(
                requirement.name,
                [],
            )

            if evidence_lines:

                evidence_block = "\n".join(
                    f"{line_index}. {text}"
                    for line_index, text in enumerate(
                        evidence_lines,
                        start=1,
                    )
                )

            else:

                evidence_block = (
                    "(No potentially relevant resume "
                    "evidence was retrieved for this "
                    "requirement.)"
                )

            hinted_technologies = adjacency_hints.get(
                requirement.name,
                [],
            )

            if hinted_technologies:

                adjacency_line = (
                    "\nKnown related-but-NOT-equivalent tools, "
                    "technologies, or standards detected in "
                    "this candidate's resume: "
                    + ", ".join(hinted_technologies)
                    + "\n"
                )

            else:

                adjacency_line = ""

            requirement_blocks.append(
                f"""
REQUIREMENT #{index}

requirement_name (echo this exactly):
{requirement.name}

Category:
{requirement.category}

Importance:
{requirement.importance}

JD Evidence:
{requirement.evidence}

Possible aliases:
{requirement.aliases}

Allowed resume evidence for THIS requirement:
{evidence_block}
{adjacency_line}"""
            )

        if full_resume_text.strip():

            full_resume_block = full_resume_text.strip()

        else:

            full_resume_block = (
                "(No resume text was extracted for this "
                "candidate.)"
            )

        prompt = f"""
You are an experienced technical recruiter for HotSeat,
screening ONE candidate's resume against a job description —
the way a real recruiter reads a resume, not a keyword
checklist.

First, form a holistic read of the candidate from the
COMPLETE RESUME TEXT below: their overall trajectory, and for
each skill/qualification they claim, how DEEP and how RECENT
that evidence is (a skill demonstrated across multiple recent
bullets/projects is stronger evidence than one passing mention
from years ago). Then, using that holistic read, determine for
EACH job-description requirement listed below whether the
candidate's EXISTING resume evidence satisfies it.

Recognize equivalent qualifications stated under different
naming conventions the way a recruiter would — e.g. "B.E." or
"B.Tech" (common outside the US) is the same tier of
qualification as "Bachelor's degree" or "B.S."; a differently-
named but equivalent professional certification, title, or
tool counts the same way. Do not penalize a candidate merely
for a regional/conventional naming difference that means the
same thing.

You are verifying {len(requirements)} requirement(s) in
this single request. Return one verification object per
requirement, using the exact "requirement_name" value given
for each requirement so results can be matched back up.

Each requirement lists its OWN "Allowed resume evidence"
block — a focused, retrieval-ranked subset most likely to be
relevant to that specific requirement. Below that, a shared
"COMPLETE RESUME TEXT" section contains this candidate's
ENTIRE resume, verbatim. The focused block is a starting
point, not a limit — if a requirement's true supporting
evidence exists elsewhere in the complete resume text but was
not included in its focused subset, you may still cite it
there, as long as it is a real, exact excerpt from the complete
resume text and is genuinely relevant to that SPECIFIC
requirement. Do NOT use any information about the candidate
that is not explicitly present in either the requirement's own
focused block or the complete resume text — nothing outside
these two sources.

JOB DESCRIPTION REQUIREMENTS
=============================

{"".join(requirement_blocks)}

COMPLETE RESUME TEXT
=============================
(Shared reference for every requirement above.)

{full_resume_block}


STRICT RULES
============

1. You may ONLY use information present in the requirement's
own "Allowed resume evidence" block, or in the shared
"COMPLETE RESUME TEXT" section — nothing else.

2. NEVER invent experience.

3. Knowledge of one tool, technology, or standard does NOT
automatically prove knowledge of a DIFFERENT, non-
interchangeable one in the same category, even when they are
commonly paired or compared.

3a. When the resume shows REAL, groundable evidence of a tool,
technology, or standard that is related-but-distinct from the
required one in the SAME category (e.g. a different cloud
platform, a different container orchestrator, a different
relational database, a different frontend framework, a
different CRM platform, a different accounting standard) — and
especially when a "Known related-but-NOT-equivalent tools,
technologies, or standards detected" hint is present for that
requirement — use decision "adjacent", NOT "partial" and NOT
"missing". "adjacent" means: real, grounded evidence exists,
but it is evidence of a DIFFERENT tool/technology/standard that
is transferable to, not proof of, the required one.

Worked example (technical):

JD:
"AWS experience required"

Resume evidence:
"Led migration of microservices to Azure Kubernetes Service"

Known related-but-NOT-equivalent tools, technologies, or
standards detected: azure

Result:
adjacent

NOT partial, NOT strong, NOT missing. Your reasoning must state
that this is cloud-platform-adjacent experience, not evidence
of AWS itself. The same logic applies across any category —
CRM platforms, accounting standards, container orchestrators,
frontend frameworks, etc.

Worked example (non-technical):

JD:
"Salesforce experience required"

Resume evidence:
"Managed the full sales pipeline in HubSpot, from lead capture
through close"

Known related-but-NOT-equivalent tools, technologies, or
standards detected: hubspot

Result:
adjacent

NOT partial, NOT strong, NOT missing. Your reasoning must state
that this is CRM-platform-adjacent experience, not evidence of
Salesforce itself.

4. Do not infer a technology merely because it is
commonly used with another technology.

5. Do not infer years of experience unless explicitly
supported.

6. Do not infer leadership unless explicitly supported.

7. Do not infer production experience unless
explicitly supported.

8. Do not infer a specific cloud platform from
generic "cloud" experience.

9. Do not infer a specific database from generic
"database" experience.

10. A conceptually related statement can be considered
a PARTIAL match when it genuinely overlaps with the exact
required skill but does not prove it. "partial" is reserved
for weaker/incomplete evidence of the SAME required skill —
it must NOT be used for cross-technology adjacency (that is
rule 3a's "adjacent" decision instead).

Example:

JD:
"Distributed systems"

Resume:
"Built scalable backend services"

Possible result:
partial

NOT:
strong

11. A direct technology mention with meaningful usage
evidence can be strong.

Example:

JD:
"FastAPI"

Resume:
"Developed REST APIs using FastAPI"

Result:
strong

12. Generic statements without enough evidence should
remain ambiguous or missing.

13. Every "supporting_evidence" item you return MUST be an
exact or near-exact excerpt from either that requirement's own
"Allowed resume evidence" block OR the "COMPLETE RESUME TEXT"
section. Do not paraphrase, combine, or invent evidence. If you
cannot quote real evidence from one of these two sources, do
not claim support. This applies to "adjacent" decisions too —
the cited evidence must be real text from one
of these two sources, not an invented technology mention.

14. Do not rewrite or improve the resume.

15. Do not suggest adding anything.

16. If the evidence is insufficient, say so — use decision
"missing" rather than stretching a weak signal into
"partial", "adjacent", or "strong".

17. Confidence represents confidence in the decision,
NOT how impressive the candidate is.

18. unsupported_assumptions must explicitly identify
any assumption that would be required to classify
the candidate more strongly.

19. Evaluate each requirement independently. Having access to
the complete resume evidence does NOT mean evidence found
relevant for one requirement can be reused to justify a
different, unrelated requirement — every piece of cited
evidence must be genuinely and specifically relevant to the
requirement it is cited for.

20. Naming-convention equivalence is not the same as
technology adjacency. "B.E." meaning the same thing as
"Bachelor's degree" is a real equivalence (same qualification,
different name) — use "strong", not "adjacent". Rule 3a's
"adjacent" is reserved for genuinely different, non-
interchangeable tools/technologies/standards (Azure when AWS
is required) — never apply it to a mere naming difference for
the SAME qualification.

21. Weigh depth and recency of evidence the way a recruiter
would: a skill backed by multiple recent, substantive bullets
is stronger evidence than a single old or passing mention. Two
candidates who both technically "mention" a skill are not
automatically equal — say so in your reasoning when it affects
your decision.

22. Holistic reading is for WEIGHING evidence, not for
SKIPPING whether the requirement's literal condition is fully
met. Do not let a generally strong or impressive resume cause
you to round an incompletely-satisfied requirement up to
"strong". Before deciding "strong", check the requirement's
own exact wording for a specific condition (fully completed,
not in-progress; a specific certification actually held, not
in pursuit; a specific years-of-experience floor actually met,
not approaching) — if that specific condition is not yet
fully met, the correct decision is "partial", regardless of
how strong the rest of the resume is.

Example — a real case this rule exists to catch:

JD requirement: "Bachelor's Degree in Computer Science"

Resume evidence: "B.E. Computer Science Engineering, BITS
Pilani, 2023 – 2027" (an in-progress degree, not yet
conferred — the end date is in the future)

Correct decision: "partial" — the degree TYPE is a genuine
equivalent (do not use "adjacent" for the naming difference,
per rule 20), but it is not yet completed. Reasoning should
say so explicitly: "in-progress, expected 2027, not yet
conferred." Do NOT decide "strong" here just because the
candidate's overall academic record looks strong — this is a
literal completion-status check, not a holistic impression.

"Partial" is not a lesser or discouraged outcome — it is the
correct, useful signal that tells the candidate specifically
what would need to change to become a full match. Reserve
"strong" for when the requirement's own literal condition is
actually, fully met.

Return ONLY structured data matching the requested schema,
with exactly one verification per requirement listed above.
"""

        response = api_key_manager.generate_content(
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SemanticVerificationBatch,
                temperature=0.0,
            ),
            purpose=(
                f"semantic_verification_batch_chunk_"
                f"{chunk_index}_of_{total_chunks}"
            ),
        )

        raw = (
            response.text or ""
        ).strip()

        if not raw:
            raise ValueError(
                "Semantic verifier returned an empty response."
            )

        try:
            parsed = json.loads(raw)

            batch = SemanticVerificationBatch.model_validate(
                parsed
            )

        except Exception as exc:
            raise ValueError(
                "Semantic verifier returned invalid "
                "structured data."
            ) from exc

        results: dict[str, SemanticVerification] = {}

        for item in batch.verifications:
            results[item.requirement_name.strip().lower()] = item

        return results
