"""
Round-based VLSI interview prompts.

Splits the single monolithic build_vlsi_prompt() interview into three
separate, standalone rounds a candidate can practice one at a time:

- Round 1: RTL & Digital Design
- Round 2: ASIC Flow, Physical Design & Timing (sub-role flavored)
- Round 3: HR / Behavioral

Unlike the business domains (finance/consulting/sales/marketing),
vlsi_prompt.py's "RTL & Digital Design" and "ASIC Design Flow &
Physical Design" sections use the SAME fixed topic list for every
sub-role - only "Static Timing Analysis & VLSI Concepts" is sub-role
keyed (via _STA_CONCEPTS_BY_SUBROLE). That asymmetry is preserved
here rather than inventing new per-sub-role RTL/ASIC-flow content
that doesn't exist in the source prompt: Round 1 is identical across
sub-roles, and only Round 2's STA-concepts portion (plus its label)
varies by sub-role. Round 3's HR scenario grounding is new content
(see _HR_CONTEXT_BY_SUBROLE below).

VLSI also has no "optional coding" structured question block at all
(RTL/Verilog questions stay conversational, not TYPE: CODING) and no
"Question Length & Style" section - both intentionally absent here
too, matching the source prompt.

This module is purely additive: vlsi_prompt.py's build_vlsi_prompt is
untouched and still used whenever a round isn't requested (see
AIService.generate_questions). Round keys ("round_1"/"round_2"/
"round_3") are shared across domains - the canonical ROUND_KEYS set
lives in software_rounds.py and is imported directly from there by
callers (e.g. AIService.generate_questions), not redefined here.
"""

from app.services.role_classifier import classify_vlsi_subrole
from app.services.prompts.vlsi_prompt import (
    STA_CONCEPTS_BY_SUBROLE,
    STA_CONCEPTS_BY_SUBROLE_NO_RESUME,
)
from app.services.prompts.vlsi_common import (
    STYLE_GUIDELINES,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: RTL & Digital Design", "description": "RTL basics, Verilog, SystemVerilog, CDC, reset strategies, and low-power RTL."},
        {"key": "round_2", "label": "Round 2: ASIC Flow, Physical Design & Timing", "description": "Synthesis, floorplanning, CTS, routing, timing closure, and core STA concepts."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Timing pressure before tapeout, design-lead disagreements, and late-found bugs."},
    ],
    "physical_design": [
        {"key": "round_1", "label": "Round 1: RTL & Digital Design", "description": "RTL basics, Verilog, SystemVerilog, CDC, reset strategies, and low-power RTL."},
        {"key": "round_2", "label": "Round 2: Physical Design & Timing Closure", "description": "Floorplanning, placement/routing trade-offs, CTS, timing closure, IR drop/EM."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Late floorplan reworks, IR drop/congestion near tapeout, and RTL-team pushback."},
    ],
    "dft": [
        {"key": "round_1", "label": "Round 1: RTL & Digital Design", "description": "RTL basics, Verilog, SystemVerilog, CDC, reset strategies, and low-power RTL."},
        {"key": "round_2", "label": "Round 2: DFT, ASIC Flow & Test Strategy", "description": "Scan insertion, ATPG, test compression, BIST, boundary scan, fault coverage."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Low fault coverage found late, DFT overhead disputes, and silicon bring-up debug."},
    ],
    "sta_timing": [
        {"key": "round_1", "label": "Round 1: RTL & Digital Design", "description": "RTL basics, Verilog, SystemVerilog, CDC, reset strategies, and low-power RTL."},
        {"key": "round_2", "label": "Round 2: Static Timing Analysis & Closure", "description": "Setup/hold analysis, clock skew/jitter, timing exceptions, MCMM, SSTA."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Timing violations near tapeout, constraint disagreements, and corner-case failures."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    VLSI sub-role. Falls back to "generic" for any unrecognized value
    so this never returns an empty list for a role already known to
    be in the vlsi domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as pressure to close timing before tapeout, disagreeing with a design lead on an implementation choice, and catching a bug late in verification",
    "physical_design": "scenarios such as a floorplan rework late in the schedule, IR drop or congestion issues discovered near tapeout, and pushback from the RTL team on timing constraints",
    "dft": "scenarios such as low fault coverage discovered late, disagreements with design teams over DFT area/timing overhead, and debugging a failing scan pattern in silicon bring-up",
    "sta_timing": "scenarios such as a timing violation found close to tapeout, disagreeing with the physical design team over constraint changes, and explaining a corner-case timing failure to stakeholders",
}


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    opening_section = (
        """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on RTL design, ASIC projects, FPGA work, physical design, verification, synthesis, timing analysis, internships, optimizations and achievements."""
        if resume_text
        else """1. Role-Specific VLSI Questions (3)

Generate exactly 3 additional VLSI role-specific questions because no resume is available."""
    )

    return f"""{header}

This is Round 1 of a multi-round VLSI interview: RTL & Digital Design. Do NOT ask ASIC Flow, Physical Design, Timing, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. RTL & Digital Design (7)

Generate exactly 7 questions.

Difficulty Guidelines

Easy

- RTL Basics
- Verilog
- FSM
- Counters
- Registers

Medium

- SystemVerilog
- Blocking vs Non-blocking
- Synchronous Design
- FSM Optimization

Hard

- CDC
- Reset Strategies
- RTL Optimization
- Low Power RTL

Questions must strictly match the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different VLSI competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    asic_flow_section = """2. ASIC Design Flow & Physical Design (3)

Generate exactly 3 questions.

Topics include:

Easy

- ASIC Design Flow
- Synthesis
- Constraints

Medium

- Floorplanning
- Placement
- Clock Tree Synthesis
- Routing

Hard

- Congestion
- Timing Closure
- IR Drop
- EM
- Physical Verification"""

    if resume_text:

        sta_block = STA_CONCEPTS_BY_SUBROLE[subrole]

        return f"""{header}

This is Round 2 of a multi-round VLSI interview: ASIC Flow, Physical Design & Timing. Do NOT ask RTL, Behavioral, or HR questions in this round - those are separate rounds.

Generate EXACTLY 7 interview questions.

Interview Structure

1. Resume-Grounded Design/Timing Question (1)

- Ask exactly 1 question that builds on a physical design, timing closure, or ASIC flow experience mentioned in the candidate's resume.
- Ask the candidate to walk through how they approached, or would now approach, that situation.

{asic_flow_section}

3. Static Timing Analysis & VLSI Concepts (3)

Generate exactly 3 questions.

Topics include:

{sta_block}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 7 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different VLSI competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    sta_block_no_resume = STA_CONCEPTS_BY_SUBROLE_NO_RESUME[subrole]

    return f"""{header}

This is Round 2 of a multi-round VLSI interview: ASIC Flow, Physical Design & Timing. Do NOT ask RTL, Behavioral, or HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

{asic_flow_section.replace("2. ", "1. ", 1)}

2. Static Timing Analysis & VLSI Concepts (3)

Generate exactly 3 questions.

Topics include:

{sta_block_no_resume}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different VLSI competencies.
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

This is Round 3 of a multi-round VLSI interview: HR / Behavioral. Do NOT ask RTL, ASIC Flow, Physical Design, or Timing questions in this round - those are separate rounds.

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


def build_vlsi_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of a VLSI interview.
    round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_vlsi_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
