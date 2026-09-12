"""
Round-based Software Engineering interview prompts.

Splits the single monolithic build_software_prompt() interview into
three separate, standalone rounds a candidate can practice one at a
time:

- Round 1: Fundamentals & Coding
- Round 2: System Design
- Round 3: HR / Behavioral

Each sub-role from classify_software_subrole() (generic, ml_data_science,
data_engineering, frontend, mobile, devops_sre, qa_testing) gets its own
round labels/descriptions and reuses that sub-role's existing fundamentals
and system-design topic content from software_prompt.py - only the HR
round's scenario grounding is new content (see _HR_CONTEXT_BY_SUBROLE).

This module is purely additive: software_prompt.py's build_software_prompt
is untouched and still used whenever a round isn't requested (see
AIService.generate_questions).
"""

from app.services.role_classifier import classify_software_subrole
from app.services.prompts.software_prompt import (
    FUNDAMENTALS_BY_SUBROLE,
    SYSTEM_DESIGN_BY_SUBROLE,
)
from app.services.prompts.software_common import (
    CODING_QUESTION_STRUCTURE,
    STYLE_GUIDELINES,
    QUESTION_LENGTH_STYLE,
    build_role_header,
)


ROUND_KEYS = {"round_1", "round_2", "round_3"}


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: DSA & Fundamentals", "description": "Core CS fundamentals (OS/DBMS/OOP) plus DSA coding problems."},
        {"key": "round_2", "label": "Round 2: System Design", "description": "Scalability, caching, databases, and distributed systems concepts."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Code reviews, sprint deadlines, and production-incident scenarios."},
    ],
    "ml_data_science": [
        {"key": "round_1", "label": "Round 1: ML Fundamentals & Coding", "description": "Statistics, ML fundamentals, model evaluation, plus coding problems."},
        {"key": "round_2", "label": "Round 2: ML System Design", "description": "Feature stores, model serving, training pipelines, and MLOps."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Production model issues and cross-functional stakeholder scenarios."},
    ],
    "data_engineering": [
        {"key": "round_1", "label": "Round 1: Data Fundamentals & Coding", "description": "SQL, database design, ETL/data pipelines, plus coding problems."},
        {"key": "round_2", "label": "Round 2: Data Architecture", "description": "Data pipeline architecture, data lake vs. warehouse, batch vs. streaming."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Pipeline failures, data quality incidents, and cross-team data contracts."},
    ],
    "frontend": [
        {"key": "round_1", "label": "Round 1: Frontend Fundamentals & Coding", "description": "JS/TS fundamentals, DOM & rendering, web performance, plus coding problems."},
        {"key": "round_2", "label": "Round 2: Frontend Architecture", "description": "Component architecture, state management, rendering strategies, micro-frontends."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Design/PM pushback, cross-browser bugs, and performance regressions."},
    ],
    "mobile": [
        {"key": "round_1", "label": "Round 1: Mobile Fundamentals & Coding", "description": "App lifecycle, memory management, concurrency, plus coding problems."},
        {"key": "round_2", "label": "Round 2: Mobile Architecture", "description": "App architecture, offline-first storage, battery/network efficiency."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "App store rejections, crash spikes, and platform API changes."},
    ],
    "devops_sre": [
        {"key": "round_1", "label": "Round 1: Systems Fundamentals & Coding", "description": "OS, networking, containers & orchestration, plus scripting problems."},
        {"key": "round_2", "label": "Round 2: Infrastructure Design", "description": "Scaling, caching, load balancing, and fault tolerance."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Production incidents, on-call rotations, and post-mortems."},
    ],
    "qa_testing": [
        {"key": "round_1", "label": "Round 1: Testing Fundamentals & Coding", "description": "Testing fundamentals, automation, bug lifecycle, plus coding problems."},
        {"key": "round_2", "label": "Round 2: Test Architecture", "description": "Test automation architecture, CI/CD test pipelines, flaky test mitigation."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Flaky tests, release-blocking bugs, and severity disagreements."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    software sub-role. Falls back to "generic" for any unrecognized
    value so this never returns an empty list for a role already
    known to be in the software domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as code reviews, sprint deadlines, and production incidents",
    "ml_data_science": "scenarios such as a model underperforming in production, explaining ML results to non-technical stakeholders, and data quality disputes",
    "data_engineering": "scenarios such as pipeline failures, data quality incidents, and cross-team data contracts",
    "frontend": "scenarios such as design/PM pushback on UX decisions, cross-browser bugs, and performance regressions",
    "mobile": "scenarios such as app store rejections, post-release crash spikes, and platform API changes",
    "devops_sre": "scenarios such as production incidents, on-call rotations, and post-mortems",
    "qa_testing": "scenarios such as flaky tests, release-blocking bugs, and severity disagreements with developers",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    fundamentals_block = FUNDAMENTALS_BY_SUBROLE[subrole]

    opening_section = (
        """1. Resume-Based Questions (3)
- Ask exactly 3 questions based on the candidate's resume.
- Focus on projects, internships, technologies used, architecture, implementation choices, optimizations, challenges faced and achievements.
- Use the resume extensively."""
        if resume_text
        else """1. Role-Specific Technical Questions (3)

Since there is no resume, generate exactly 3 role-specific technical questions relevant to the candidate's role."""
    )

    return f"""{header}

This is Round 1 of a multi-round Software Engineering interview: Fundamentals & Coding. Do NOT ask System Design or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure:

{opening_section}

2. Core Fundamentals (4)
Generate exactly 4 questions.

{fundamentals_block}

Adjust the complexity according to the interview difficulty:
- Easy → basic concepts and definitions
- Medium → application-based interview questions
- Hard → advanced concepts, trade-offs and real interview scenarios

3. Coding / DSA (3)

Generate exactly 3 coding interview questions.

Requirements:

- Use famous interview problems commonly asked in Software Engineering interviews.
- Select problems appropriate for the chosen difficulty.
    - Easy → Comparable to LeetCode Easy
    - Medium → Comparable to LeetCode Medium
    - Hard → Comparable to LeetCode Hard

{CODING_QUESTION_STRUCTURE}

{STYLE_GUIDELINES}

General Rules:
- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover a variety of topics.
- Questions should resemble real Software Engineering interviews.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the 10 numbered interview questions.

For resume/role-specific and fundamentals questions, return only the numbered question.

For coding questions, keep the numbering, then on its own line write exactly `TYPE: CODING`, then immediately follow the required coding question structure exactly as specified above. Do NOT add a `TYPE: CODING` line to any other question.

Do not include introductions, conclusions, markdown, or any additional explanatory text outside the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    system_design_block = SYSTEM_DESIGN_BY_SUBROLE[subrole]

    if resume_text:

        return f"""{header}

This is Round 2 of a multi-round Software Engineering interview: System Design. Do NOT ask Coding/DSA or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure:

1. Resume-Grounded Design Question (1)
- Ask exactly 1 system/architecture design question that builds on a project, system or technology mentioned in the candidate's resume.
- Ask the candidate to extend, scale or redesign something from their own experience.

2. Conceptual System Design Questions (5)
Generate exactly 5 conceptual system/architecture design questions.

DO NOT ask candidates to design complete systems such as:
- Design Twitter
- Design WhatsApp
- Design YouTube
- Design Uber

Instead ask conceptual interview questions on topics such as:
{system_design_block}

Increase the conceptual depth according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules:
- Generate EXACTLY 7 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover a variety of topics.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the 7 numbered interview questions.

Return only the numbered question - no markdown, introductions or conclusions.
"""

    return f"""{header}

This is Round 2 of a multi-round Software Engineering interview: System Design. Do NOT ask Coding/DSA or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure:

Conceptual System Design Questions (6)
Generate exactly 6 conceptual system/architecture design questions.

DO NOT ask candidates to design complete systems such as:
- Design Twitter
- Design WhatsApp
- Design YouTube
- Design Uber

Instead ask conceptual interview questions on topics such as:
{system_design_block}

Increase the conceptual depth according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules:
- Generate EXACTLY 6 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover a variety of topics.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the 6 numbered interview questions.

Return only the numbered question - no markdown, introductions or conclusions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their projects, team experiences, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Software Engineering interview: HR / Behavioral. Do NOT ask Coding/DSA or System Design questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure:

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across teamwork, conflict, ownership, communication, handling failure, and decision-making under pressure - do not repeat the same theme.

{STYLE_GUIDELINES}

General Rules:
- Generate EXACTLY 5 questions.
- Questions must match the selected role.
- Avoid duplicate themes.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the 5 numbered interview questions.

Return only the numbered question - no markdown, introductions or conclusions.
"""


_ROUND_BUILDERS = {
    "round_1": _build_round_1,
    "round_2": _build_round_2,
    "round_3": _build_round_3,
}


def build_software_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Software Engineering
    interview. round_key must be one of ROUND_KEYS - callers are
    expected to validate this before calling (see
    AIService.generate_questions).
    """

    subrole = classify_software_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
