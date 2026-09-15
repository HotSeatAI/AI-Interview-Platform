"""
Round-based Finance interview prompts.

Splits the single monolithic build_finance_prompt() interview into
three separate, standalone rounds a candidate can practice one at a
time:

- Round 1: Fundamentals & Technicals
- Round 2: Case Studies
- Round 3: HR / Behavioral

Each sub-role from classify_finance_subrole() (generic,
investment_banking_pe, equity_research, corporate_finance_treasury,
risk_management, venture_capital) gets its own round labels and
content. Round 1 reuses that sub-role's existing fundamentals content
from finance_prompt.py; Round 2's case-study focus and Round 3's HR
scenario grounding are new content (see _CASE_STUDY_FOCUS_BY_SUBROLE
and _HR_CONTEXT_BY_SUBROLE below).

This module is purely additive: finance_prompt.py's build_finance_prompt
is untouched and still used whenever a round isn't requested (see
AIService.generate_questions). Round keys ("round_1"/"round_2"/"round_3")
are shared across domains - the canonical ROUND_KEYS set lives in
software_rounds.py and is imported directly from there by callers
(e.g. AIService.generate_questions), not redefined here.
"""

from app.services.role_classifier import classify_finance_subrole
from app.services.prompts.finance_prompt import FUNDAMENTALS_BY_SUBROLE
from app.services.prompts.finance_common import (
    OPTIONAL_CODING_STRUCTURE,
    STYLE_GUIDELINES,
    QUESTION_LENGTH_STYLE,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Finance Fundamentals & Technicals", "description": "Accounting, financial statements, valuation basics, plus role-specific technical questions."},
        {"key": "round_2", "label": "Round 2: Finance Case Studies", "description": "Business situations, financial analysis, and multi-step valuation/strategy case studies."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Reporting deadlines, manager disagreements, and communicating bad financial news."},
    ],
    "investment_banking_pe": [
        {"key": "round_1", "label": "Round 1: IB/PE Fundamentals & Technicals", "description": "Enterprise vs equity value, DCF, comps, precedent transactions, plus technicals."},
        {"key": "round_2", "label": "Round 2: Deal & LBO Case Studies", "description": "LBO modeling, deal structuring, and synergies/accretion-dilution analysis."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Deal-closing crunches, conflicting priorities, and pushback from senior bankers."},
    ],
    "equity_research": [
        {"key": "round_1", "label": "Round 1: Equity Research Fundamentals & Technicals", "description": "Financial statements, ratio analysis, industry basics, DCF, comps, earnings models."},
        {"key": "round_2", "label": "Round 2: Valuation & Stock Pitch Case Studies", "description": "DCF/comps-based stock pitches, earnings walkthroughs, and industry analysis."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Defending a controversial call, management pressure, and correcting published errors."},
    ],
    "corporate_finance_treasury": [
        {"key": "round_1", "label": "Round 1: Corporate Finance & Treasury Fundamentals", "description": "Working capital, capital budgeting, cost of capital, cash flow forecasting."},
        {"key": "round_2", "label": "Round 2: Capital & Liquidity Case Studies", "description": "Capital structure decisions, liquidity and cash management, financial risk hedging."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Budget disputes, justifying rejected projects, and managing a liquidity crunch."},
    ],
    "risk_management": [
        {"key": "round_1", "label": "Round 1: Risk Fundamentals & Technicals", "description": "Risk types, Value at Risk, hedging strategies, credit risk assessment."},
        {"key": "round_2", "label": "Round 2: Stress-Testing & Hedging Case Studies", "description": "VaR scenarios, stress testing, hedging design, and regulatory capital (Basel)."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Escalating a limit breach, disagreeing with a trading desk, and explaining model limits."},
    ],
    "venture_capital": [
        {"key": "round_1", "label": "Round 1: VC Fundamentals & Technicals", "description": "Cap tables, startup valuation (VC method), market sizing, term sheets."},
        {"key": "round_2", "label": "Round 2: Startup Valuation & Diligence Case Studies", "description": "VC-method valuation, cap table scenarios, due diligence, and exit strategy."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Saying no to a founder, partner disagreements, and diligence red flags under pressure."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    finance sub-role. Falls back to "generic" for any unrecognized
    value so this never returns an empty list for a role already
    known to be in the finance domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_CASE_STUDY_FOCUS_BY_SUBROLE = {
    "generic": "simple business situations, then financial analysis and investment decisions, then multi-step valuation, risk analysis and strategic financial decisions",
    "investment_banking_pe": "LBO modeling, deal structuring, and synergies/accretion-dilution analysis",
    "equity_research": "DCF- and comps-based stock pitches, earnings model walkthroughs, and industry/company analysis",
    "corporate_finance_treasury": "capital structure decisions, liquidity and cash management, and financial risk hedging",
    "risk_management": "VaR scenarios, stress testing, hedging strategy design, and regulatory capital (Basel) questions",
    "venture_capital": "VC-method startup valuation, cap table scenarios, due diligence red flags, and exit strategy",
}


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as tight reporting deadlines, disagreements with a manager over an analysis, and communicating bad financial news to stakeholders",
    "investment_banking_pe": "scenarios such as all-nighters before a deal closes, conflicting priorities across live deals, and pushback from senior bankers on a pitch book",
    "equity_research": "scenarios such as defending a controversial stock call, pressure from a covered company's management, and correcting a published error in a report",
    "corporate_finance_treasury": "scenarios such as budget disputes with business unit heads, justifying a rejected capital project, and managing a liquidity crunch",
    "risk_management": "scenarios such as escalating a limit breach, disagreeing with a trading desk over risk exposure, and explaining a risk model's limitations to auditors",
    "venture_capital": "scenarios such as saying no to a founder you like, disagreeing with a partner over an investment thesis, and handling due diligence red flags under time pressure",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    fundamentals_block = FUNDAMENTALS_BY_SUBROLE[subrole]

    opening_section = (
        """1. Resume-Based Questions (3)

- Ask exactly 3 questions from the candidate's resume.
- Focus on internships, financial projects, certifications, investment experience, accounting knowledge, leadership and achievements."""
        if resume_text
        else """1. Role-Specific Questions (3)

Generate exactly 3 finance role-specific questions because no resume is available."""
    )

    return f"""{header}

This is Round 1 of a multi-round Finance interview: Fundamentals & Technicals. Do NOT ask Case Study or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Finance Fundamentals (4)

Generate exactly 4 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must match the selected difficulty.

3. Role-Specific Technical Questions (3)

Generate exactly 3 questions specifically related to the selected role.

Examples include:

- Investment Banking
- Equity Research
- Corporate Finance
- Risk Management
- Financial Analyst
- Treasury
- Asset Management
- Private Equity
- Venture Capital

Match the difficulty.

{OPTIONAL_CODING_STRUCTURE}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different finance competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Role-Specific Technical Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    case_focus = _CASE_STUDY_FOCUS_BY_SUBROLE.get(subrole, _CASE_STUDY_FOCUS_BY_SUBROLE["generic"])

    difficulty_guidelines = """Difficulty Guidelines:

Easy
- Simple business situations

Medium
- Financial analysis and investment decisions

Hard
- Multi-step valuation, risk analysis and strategic financial decisions"""

    if resume_text:

        return f"""{header}

This is Round 2 of a multi-round Finance interview: Case Studies. Do NOT ask Fundamentals, Technical, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure

1. Resume-Grounded Case Study (1)

- Ask exactly 1 case-study question that builds on a project, deal, or experience mentioned in the candidate's resume.
- Ask the candidate to analyze, extend or reconsider a financial decision from their own experience.

2. Case Study Questions (6)

Generate exactly 6 real interview case-study questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 7 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different finance competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""{header}

This is Round 2 of a multi-round Finance interview: Case Studies. Do NOT ask Fundamentals, Technical, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

Case Study Questions (6)

Generate exactly 6 real interview case-study questions, focused on {case_focus}.

{difficulty_guidelines}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different finance competencies.
- Do NOT provide answers, hints or explanations.

{QUESTION_LENGTH_STYLE}

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their deals, projects, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Finance interview: HR / Behavioral. Do NOT ask Fundamentals, Technical, or Case Study questions in this round - those are separate rounds.

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


def build_finance_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Finance interview.
    round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_finance_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
