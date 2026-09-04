"""
Round-based Embedded Systems interview prompts.

Splits the single monolithic build_embedded_systems_prompt()
interview into three separate, standalone rounds a candidate can
practice one at a time:

- Round 1: Embedded C & Programming Fundamentals
- Round 2: Microcontrollers, Protocols & RTOS (sub-role flavored)
- Round 3: HR / Behavioral

Embedded C & Programming Fundamentals (Round 1) is identical across
all 4 sub-roles in the source prompt, same as the fundamentals round
in every other hardware domain done so far. Round 2 is where BOTH of
the source prompt's sub-role dicts live - unlike Digital Design's
asymmetric dicts, both _PROTOCOLS_BLOCK_BY_SUBROLE and
_RTOS_BLOCK_BY_SUBROLE have distinct, real content for all 4
sub-roles (generic, embedded_linux, iot, automotive_embedded), with
no silent fallback to "generic" for any of them - making Round 2 the
most fully-specialized round of any hardware domain shipped so far.

Like vlsi_rounds.py / digital_design_rounds.py / analog_design_rounds.py,
this module has no coding-question structure and no "Question Length
& Style" block, matching the source prompt. It also preserves the
source prompt's resume/no-resume asymmetry: "generic"'s no-resume
topic lists are shorter/different than its resume-branch lists, while
"embedded_linux"/"iot"/"automotive_embedded" use identical lists in
both branches (direct references in the source, not separate lists).

This module is purely additive: embedded_systems_prompt.py's
build_embedded_systems_prompt is untouched and still used whenever a
round isn't requested (see AIService.generate_questions). Round keys
("round_1"/"round_2"/"round_3") are shared across domains - the
canonical ROUND_KEYS set lives in software_rounds.py and is imported
directly from there by callers (e.g. AIService.generate_questions),
not redefined here.
"""

from app.services.role_classifier import classify_embedded_subrole
from app.services.prompts.embedded_systems_prompt import (
    PROTOCOLS_BLOCK_BY_SUBROLE,
    PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME,
    RTOS_BLOCK_BY_SUBROLE,
    RTOS_BLOCK_BY_SUBROLE_NO_RESUME,
)
from app.services.prompts.embedded_systems_common import (
    STYLE_GUIDELINES,
    build_role_header,
)


_ROUND_LABELS_BY_SUBROLE = {
    "generic": [
        {"key": "round_1", "label": "Round 1: Embedded C & Programming Fundamentals", "description": "Pointers, structures, memory basics, bit manipulation, linker scripts, undefined behavior."},
        {"key": "round_2", "label": "Round 2: Microcontrollers, Protocols & RTOS", "description": "GPIO/UART/SPI/I2C/CAN/DMA/interrupts plus RTOS, scheduling, semaphores, and deadlocks."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Hard-to-reproduce field bugs, late-found race conditions, and cross-team trade-off explanations."},
    ],
    "embedded_linux": [
        {"key": "round_1", "label": "Round 1: Embedded C & Programming Fundamentals", "description": "Pointers, structures, memory basics, bit manipulation, linker scripts, undefined behavior."},
        {"key": "round_2", "label": "Round 2: Embedded Linux Kernel & Device Drivers", "description": "Device tree, bootloader/U-Boot, cross-compilation plus kernel internals, modules, and device drivers."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Kernel panics only on target hardware, driver portability issues, and boot-failure debugging."},
    ],
    "iot": [
        {"key": "round_1", "label": "Round 1: Embedded C & Programming Fundamentals", "description": "Pointers, structures, memory basics, bit manipulation, linker scripts, undefined behavior."},
        {"key": "round_2", "label": "Round 2: IoT Connectivity & Power Management", "description": "BLE/Zigbee/LoRaWAN, MQTT/CoAP, low-power design plus OTA updates, IoT security, and edge computing."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "Battery drain in the field, an OTA update that bricks devices, and fleet-wide connectivity diagnosis."},
    ],
    "automotive_embedded": [
        {"key": "round_1", "label": "Round 1: Embedded C & Programming Fundamentals", "description": "Pointers, structures, memory basics, bit manipulation, linker scripts, undefined behavior."},
        {"key": "round_2", "label": "Round 2: Automotive Protocols & Functional Safety", "description": "CAN/LIN/FlexRay plus AUTOSAR, ISO 26262 functional safety, and UDS/OBD-II diagnostics."},
        {"key": "round_3", "label": "Round 3: HR / Behavioral", "description": "A functional-safety review blocking a release, CAN timing issues, and safety-auditor justifications."},
    ],
}


def get_rounds_for_subrole(subrole: str) -> list[dict]:
    """
    Returns the 3-round catalog (key/label/description) for a given
    Embedded Systems sub-role. Falls back to "generic" for any
    unrecognized value so this never returns an empty list for a role
    already known to be in the embedded_systems domain.
    """

    return _ROUND_LABELS_BY_SUBROLE.get(subrole, _ROUND_LABELS_BY_SUBROLE["generic"])


_HR_CONTEXT_BY_SUBROLE = {
    "generic": "scenarios such as a hard-to-reproduce firmware bug that only shows up in the field, a race condition or priority-inversion issue found late, and explaining a low-level trade-off to a non-embedded stakeholder",
    "embedded_linux": "scenarios such as a kernel panic discovered only on target hardware, a driver that works on one kernel version but not another, and debugging a boot failure with limited serial access",
    "iot": "scenarios such as a device that drains its battery faster than spec in the field, an OTA update that bricks a subset of devices, and diagnosing a connectivity issue across thousands of deployed units",
    "automotive_embedded": "scenarios such as a functional-safety review that blocks a release, a CAN bus timing issue found during vehicle integration, and justifying a design choice to a safety auditor",
}


_FUNDAMENTALS_TOPICS = """Easy
- C Programming
- Pointers
- Arrays
- Structures
- Memory Basics

Medium
- Function Pointers
- Dynamic Memory
- Bit Manipulation
- Volatile
- Const
- Memory Layout

Hard
- Linker Scripts
- Memory Optimization
- Undefined Behavior
- Low-level Programming
- Compiler Optimizations"""

_FUNDAMENTALS_TOPICS_NO_RESUME = """Easy
- C Programming
- Pointers
- Arrays
- Structures

Medium
- Function Pointers
- Bit Manipulation
- Volatile
- Memory Layout

Hard
- Linker Scripts
- Memory Optimization
- Undefined Behavior"""


def _build_round_1(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:
        opening_section = """1. Resume-Based Questions (3)

- Ask exactly 3 questions based on the candidate's resume.
- Focus on embedded projects, firmware development, microcontrollers, RTOS, communication protocols, debugging, optimizations, internships and achievements."""
        fundamentals_block = _FUNDAMENTALS_TOPICS
    else:
        opening_section = """1. Role-Specific Embedded Systems Questions (3)

Generate exactly 3 additional role-specific embedded systems questions because no resume is available."""
        fundamentals_block = _FUNDAMENTALS_TOPICS_NO_RESUME

    return f"""{header}

This is Round 1 of a multi-round Embedded Systems interview: Embedded C & Programming Fundamentals. Do NOT ask Microcontrollers/Protocols, RTOS/Debugging, or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 10 interview questions.

Interview Structure

{opening_section}

2. Embedded C & Programming Fundamentals (7)

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
- Cover different Embedded Systems competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


def _build_round_2(role: str, difficulty: str, resume_text: str | None, subrole: str) -> str:

    header = build_role_header(role, difficulty, resume_text)

    if resume_text:

        protocols_block = PROTOCOLS_BLOCK_BY_SUBROLE[subrole]
        rtos_block = RTOS_BLOCK_BY_SUBROLE[subrole]

        return f"""{header}

This is Round 2 of a multi-round Embedded Systems interview: Microcontrollers, Protocols & RTOS. Do NOT ask Embedded C/Programming Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 6 interview questions.

Interview Structure

1. Resume-Grounded Question (1)

- Ask exactly 1 question that builds on a microcontroller, protocol, or RTOS project mentioned in the candidate's resume.
- Ask the candidate to walk through how they approached, or would now approach, that situation.

2. Microcontrollers & Communication Protocols (2)

Generate exactly 2 questions.

Topics may include:

{protocols_block}

3. RTOS & Debugging (3)

Generate exactly 3 questions.

Topics include:

{rtos_block}

Adjust complexity according to the selected difficulty.

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 6 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Embedded Systems competencies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    protocols_block_no_resume = PROTOCOLS_BLOCK_BY_SUBROLE_NO_RESUME[subrole]
    rtos_block_no_resume = RTOS_BLOCK_BY_SUBROLE_NO_RESUME[subrole]

    return f"""{header}

This is Round 2 of a multi-round Embedded Systems interview: Microcontrollers, Protocols & RTOS. Do NOT ask Embedded C/Programming Fundamentals or Behavioral/HR questions in this round - those are separate rounds.

Generate EXACTLY 5 interview questions.

Interview Structure

1. Microcontrollers & Communication Protocols (2)

Generate exactly 2 questions.

Topics include:

{protocols_block_no_resume}

2. RTOS & Debugging (3)

Generate exactly 3 questions.

Topics include:

{rtos_block_no_resume}

{STYLE_GUIDELINES}

General Rules

- Generate EXACTLY 5 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Embedded Systems competencies.
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

This is Round 3 of a multi-round Embedded Systems interview: HR / Behavioral. Do NOT ask Embedded C/Programming Fundamentals, Microcontrollers/Protocols, or RTOS/Debugging questions in this round - those are separate rounds.

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


def build_embedded_systems_round_prompt(
    round_key: str,
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for one round of an Embedded Systems
    interview. round_key must be one of ROUND_KEYS (imported from
    software_rounds.py) - callers are expected to validate this
    before calling (see AIService.generate_questions).
    """

    subrole = classify_embedded_subrole(role)
    builder = _ROUND_BUILDERS[round_key]

    return builder(role, difficulty, resume_text, subrole)
