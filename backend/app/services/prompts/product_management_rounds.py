"""
Round-based Product Management interview prompts.

Splits the single monolithic build_product_management_prompt()
interview into three separate, standalone rounds a candidate can
practice one at a time:

- Round 1: Product Sense & Design
- Round 2: Product Strategy & Analytics (sub-role flavored)
- Round 3: HR / Behavioral

This domain has the most intricate sub-role tailoring shipped so far:
three independent dicts, each tailoring a DIFFERENT one of the three
content sections for a DIFFERENT one of the three specialized
sub-roles, all falling back to "generic" otherwise:

- _PRODUCT_SENSE_BLOCK_BY_SUBROLE: only "technical_pm" is tailored
  (technical basics, API design, engineering collaboration);
  "growth_pm" and "product_analyst" fall back to "generic".
- _PRODUCT_STRATEGY_BLOCK_BY_SUBROLE: only "growth_pm" is tailored
  (AARRR, growth loops, referral/virality, growth experimentation);
  "technical_pm" and "product_analyst" fall back to "generic".
- _PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE: only "product_analyst" is
  tailored (cohort analysis, experimentation design, statistical
  significance); "technical_pm" and "growth_pm" fall back to
  "generic".

So each specialized sub-role's specialty shows up in exactly ONE of
the two rounds below - e.g. technical_pm's Round 2 is byte-identical
to generic's Round 2, since neither tailors Strategy or Analytics.
This is the source prompt's own existing, intentional design and is
preserved exactly here - no new tailoring is invented for a sub-role
that doesn't already have it in the source prompt.

Like the hardware domains, this module has no "Question Length &
Style" block; like the business domains, it has no coding-question
structure - both intentionally absent, matching the source prompt.
It also preserves the source prompt's unique "Important Instructions"
block (no single correct answer / avoid trivia / prefer practical
scenarios), reused across all 3 rounds since it shapes question style
throughout, not just one section.

This module is purely additive: product_management.py's
build_product_management_prompt is untouched and still used whenever
a round isn't requested (see AIService.generate_questions). Round
keys ("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_product_management_subrole
from app.services.prompts.product_management import (
    PRODUCT_SENSE_BLOCK_BY_SUBROLE,
    PRODUCT_SENSE_BLOCK_BY_SUBROLE_NO_RESUME,
    PRODUCT_SENSE_TOPICS,
    PRODUCT_SENSE_TOPICS_NO_RESUME,
    PRODUCT_STRATEGY_BLOCK_BY_SUBROLE,
    PRODUCT_STRATEGY_BLOCK_BY_SUBROLE_NO_RESUME,
    PRODUCT_STRATEGY_TOPICS,
    PRODUCT_STRATEGY_TOPICS_NO_RESUME,
    PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE,
    PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE_NO_RESUME,
    PRODUCT_ANALYTICS_TOPICS,
    PRODUCT_ANALYTICS_TOPICS_NO_RESUME,
)
from app.services.prompts.product_management_common import (
    STYLE_GUIDELINES,
    IMPORTANT_INSTRUCTIONS,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Product Sense & Design", "description": "User personas, MVP, feature prioritization, platform strategy, and ecosystem design."},
        {"key": "round_2", "label": "Round 2: Product Strategy & Analytics", "description": "Market entry, monetization, pricing, plus North Star metrics, funnels, and A/B testing."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "An underperforming launch, engineering scope disagreements, and saying no to stakeholders."},
    ],
    "technical_pm": [
        {"key": "round_1", "label": "Round 1: Technical Product Sense & Design", "description": "Technical basics for PMs, API design, system architecture trade-offs, engineering collaboration."},
        {"key": "round_2", "label": "Round 2: Product Strategy & Analytics", "description": "Market entry, monetization, pricing, plus North Star metrics, funnels, and A/B testing."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Pushing back on engineering estimates, technical trade-offs, and explaining constraints to stakeholders."},
    ],
    "growth_pm": [
        {"key": "round_1", "label": "Round 1: Product Sense & Design", "description": "User personas, MVP, feature prioritization, platform strategy, and ecosystem design."},
        {"key": "round_2", "label": "Round 2: Growth Strategy & Product Analytics", "description": "AARRR, growth loops, referral & virality, growth experimentation, plus product analytics."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A growth experiment that backfires, channel-strategy disagreements, and defending retention work."},
    ],
    "product_analyst": [
        {"key": "round_1", "label": "Round 1: Product Sense & Design", "description": "User personas, MVP, feature prioritization, platform strategy, and ecosystem design."},
        {"key": "round_2", "label": "Round 2: Product Strategy & Data-Driven Analytics", "description": "Market entry and pricing, plus cohort analysis, experimentation design, and statistical significance."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A misleading metric, disagreements over what to measure, and defending counter-intuitive results."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    Product Management sub-role. Falls back to "generic" for any
    unrecognized value so this never returns an empty list for a role
    already known to be in the product_management domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as a feature launch that underperforms, disagreeing with engineering on scope, and saying no to a stakeholder's pet feature",
    "technical_pm": "scenarios such as pushing back on an engineering estimate, a technical trade-off that delays a launch, and explaining a technical constraint to non-technical stakeholders",
    "growth_pm": "scenarios such as a growth experiment that backfires, disagreeing with marketing on channel strategy, and defending a retention initiative over an acquisition-only push",
    "product_analyst": "scenarios such as a metric that looks good but hides a real problem, disagreeing with a PM over what to measure, and defending a counter-intuitive A/B test result",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:
        opening_section = """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on product initiatives, internships, leadership, product launches, business impact, user problems solved, metrics, cross-functional collaboration and achievements."""
        product_sense_block = PRODUCT_SENSE_BLOCK_BY_SUBROLE.get(subrole, PRODUCT_SENSE_TOPICS)
    else:
        opening_section = """1. Role-Specific Product Management Questions (3)

Generate exactly 3 additional role-specific Product Management questions because no resume is available."""
        product_sense_block = PRODUCT_SENSE_BLOCK_BY_SUBROLE_NO_RESUME.get(subrole, PRODUCT_SENSE_TOPICS_NO_RESUME)

    return f"""{header}

This is Round 1 of a multi-round Product Management interview: Product Sense & Design. Do NOT ask Product Strategy, Product Analytics, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Product Sense & Product Design (7)

Generate exactly 7 questions.

Difficulty Guidelines

{product_sense_block}

Questions must strictly match the selected difficulty.

{STYLE_GUIDELINES}

{IMPORTANT_INSTRUCTIONS}

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Product Management competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:

        product_strategy_block = PRODUCT_STRATEGY_BLOCK_BY_SUBROLE.get(subrole, PRODUCT_STRATEGY_TOPICS)
        product_analytics_block = PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE.get(subrole, PRODUCT_ANALYTICS_TOPICS)

        return f"""{header}

This is Round 2 of a multi-round Product Management interview: Product Strategy & Analytics. Do NOT ask Product Sense/Design or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

1. Resume-Grounded Question (1)

- Ask exactly 1 question that builds on a product strategy or analytics decision mentioned in the candidate's resume.
- Ask the candidate to walk through how they approached, or would now approach, that situation.

2. Product Strategy & Business Thinking (2)

Generate exactly 2 questions.

Topics include:

{product_strategy_block}

3. Product Analytics & Execution (3)

Generate exactly 3 questions.

Topics include:

{product_analytics_block}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

{IMPORTANT_INSTRUCTIONS}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Product Management competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    product_strategy_block_no_resume = PRODUCT_STRATEGY_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, PRODUCT_STRATEGY_TOPICS_NO_RESUME
    )
    product_analytics_block_no_resume = PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, PRODUCT_ANALYTICS_TOPICS_NO_RESUME
    )

    return f"""{header}

This is Round 2 of a multi-round Product Management interview: Product Strategy & Analytics. Do NOT ask Product Sense/Design or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 5 interview questions.

Interview Structure

1. Product Strategy & Business Thinking (2)

Generate exactly 2 questions.

Topics include:

{product_strategy_block_no_resume}

2. Product Analytics & Execution (3)

Generate exactly 3 questions.

Topics include:

{product_analytics_block_no_resume}

{STYLE_GUIDELINES}

{IMPORTANT_INSTRUCTIONS}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Product Management competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their launches, projects, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Product Management interview: HR / Behavioral. Do NOT ask Product Sense/Design, Product Strategy, or Product Analytics questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across ownership, cross-functional communication, handling ambiguity, prioritization under pressure, and decision-making with incomplete data - do not repeat the same theme.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
- Avoid duplicate themes.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


_ROUND_BUILDERS = {
    "round_1": _build_round_1,
    "round_2": _build_round_2,
    "round_3": _build_round_3,
}


def build_product_management_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Product Management
    interview. round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_product_management_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
