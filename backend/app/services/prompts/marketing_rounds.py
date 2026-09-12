"""
Round-based Marketing interview prompts.

Splits the single monolithic build_marketing_prompt() interview into
three separate, standalone rounds a candidate can practice one at a
time:

- Round 1: Fundamentals & Analytics
- Round 2: Campaign Case Studies
- Round 3: HR / Behavioral

Each sub-role from classify_marketing_subrole() (generic,
brand_management, seo, content_marketing, product_marketing) gets its
own round labels and content. Round 1 reuses that sub-role's existing
fundamentals content from marketing_prompt.py; Round 2's case-study
focus and Round 3's HR scenario grounding are new content (see
_CASE_STUDY_FOCUS_BY_SUBROLE and _HR_CONTEXT_BY_SUBROLE below).

This module is purely additive: marketing_prompt.py's
build_marketing_prompt is untouched and still used whenever a round
isn't requested (see AIService.generate_questions). Round keys
("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_marketing_subrole
from app.services.prompts.marketing_prompt import FUNDAMENTALS_BY_SUBROLE
from app.services.prompts.marketing_common import (
    OPTIONAL_CODING_STRUCTURE,
    STYLE_GUIDELINES,
    QUESTION_LENGTH_STYLE,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Marketing Fundamentals & Analytics", "description": "Branding, marketing mix, SEO, consumer behaviour, growth marketing, plus analytics questions."},
        {"key": "round_2", "label": "Round 2: Campaign Case Studies", "description": "Basic campaign planning through multi-channel strategy and data-driven decisions."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Missed deadlines, stakeholder pushback on creative direction, and defending a budget cut."},
    ],
    "brand_management": [
        {"key": "round_1", "label": "Round 1: Brand Fundamentals & Analytics", "description": "Brand positioning, brand equity, brand architecture, portfolio strategy."},
        {"key": "round_2", "label": "Round 2: Brand Strategy Case Studies", "description": "Brand positioning and awareness through tracking, repositioning, and portfolio strategy."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Defending brand guidelines, navigating a brand crisis, and cross-functional alignment on voice."},
    ],
    "seo": [
        {"key": "round_1", "label": "Round 1: SEO Fundamentals & Analytics", "description": "Keyword research, on-page and technical SEO, link building, Core Web Vitals."},
        {"key": "round_2", "label": "Round 2: SEO Strategy Case Studies", "description": "Keyword/on-page optimization through technical audits and large-scale SEO strategy."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A traffic drop after an algorithm update, engineering pushback, and roadmap prioritization."},
    ],
    "content_marketing": [
        {"key": "round_1", "label": "Round 1: Content Fundamentals & Analytics", "description": "Content formats, editorial planning, storytelling, content-led growth."},
        {"key": "round_2", "label": "Round 2: Content Strategy Case Studies", "description": "Content planning through distribution, storytelling, and content-led growth ROI."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A missed editorial deadline, pivoting low-performing content, and stakeholder pushback."},
    ],
    "product_marketing": [
        {"key": "round_1", "label": "Round 1: Product Marketing Fundamentals & Analytics", "description": "Positioning, messaging, go-to-market strategy, competitive analysis."},
        {"key": "round_2", "label": "Round 2: GTM Case Studies", "description": "Positioning and messaging through go-to-market strategy and multi-product launches."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Messaging misalignment with sales, an underperforming launch, and cross-functional pushback."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    marketing sub-role. Falls back to "generic" for any unrecognized
    value so this never returns an empty list for a role already
    known to be in the marketing domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_CASE_STUDY_FOCUS_BY_SUBROLE = {
    "generic": "basic campaign planning and brand awareness, then campaign optimization and budget allocation, then multi-channel marketing strategy, growth experiments and data-driven campaign decisions",
    "brand_management": "brand positioning and awareness campaigns, then brand tracking/perception studies and repositioning, then brand portfolio strategy and long-term brand value building",
    "seo": "keyword and on-page optimization, then technical SEO audits and link-building campaigns, then large-scale SEO strategy for competitive markets",
    "content_marketing": "content planning and format selection, then content distribution and storytelling campaigns, then content-led growth strategy and ROI",
    "product_marketing": "positioning and messaging for a launch, then go-to-market strategy and competitive analysis, then multi-product positioning and launch strategy at scale",
}


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as a missed campaign deadline, stakeholder pushback on creative direction, and defending a budget cut",
    "brand_management": "scenarios such as defending brand guidelines against a stakeholder, navigating a brand or PR crisis, and aligning cross-functional teams on brand voice",
    "seo": "scenarios such as a traffic drop after an algorithm update, engineering pushback on technical SEO fixes, and prioritizing SEO work against other roadmap items",
    "content_marketing": "scenarios such as a missed editorial deadline, pivoting a low-performing content series, and stakeholder pushback on content direction",
    "product_marketing": "scenarios such as messaging misalignment with sales, an underperforming product launch, and cross-functional pushback from product or engineering",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    fundamentals_block = FUNDAMENTALS_BY_SUBROLE[subrole]

    opening_section = (
        """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on marketing campaigns, internships, projects, branding initiatives, leadership, certifications, measurable results and achievements.
- Use the resume extensively."""
        if resume_text
        else """1. Role-Specific Marketing Questions (3)

Generate exactly 3 additional role-specific marketing questions because no resume is available."""
    )

    return f"""{header}

This is Round 1 of a multi-round Marketing interview: Fundamentals & Analytics. Do NOT ask Campaign Case Study or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Marketing Fundamentals (4)

Generate exactly 4 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must strictly match the selected difficulty.

3. Marketing Analytics Questions (3)

Generate exactly 3 role-specific marketing questions.

Examples include:

- Digital Marketing
- Brand Management
- Product Marketing
- Performance Marketing
- Growth Marketing
- SEO Specialist
- Content Marketing
- Marketing Analytics

Questions should evaluate practical marketing knowledge and decision-making.

{OPTIONAL_CODING_STRUCTURE}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different marketing competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Marketing Analytics Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    case_focus = _CASE_STUDY_FOCUS_BY_SUBROLE.get(subrole, _CASE_STUDY_FOCUS_BY_SUBROLE["generic"])

    difficulty_guidelines = """Difficulty Guidelines:

Easy
- Basic campaign planning
- Product promotion
- Brand awareness

Medium
- Campaign optimization
- Budget allocation
- Performance improvement

Hard
- Multi-channel marketing strategy
- Growth experiments
- Data-driven campaign decisions
- Scaling marketing initiatives"""

    if resume_text:

        return f"""{header}

This is Round 2 of a multi-round Marketing interview: Campaign Case Studies. Do NOT ask Fundamentals, Analytics, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure

1. Resume-Grounded Case Study (1)

- Ask exactly 1 campaign case-study question that builds on a campaign, project, or initiative mentioned in the candidate's resume.
- Ask the candidate to analyze, extend or reconsider a marketing decision from their own experience.

2. Campaign Case Studies (6)

Generate exactly 6 campaign-based case study questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 7 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different marketing competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""{header}

This is Round 2 of a multi-round Marketing interview: Campaign Case Studies. Do NOT ask Fundamentals, Analytics, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

Campaign Case Studies (6)

Generate exactly 6 campaign-based case study questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different marketing competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their campaigns, projects, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Marketing interview: HR / Behavioral. Do NOT ask Fundamentals, Analytics, or Campaign Case Study questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across creativity under constraints, ownership, cross-functional communication, handling underperformance, and decision-making with incomplete data - do not repeat the same theme.

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


def build_marketing_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Marketing interview.
    round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_marketing_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
