"""
Round-based Sales interview prompts.

Splits the single monolithic build_sales_prompt() interview into
three separate, standalone rounds a candidate can practice one at a
time:

- Round 1: Fundamentals & Strategy
- Round 2: Customer Scenarios
- Round 3: HR / Behavioral

Each sub-role from classify_sales_subrole() (generic, customer_success)
gets its own round labels and content. Round 1 reuses that sub-role's
existing fundamentals content from sales_prompt.py; Round 2's scenario
focus and Round 3's HR grounding are new content (see
_SCENARIO_FOCUS_BY_SUBROLE and _HR_CONTEXT_BY_SUBROLE below) - the
original prompt's "Customer Scenarios" difficulty guidelines are
shared across both sub-roles rather than tailored, so this is the
first genuinely new per-sub-role content for this domain.

This module is purely additive: sales_prompt.py's build_sales_prompt
is untouched and still used whenever a round isn't requested (see
AIService.generate_questions). Round keys ("round_1"/"round_2"/
"round_3") are shared across domains - the canonical ROUND_KEYS set
lives in software_rounds.py and is imported directly from there by
callers (e.g. AIService.generate_questions), not redefined here.
"""

from app.services.role_classifier import classify_sales_subrole
from app.services.prompts.sales_prompt import FUNDAMENTALS_BY_SUBROLE
from app.services.prompts.sales_common import (
    OPTIONAL_CODING_STRUCTURE,
    STYLE_GUIDELINES,
    QUESTION_LENGTH_STYLE,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Sales Fundamentals & Strategy", "description": "Sales funnel, CRM, lead generation, negotiation, pipeline management, plus sales strategy questions."},
        {"key": "round_2", "label": "Round 2: Customer Scenarios", "description": "Basic customer interactions through enterprise negotiations and multi-stakeholder selling."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Missing a quota, losing a deal to a competitor, and handling a demanding client."},
    ],
    "customer_success": [
        {"key": "round_1", "label": "Round 1: Customer Success Fundamentals & Strategy", "description": "Onboarding, health scores, account management, renewals, upsell & churn prevention."},
        {"key": "round_2", "label": "Round 2: Customer Success Scenarios", "description": "Onboarding and adoption through renewal negotiations and strategic account growth."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "An angry or churning customer, cross-functional escalations, and pushing back on unreasonable requests."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    sales sub-role. Falls back to "generic" for any unrecognized
    value so this never returns an empty list for a role already
    known to be in the sales domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_SCENARIO_FOCUS_BY_SUBROLE = {
    "generic": "basic customer interactions, then handling objections, closing deals and customer negotiations, then enterprise customer scenarios, strategic negotiations and multi-stakeholder selling",
    "customer_success": "onboarding and adoption scenarios, then renewal negotiations and upsell/cross-sell conversations, then strategic account growth and enterprise renewal negotiations",
}


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as missing a quota, losing a deal to a competitor, and handling a demanding client",
    "customer_success": "scenarios such as an angry or churning customer, a cross-functional escalation with product or support teams, and pushing back on an unreasonable customer request",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    fundamentals_block = FUNDAMENTALS_BY_SUBROLE[subrole]

    opening_section = (
        """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on sales experience, internships, achievements, targets, client handling, negotiations, leadership and measurable business impact."""
        if resume_text
        else """1. Role-Specific Sales Questions (3)

Generate exactly 3 additional role-specific sales questions because no resume is available."""
    )

    return f"""{header}

This is Round 1 of a multi-round Sales interview: Fundamentals & Strategy. Do NOT ask Customer Scenario or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Sales Fundamentals (4)

Generate exactly 4 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must strictly match the selected difficulty.

3. Sales Strategy Questions (3)

Generate exactly 3 questions specific to the selected sales role.

Examples include:

- Business Development
- Account Executive
- Account Manager
- Customer Success
- Relationship Manager
- Inside Sales
- Enterprise Sales

Questions should assess practical sales thinking.

{OPTIONAL_CODING_STRUCTURE}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different sales competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Sales Strategy Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    scenario_focus = _SCENARIO_FOCUS_BY_SUBROLE.get(subrole, _SCENARIO_FOCUS_BY_SUBROLE["generic"])

    difficulty_guidelines = """Difficulty Guidelines:

Easy
- Basic customer interactions

Medium
- Handling objections
- Closing deals
- Customer negotiations

Hard
- Enterprise customer scenarios
- Strategic negotiations
- Multi-stakeholder selling"""

    if resume_text:

        return f"""{header}

This is Round 2 of a multi-round Sales interview: Customer Scenarios. Do NOT ask Fundamentals, Strategy, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure

1. Resume-Grounded Scenario (1)

- Ask exactly 1 customer-scenario question that builds on a deal, account, or client relationship mentioned in the candidate's resume.
- Ask the candidate to walk through how they handled or would now approach that situation.

2. Customer Scenario Questions (6)

Generate exactly 6 customer-based scenario questions, focused on {scenario_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 7 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different sales competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""{header}

This is Round 2 of a multi-round Sales interview: Customer Scenarios. Do NOT ask Fundamentals, Strategy, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

Customer Scenario Questions (6)

Generate exactly 6 customer-based scenario questions, focused on {scenario_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different sales competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their deals, accounts, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Sales interview: HR / Behavioral. Do NOT ask Fundamentals, Strategy, or Customer Scenario questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across resilience, ownership, communication under pressure, handling rejection, and decision-making with incomplete information - do not repeat the same theme.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
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


def build_sales_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Sales interview.
    round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_sales_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
