"""
Round-based Consulting interview prompts.

Splits the single monolithic build_consulting_prompt() interview into
three separate, standalone rounds a candidate can practice one at a
time:

- Round 1: Fundamentals & Business Analysis
- Round 2: Case Studies
- Round 3: HR / Behavioral

Each sub-role from classify_consulting_subrole() (generic,
operations_consulting, digital_consulting) gets its own round labels
and content. Round 1 reuses that sub-role's existing fundamentals
content from consulting_prompt.py; Round 2's case-study focus and
Round 3's HR scenario grounding are new content (see
_CASE_STUDY_FOCUS_BY_SUBROLE and _HR_CONTEXT_BY_SUBROLE below).

This module is purely additive: consulting_prompt.py's
build_consulting_prompt is untouched and still used whenever a round
isn't requested (see AIService.generate_questions). Round keys
("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_consulting_subrole
from app.services.prompts.consulting_prompt import FUNDAMENTALS_BY_SUBROLE
from app.services.prompts.consulting_common import (
    OPTIONAL_CODING_STRUCTURE,
    STYLE_GUIDELINES,
    QUESTION_LENGTH_STYLE,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Consulting Fundamentals & Business Analysis", "description": "SWOT, Porter's Five Forces, PESTLE, market entry and growth strategy, plus business analysis questions."},
        {"key": "round_2", "label": "Round 2: Business Case Studies", "description": "Simple business scenarios through multi-step strategic cases with analysis and recommendations."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Tight case deadlines, disagreeing with a client's assumptions, and unwelcome recommendations."},
    ],
    "operations_consulting": [
        {"key": "round_1", "label": "Round 1: Operations Fundamentals & Business Analysis", "description": "Process mapping, supply chain basics, cost structures, Lean & Six Sigma."},
        {"key": "round_2", "label": "Round 2: Process & Supply Chain Case Studies", "description": "Process optimization, supply chain redesign, and operational cost-reduction at scale."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Shop-floor resistance to change, conflicting priorities across sites, and cost-cutting pushback."},
    ],
    "digital_consulting": [
        {"key": "round_1", "label": "Round 1: Digital Fundamentals & Business Analysis", "description": "Digital basics, technology landscape, cloud and data & analytics strategy."},
        {"key": "round_2", "label": "Round 2: Digital Transformation Case Studies", "description": "Digital transformation roadmaps, cloud/data strategy, and enterprise technology transformation."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Client IT resistance, scope creep, and explaining technical trade-offs to executives."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    consulting sub-role. Falls back to "generic" for any unrecognized
    value so this never returns an empty list for a role already
    known to be in the consulting domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_CASE_STUDY_FOCUS_BY_SUBROLE = {
    "generic": "simple business scenarios, then structured business case interviews, then multi-step strategic consulting cases involving analysis and recommendations",
    "operations_consulting": "process optimization and lean/six sigma scenarios, supply chain redesign, and operational cost-reduction cases",
    "digital_consulting": "digital transformation roadmaps, cloud/data strategy scenarios, and enterprise technology transformation cases",
}


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as tight case deadlines, disagreeing with a client's assumptions, and delivering an unwelcome recommendation",
    "operations_consulting": "scenarios such as resistance to a process change on the shop floor, conflicting priorities across client sites, and defending a cost-cutting recommendation",
    "digital_consulting": "scenarios such as client IT teams resisting a digital roadmap, scope creep on a transformation project, and explaining technical trade-offs to non-technical executives",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    fundamentals_block = FUNDAMENTALS_BY_SUBROLE[subrole]

    opening_section = (
        """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on internships, leadership experiences, business projects, achievements, problem-solving experience, impact created and decision making."""
        if resume_text
        else """1. Role-Specific Consulting Questions (3)

Generate exactly 3 consulting role-specific questions since no resume is available."""
    )

    return f"""{header}

This is Round 1 of a multi-round Consulting interview: Fundamentals & Business Analysis. Do NOT ask Case Study or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Consulting Fundamentals (4)

Generate exactly 4 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must match the selected difficulty.

3. Business Analysis Questions (3)

Generate exactly 3 business analysis questions related to the selected consulting role.

Examples include:

- Strategy Consulting
- Operations Consulting
- Business Consulting
- Advisory
- Management Consulting
- Digital Consulting

Match the selected difficulty.

{OPTIONAL_CODING_STRUCTURE}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different consulting competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Business Analysis Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    case_focus = _CASE_STUDY_FOCUS_BY_SUBROLE.get(subrole, _CASE_STUDY_FOCUS_BY_SUBROLE["generic"])

    difficulty_guidelines = """Difficulty Guidelines:

Easy
- Simple business scenarios

Medium
- Structured business case interviews

Hard
- Multi-step strategic consulting cases involving analysis and recommendations"""

    if resume_text:

        return f"""{header}

This is Round 2 of a multi-round Consulting interview: Business Case Studies. Do NOT ask Fundamentals, Business Analysis, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure

1. Resume-Grounded Case Study (1)

- Ask exactly 1 case-study question that builds on a project, engagement, or experience mentioned in the candidate's resume.
- Ask the candidate to analyze, extend or reconsider a business decision from their own experience.

2. Business Case Studies (6)

Generate exactly 6 consulting case interview questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 7 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different consulting competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""{header}

This is Round 2 of a multi-round Consulting interview: Business Case Studies. Do NOT ask Fundamentals, Business Analysis, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

Business Case Studies (6)

Generate exactly 6 consulting case interview questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different consulting competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their engagements, projects, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Consulting interview: HR / Behavioral. Do NOT ask Fundamentals, Business Analysis, or Case Study questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across teamwork, conflict, ownership, communication under pressure, handling mistakes, and decision-making with incomplete information - do not repeat the same theme.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Questions must match the selected role.
- Avoid duplicate themes.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


_ROUND_BUILDERS = {
    "round_1": _build_round_1,
    "round_2": _build_round_2,
    "round_3": _build_round_3,
}


def build_consulting_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Consulting interview.
    round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_consulting_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
