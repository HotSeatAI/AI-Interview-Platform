"""
VLSI interview prompt builder.
"""

from app.services.role_classifier import classify_vlsi_subrole


_STA_CONCEPTS_BY_SUBROLE = {
    "generic": """- Setup Time
- Hold Time
- Clock Skew
- Clock Jitter
- Timing Paths
- STA
- DRC
- LVS
- Power Optimization
- Multi-Corner Multi-Mode (MCMM)
- Process Variations""",
    "physical_design": """- Floorplanning Strategies
- Placement & Routing Trade-offs
- Clock Tree Synthesis (CTS)
- Timing Closure
- IR Drop & EM Analysis
- Physical Verification (DRC/LVS)""",
    "dft": """- Scan Insertion
- ATPG (Automatic Test Pattern Generation)
- Test Compression
- Built-In Self-Test (BIST)
- Boundary Scan (JTAG)
- Fault Coverage""",
    "sta_timing": """- Setup & Hold Time Analysis
- Clock Skew & Jitter
- Timing Paths & Exceptions
- Multi-Corner Multi-Mode (MCMM) Analysis
- Timing Closure Techniques
- Statistical Static Timing Analysis (SSTA)""",
}

# No-resume branch originally used a shorter "generic" topic list than
# the resume branch - preserved here so that fallback stays byte-
# identical to before for unmatched roles. New buckets reuse the same
# tailored content as the resume branch.
_STA_CONCEPTS_BY_SUBROLE_NO_RESUME = {
    **_STA_CONCEPTS_BY_SUBROLE,
    "generic": """- STA
- Setup/Hold
- Clock Skew
- Timing Closure
- DRC
- LVS
- MCMM
- Power Optimization""",
}


def build_vlsi_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for VLSI interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_vlsi_subrole(role)
    sta_concepts_block = _STA_CONCEPTS_BY_SUBROLE[subrole]
    sta_concepts_block_no_resume = _STA_CONCEPTS_BY_SUBROLE_NO_RESUME[subrole]

    if resume_text:

        return f"""
You are an expert VLSI interviewer hiring for leading semiconductor companies such as NVIDIA, AMD, Intel, Qualcomm, Apple, Broadcom, Samsung, Micron, Texas Instruments and MediaTek.

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
- Focus on RTL design, ASIC projects, FPGA work, physical design, verification, synthesis, timing analysis, internships, optimizations and achievements.

2. RTL & Digital Design (2)

Generate exactly 2 questions.

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

3. ASIC Design Flow & Physical Design (2)

Generate exactly 2 questions.

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
- Physical Verification

4. Static Timing Analysis & VLSI Concepts (3)

Generate exactly 3 questions.

Topics include:

{sta_concepts_block}

Adjust complexity according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced VLSI interviewer would speak.
- Use simple, easy-to-understand English while preserving all important VLSI terminology.
- The difficulty should come from the engineering concepts being tested, not from complicated wording.
- Do NOT simplify the engineering concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, implementation decisions and design trade-offs.
- Questions should resemble real VLSI interviews.

Avoid overly direct textbook-style questions such as:

- "Explain STA."
- "Define CTS."
- "What is Floorplanning?"

Instead, naturally introduce topics using a variety of conversational styles such as:

- "Let's talk about..."
- "Suppose you're implementing..."
- "Imagine you're closing timing..."
- "Can you walk me through..."
- "How would you approach..."
- "What do you think would happen if..."
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
- Cover different VLSI competencies.
- Keep every question concise while still being conversational.
- Questions should resemble real interviews conducted at leading semiconductor companies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""
You are an expert VLSI interviewer hiring for leading semiconductor companies such as NVIDIA, AMD, Intel, Qualcomm, Apple, Broadcom, Samsung, Micron, Texas Instruments and MediaTek.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific VLSI Questions (2)

Generate exactly 2 additional VLSI role-specific questions because no resume is available.

2. RTL & Digital Design (2)

Generate exactly 2 questions.

Topics include:

Easy

- Verilog
- FSM
- Registers

Medium

- SystemVerilog
- RTL Optimization
- Reset Design

Hard

- CDC
- Low Power RTL
- Clock Domain Design

3. ASIC Design Flow & Physical Design (2)

Generate exactly 2 questions.

Topics include:

- Synthesis
- Floorplanning
- Placement
- CTS
- Routing

4. Static Timing Analysis & VLSI Concepts (3)

Generate exactly 3 questions.

Topics include:

{sta_concepts_block_no_resume}

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving all important VLSI terminology.
- The difficulty should come from the concepts being tested, not from complicated wording.
- Encourage reasoning, implementation thinking and design trade-offs.
- Questions should resemble real VLSI interviews.

Avoid textbook-style questions.

Use conversational openings such as:

- "Let's talk about..."
- "Suppose you're implementing..."
- "Imagine you're closing timing..."
- "Can you walk me through..."
- "How would you approach..."

Do NOT start every question with the same phrase.

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


# Public re-exports for vlsi_rounds.py - added without touching any
# existing prompt text/structure above. Lets the round-based builders
# reuse the same per-sub-role STA/VLSI concepts content without
# reaching into this module's underscore-prefixed names.
STA_CONCEPTS_BY_SUBROLE = _STA_CONCEPTS_BY_SUBROLE
STA_CONCEPTS_BY_SUBROLE_NO_RESUME = _STA_CONCEPTS_BY_SUBROLE_NO_RESUME