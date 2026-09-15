"""
Round-based Digital Design interview prompts.

Splits the single monolithic build_digital_design_prompt() interview
into three separate, standalone rounds a candidate can practice one
at a time:

- Round 1: Digital Design Fundamentals
- Round 2: Computer Architecture & RTL/Verification (sub-role flavored)
- Round 3: HR / Behavioral

Digital Design Fundamentals (Round 1) is identical across all 3
sub-roles in the source prompt, same as VLSI's RTL & Digital Design
round. Round 2 is where BOTH of the source prompt's sub-role dicts
live, and each one only tailors a DIFFERENT sub-role - preserved
exactly as-is:

- _COMPUTER_ARCH_BLOCK_BY_SUBROLE: "fpga" gets FPGA-specific topics;
  "verification_dv" silently falls back to "generic"'s topics.
- _RTL_VERIFICATION_BLOCK_BY_SUBROLE: "verification_dv" gets DV
  topics (UVM/SVA/formal verification); "fpga" silently falls back to
  "generic"'s Verilog/SystemVerilog topics.

So a fpga round 2 gets FPGA-flavored architecture but generic
RTL/verification content; a verification_dv round 2 gets generic
architecture but DV-flavored RTL/verification content. No new
tailoring is invented for the sub-role that doesn't already have it
in the source prompt. The no-resume "generic" Computer Architecture
branch also has no topic list at all (just "Difficulty must match the
selected level.") - preserved via the same _COMPUTER_ARCH_TAIL_BY_SUBROLE
dict the source prompt uses.

Like vlsi_rounds.py, this module has no coding-question structure and
no "Question Length & Style" block, matching the source prompt.

This module is purely additive: digital_design_prompt.py's
build_digital_design_prompt is untouched and still used whenever a
round isn't requested (see AIService.generate_questions). Round keys
("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_digital_design_subrole
from app.services.prompts.digital_design_prompt import (
    COMPUTER_ARCH_BLOCK_BY_SUBROLE,
    COMPUTER_ARCH_TAIL_BY_SUBROLE,
    RTL_VERIFICATION_BLOCK_BY_SUBROLE,
    RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME,
    COMPUTER_ARCHITECTURE_TOPICS,
    RTL_VERIFICATION_TOPICS,
    RTL_VERIFICATION_TOPICS_NO_RESUME,
)
from app.services.prompts.digital_design_common import (
    STYLE_GUIDELINES,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Digital Design Fundamentals", "description": "Boolean algebra, FSM, sequential/combinational logic, metastability, CDC, timing closure."},
        {"key": "round_2", "label": "Round 2: Computer Architecture & RTL/Verification", "description": "CPU basics, pipelining, cache/memory hierarchy, plus Verilog/SystemVerilog and testbenches."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Hard-to-reproduce timing bugs, RTL design disagreements, and explaining trade-offs to stakeholders."},
    ],
    "fpga": [
        {"key": "round_1", "label": "Round 1: Digital Design Fundamentals", "description": "Boolean algebra, FSM, sequential/combinational logic, metastability, CDC, timing closure."},
        {"key": "round_2", "label": "Round 2: FPGA Architecture & RTL/Verification", "description": "FPGA basics, LUTs/CLBs, timing constraints, tool flow, plus Verilog/SystemVerilog and testbenches."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Running out of FPGA resources, hardware-only timing failures, and partial-reconfiguration debugging."},
    ],
    "verification_dv": [
        {"key": "round_1", "label": "Round 1: Digital Design Fundamentals", "description": "Boolean algebra, FSM, sequential/combinational logic, metastability, CDC, timing closure."},
        {"key": "round_2", "label": "Round 2: Computer Architecture & Verification (UVM/DV)", "description": "CPU basics and pipelining, plus UVM, functional coverage, SVA, and formal verification."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Verification gaps that miss real bugs, coverage disagreements, and regression time trade-offs."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    Digital Design sub-role. Falls back to "generic" for any
    unrecognized value so this never returns an empty list for a role
    already known to be in the digital_design domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as a hard-to-reproduce timing bug, disagreeing with a teammate on an RTL implementation choice, and explaining a design trade-off to a non-hardware stakeholder",
    "fpga": "scenarios such as running out of FPGA resources late in a project, a design that fails timing closure only on hardware, and debugging an issue that only appears after partial reconfiguration",
    "verification_dv": "scenarios such as a verification environment that misses a real bug, disagreeing with an RTL designer over test coverage, and justifying more time for regression before tapeout",
}


_FUNDAMENTALS_TOPICS = """Easy
- Boolean Algebra
- Logic Gates
- Flip-Flops
- Latches
- Counters
- Registers
- FSM Basics

Medium
- FSM Design
- Sequential Logic
- Combinational Logic
- Timing Diagrams
- Clock Domains
- Digital Circuit Design

Hard
- Metastability
- Clock Domain Crossing (CDC)
- Setup and Hold Timing
- Clock Skew
- Timing Closure
- Synchronous Design Trade-offs"""

_FUNDAMENTALS_TOPICS_NO_RESUME = """Easy
- Boolean Algebra
- Logic Gates
- Flip-Flops
- Latches
- Counters

Medium
- FSM
- Sequential Logic
- Timing Diagrams
- Clock Domains

Hard
- Metastability
- Setup and Hold Timing
- Clock Domain Crossing
- Timing Closure"""


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:
        opening_section = """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on internships, digital design projects, FPGA work, Verilog/SystemVerilog, RTL implementation, computer architecture, optimizations, debugging, leadership and achievements."""
        fundamentals_block = _FUNDAMENTALS_TOPICS
    else:
        opening_section = """1. Role-Specific Digital Design Questions (3)

Generate exactly 3 additional role-specific Digital Design questions because no resume is available."""
        fundamentals_block = _FUNDAMENTALS_TOPICS_NO_RESUME

    return f"""{header}

This is Round 1 of a multi-round Digital Design interview: Digital Design Fundamentals. Do NOT ask Computer Architecture, RTL/Verification, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Digital Design Fundamentals (7)

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
- Cover different Digital Design competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:

        computer_arch_block = COMPUTER_ARCH_BLOCK_BY_SUBROLE.get(subrole, COMPUTER_ARCHITECTURE_TOPICS)
        rtl_verification_block = RTL_VERIFICATION_BLOCK_BY_SUBROLE.get(subrole, RTL_VERIFICATION_TOPICS)

        return f"""{header}

This is Round 2 of a multi-round Digital Design interview: Computer Architecture & RTL/Verification. Do NOT ask Digital Design Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

1. Resume-Grounded Question (1)

- Ask exactly 1 question that builds on a computer architecture, RTL, or verification project mentioned in the candidate's resume.
- Ask the candidate to walk through how they approached, or would now approach, that situation.

2. Computer Architecture (2)

Generate exactly 2 questions.

Topics may include:

{computer_arch_block}

3. RTL Design & Verification (3)

Generate exactly 3 questions.

Topics include:

{rtl_verification_block}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Digital Design competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    computer_arch_tail = COMPUTER_ARCH_TAIL_BY_SUBROLE.get(subrole, COMPUTER_ARCH_TAIL_BY_SUBROLE["generic"])
    rtl_verification_block_no_resume = RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, RTL_VERIFICATION_TOPICS_NO_RESUME
    )

    return f"""{header}

This is Round 2 of a multi-round Digital Design interview: Computer Architecture & RTL/Verification. Do NOT ask Digital Design Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 5 interview questions.

Interview Structure

1. Computer Architecture (2)

Generate exactly 2 questions.

{computer_arch_tail}

2. RTL Design & Verification (3)

Generate exactly 3 questions.

Topics include:

{rtl_verification_block_no_resume}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Digital Design competencies.
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

This is Round 3 of a multi-round Digital Design interview: HR / Behavioral. Do NOT ask Digital Design Fundamentals, Computer Architecture, or RTL/Verification questions in this round - those are separate rounds.

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


def build_digital_design_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a Digital Design
    interview. round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_digital_design_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
