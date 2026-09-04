"""
Digital Design interview prompt builder.
"""

from app.services.role_classifier import classify_digital_design_subrole


_COMPUTER_ARCHITECTURE_TOPICS = """Easy
- CPU Basics
- Memory Hierarchy
- Cache Basics
- Instruction Cycle

Medium
- Pipelining
- Hazards
- Cache Mapping
- Virtual Memory

Hard
- Branch Prediction
- Out-of-Order Execution
- Superscalar Architecture
- Cache Coherency
- Performance Trade-offs"""

_FPGA_TOPICS = """Easy
- FPGA Basics
- LUTs & CLBs
- I/O Blocks

Medium
- FPGA Timing Constraints
- Resource Utilization
- Clock Management (PLLs/MMCMs)

Hard
- FPGA Tool Flow (Synthesis/Place & Route)
- Partial Reconfiguration
- FPGA Power Optimization"""

# Resume branch: "Topics may include:" is followed directly by the
# tiered list.
_COMPUTER_ARCH_BLOCK_BY_SUBROLE = {
    "generic": _COMPUTER_ARCHITECTURE_TOPICS,
    "fpga": _FPGA_TOPICS,
}

# No-resume branch originally had no topic list at all for this
# section ("Difficulty must match the selected level." only) -
# preserved for "generic"; the fpga bucket adds a tiered list before
# that same closing line.
_COMPUTER_ARCH_TAIL_BY_SUBROLE = {
    "generic": "Difficulty must match the selected level.",
    "fpga": f"""Topics include:

{_FPGA_TOPICS}

Difficulty must match the selected level.""",
}

_RTL_VERIFICATION_TOPICS = """- Verilog
- SystemVerilog
- Blocking vs Non-blocking Assignments
- Synchronous vs Asynchronous Reset
- Testbench Basics
- Assertions
- Functional Verification
- Code Optimization
- Synthesizable RTL
- Linting Concepts"""

_RTL_VERIFICATION_TOPICS_NO_RESUME = """- Verilog
- SystemVerilog
- Blocking vs Non-blocking
- Reset Design
- Testbench
- Assertions
- Verification"""

_VERIFICATION_DV_TOPICS = """- UVM (Universal Verification Methodology)
- Testbench Architecture
- Functional Coverage
- SystemVerilog Assertions (SVA)
- Formal Verification
- Constrained Random Verification
- Scoreboard & Checkers
- Verification Planning"""

_RTL_VERIFICATION_BLOCK_BY_SUBROLE = {
    "generic": _RTL_VERIFICATION_TOPICS,
    "verification_dv": _VERIFICATION_DV_TOPICS,
}

_RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _RTL_VERIFICATION_TOPICS_NO_RESUME,
    "verification_dv": _VERIFICATION_DV_TOPICS,
}


def build_digital_design_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Digital Design interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_digital_design_subrole(role)
    computer_arch_block = _COMPUTER_ARCH_BLOCK_BY_SUBROLE.get(
        subrole, _COMPUTER_ARCHITECTURE_TOPICS
    )
    computer_arch_tail = _COMPUTER_ARCH_TAIL_BY_SUBROLE.get(
        subrole, _COMPUTER_ARCH_TAIL_BY_SUBROLE["generic"]
    )
    rtl_verification_block = _RTL_VERIFICATION_BLOCK_BY_SUBROLE.get(
        subrole, _RTL_VERIFICATION_TOPICS
    )
    rtl_verification_block_no_resume = _RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, _RTL_VERIFICATION_TOPICS_NO_RESUME
    )

    if resume_text:

        return f"""
You are an expert Digital Design interviewer hiring for leading semiconductor companies such as NVIDIA, AMD, Intel, Qualcomm, Apple, Samsung, Broadcom, Micron and Texas Instruments.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

Candidate Resume:
{resume_text}

Generate EXACTLY 10 interview questions.

Interview Structure

1. Resume-Based Questions (2)

- Ask exactly 2 questions based on the candidate's resume.
- Focus on internships, digital design projects, FPGA work, Verilog/SystemVerilog, RTL implementation, computer architecture, optimizations, debugging, leadership and achievements.

2. Digital Design Fundamentals (2)

Generate exactly 2 questions.

Difficulty Guidelines

Easy
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
- Synchronous Design Trade-offs

Questions must strictly match the selected difficulty.

3. Computer Architecture (2)

Generate exactly 2 questions.

Topics may include:

{computer_arch_block}

4. RTL Design & Verification (3)

Generate exactly 3 questions.

Topics include:

{rtl_verification_block}

Adjust complexity according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced Digital Design interviewer would speak.
- Use simple, easy-to-understand English while preserving all important digital design terminology and concepts.
- The difficulty should come from the engineering concepts being tested, not from complicated wording.
- Do NOT simplify the engineering concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, debugging approach, hardware design decisions and trade-offs.
- Questions should resemble real semiconductor interviews.

Avoid overly direct textbook-style questions such as:
- "Explain Setup Time."
- "Define FSM."
- "What is Verilog?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're designing..."
- "Imagine you're debugging..."
- "Can you walk me through..."
- "How would you approach..."
- "What do you think happens if..."
- "Have you worked with..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Digital Design competencies.
- Keep every question concise while still being conversational.
- Questions should resemble real interviews conducted at leading semiconductor companies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""
You are an expert Digital Design interviewer hiring for leading semiconductor companies such as NVIDIA, AMD, Intel, Qualcomm, Apple, Samsung, Broadcom, Micron and Texas Instruments.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Digital Design Questions (2)

Generate exactly 2 additional role-specific Digital Design questions because no resume is available.

2. Digital Design Fundamentals (2)

Generate exactly 2 questions.

Topics include:

Easy
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
- Timing Closure

3. Computer Architecture (2)

Generate exactly 2 questions.

{computer_arch_tail}

4. RTL Design & Verification (3)

Generate exactly 3 questions.

Topics include:

{rtl_verification_block_no_resume}

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving all important engineering terminology.
- The difficulty should come from the concepts being tested, not from complicated wording.
- Encourage reasoning and design thinking.
- Questions should resemble real semiconductor interviews.

Avoid textbook-style questions.

Use conversational openings such as:
- "Let's talk about..."
- "Suppose you're designing..."
- "Imagine you're debugging..."
- "Can you walk me through..."
- "How would you approach..."

Do NOT start every question with the same phrase.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Digital Design competencies.
- Keep questions concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""


# Public re-exports for digital_design_rounds.py - added without
# touching any existing prompt text/structure above. Lets the
# round-based builders reuse the same per-sub-role topic content
# without reaching into this module's underscore-prefixed names.
COMPUTER_ARCH_BLOCK_BY_SUBROLE = _COMPUTER_ARCH_BLOCK_BY_SUBROLE
COMPUTER_ARCH_TAIL_BY_SUBROLE = _COMPUTER_ARCH_TAIL_BY_SUBROLE
RTL_VERIFICATION_BLOCK_BY_SUBROLE = _RTL_VERIFICATION_BLOCK_BY_SUBROLE
RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME = _RTL_VERIFICATION_BLOCK_BY_SUBROLE_NO_RESUME
COMPUTER_ARCHITECTURE_TOPICS = _COMPUTER_ARCHITECTURE_TOPICS
RTL_VERIFICATION_TOPICS = _RTL_VERIFICATION_TOPICS
RTL_VERIFICATION_TOPICS_NO_RESUME = _RTL_VERIFICATION_TOPICS_NO_RESUME