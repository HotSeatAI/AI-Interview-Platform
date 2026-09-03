"""
Round-based Analog Design interview prompts.

Splits the single monolithic build_analog_design_prompt() interview
into three separate, standalone rounds a candidate can practice one
at a time:

- Round 1: Analog Electronics Fundamentals
- Round 2: Circuit Analysis & Analog IC Design (sub-role flavored)
- Round 3: HR / Behavioral

Analog Electronics Fundamentals (Round 1) is identical across both
sub-roles in the source prompt, same as VLSI's RTL & Digital Design
round and Digital Design's Fundamentals round. Round 2 combines the
shared "Circuit Analysis & Design" section with the ONE sub-role-
tailored section in this domain, "Analog IC Design Concepts"
(_IC_DESIGN_CONCEPTS_BY_SUBROLE) - mirroring exactly how VLSI's
Round 2 merges its shared ASIC-flow section with its sub-role-
tailored STA section.

Like vlsi_rounds.py and digital_design_rounds.py, this module has no
coding-question structure and no "Question Length & Style" block,
matching the source prompt. It also preserves the source prompt's
resume/no-resume asymmetry: the no-resume "generic" IC-design topic
list is shorter than the resume-branch version, while "mixed_signal"
uses the identical list in both branches (a direct reference in the
source, not a separate list) - and the no-resume "Circuit Analysis &
Design" section drops its Easy/Medium/Hard tiering entirely in favor
of one flat topic list, which is also preserved as-is.

This module is purely additive: analog_design_prompt.py's
build_analog_design_prompt is untouched and still used whenever a
round isn't requested (see AIService.generate_questions). Round keys
("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_analog_subrole
from app.services.prompts.analog_design_prompt import (
    IC_DESIGN_CONCEPTS_BY_SUBROLE,
    IC_DESIGN_CONCEPTS_BY_SUBROLE_NO_RESUME,
)
from app.services.prompts.analog_design_common import (
    STYLE_GUIDELINES,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Analog Electronics Fundamentals", "description": "Diodes, BJT, MOSFET, op-amps, differential amplifiers, current mirrors, stability, noise analysis."},
        {"key": "round_2", "label": "Round 2: Circuit Analysis & Analog IC Design", "description": "Biasing, gain, active filters, oscillators, plus ADC/DAC/PLL/bandgap IC design concepts."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A circuit missing spec after layout, late-found noise/stability bugs, and cross-team trade-off explanations."},
    ],
    "mixed_signal": [
        {"key": "round_1", "label": "Round 1: Analog Electronics Fundamentals", "description": "Diodes, BJT, MOSFET, op-amps, differential amplifiers, current mirrors, stability, noise analysis."},
        {"key": "round_2", "label": "Round 2: Circuit Analysis & Mixed-Signal IC Design", "description": "Biasing, gain, filters, plus ADC/DAC architectures, SNR/ENOB/SFDR, and digital-analog interfacing."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "An ADC/DAC missing its SNR/ENOB spec, late integration issues, and debugging sampling artifacts."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    Analog Design sub-role. Falls back to "generic" for any
    unrecognized value so this never returns an empty list for a role
    already known to be in the analog_design domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as a circuit that misses spec after layout, debugging a noise or stability issue found late, and explaining a design trade-off to a digital-side teammate",
    "mixed_signal": "scenarios such as an ADC or DAC missing its SNR/ENOB spec, a digital-analog interface issue discovered late in integration, and debugging aliasing or sampling artifacts",
}


_FUNDAMENTALS_TOPICS = """Easy

- Diodes
- BJT
- MOSFET
- Basic Amplifiers
- Operational Amplifiers

Medium

- Differential Amplifiers
- Small Signal Analysis
- Current Mirrors
- Frequency Response
- Feedback

Hard

- Compensation
- Stability
- Noise Analysis
- Analog IC Design Trade-offs
- High-Speed Analog Circuits"""

_FUNDAMENTALS_TOPICS_NO_RESUME = """Easy

- Diodes
- MOSFET
- BJT
- Operational Amplifiers

Medium

- Differential Amplifiers
- Current Mirrors
- Frequency Response

Hard

- Stability
- Compensation
- Noise Analysis"""

_CIRCUIT_ANALYSIS_TOPICS = """Easy

- Biasing
- Gain
- Input / Output Resistance

Medium

- Frequency Response
- Bandwidth
- Active Filters
- Oscillators

Hard

- Multi-stage Amplifiers
- Compensation Techniques
- Power Optimization
- Precision Circuits"""

_CIRCUIT_ANALYSIS_TOPICS_NO_RESUME = """- Biasing
- Gain
- Active Filters
- Oscillators
- Feedback"""


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:
        opening_section = """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on analog circuit projects, internships, PCB design, analog IC design, simulations, debugging, optimizations, research work and achievements."""
        fundamentals_block = _FUNDAMENTALS_TOPICS
    else:
        opening_section = """1. Role-Specific Analog Design Questions (3)

Generate exactly 3 additional role-specific analog design questions because no resume is available."""
        fundamentals_block = _FUNDAMENTALS_TOPICS_NO_RESUME

    return f"""{header}

This is Round 1 of a multi-round Analog Design interview: Analog Electronics Fundamentals. Do NOT ask Circuit Analysis, Analog IC Design, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Analog Electronics Fundamentals (7)

Generate exactly 7 questions.

Difficulty Guidelines

{fundamentals_block}

Questions must strictly match the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Analog Design competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:

        ic_design_block = IC_DESIGN_CONCEPTS_BY_SUBROLE[subrole]

        return f"""{header}

This is Round 2 of a multi-round Analog Design interview: Circuit Analysis & Analog IC Design. Do NOT ask Analog Electronics Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

1. Resume-Grounded Question (1)

- Ask exactly 1 question that builds on an analog circuit or IC design project mentioned in the candidate's resume.
- Ask the candidate to walk through how they approached, or would now approach, that situation.

2. Circuit Analysis & Design (2)

Generate exactly 2 questions.

Topics include:

{_CIRCUIT_ANALYSIS_TOPICS}

3. Analog IC Design Concepts (3)

Generate exactly 3 questions.

Topics include:

{ic_design_block}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Analog Design competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    ic_design_block_no_resume = IC_DESIGN_CONCEPTS_BY_SUBROLE_NO_RESUME[subrole]

    return f"""{header}

This is Round 2 of a multi-round Analog Design interview: Circuit Analysis & Analog IC Design. Do NOT ask Analog Electronics Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 5 interview questions.

Interview Structure

1. Circuit Analysis & Design (2)

Generate exactly 2 questions.

Topics include:

{_CIRCUIT_ANALYSIS_TOPICS_NO_RESUME}

2. Analog IC Design Concepts (3)

Generate exactly 3 questions.

Topics include:

{ic_design_block_no_resume}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Analog Design competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_3(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)
    hr_context = _HR_CONTEXT_BY_SUBROLE.get(subrole, _HR_CONTEXT_BY_SUBROLE["generic"])

    resume_note = (
        "Where relevant, ground behavioral questions in the candidate's own resume - their projects, designs, and achievements - rather than asking fully generic questions."
        if resume_text
        else "The candidate has not provided a resume, so keep behavioral questions role-generic."
    )

    return f"""{header}

This is Round 3 of a multi-round Analog Design interview: HR / Behavioral. Do NOT ask Analog Electronics Fundamentals, Circuit Analysis, or Analog IC Design questions in this round - those are separate rounds.

Generate EXACTLY 5 behavioral interview questions.

Interview Structure

Behavioral Questions (5)

Ground the questions in {hr_context}, and other realistic on-the-job situations for this role.

{resume_note}

Cover a variety of themes across ownership, cross-team communication, handling schedule pressure, catching mistakes, and decision-making under uncertainty - do not repeat the same theme.

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


def build_analog_design_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of an Analog Design
    interview. round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_analog_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
