"""
Analog Design interview prompt builder.
"""

from app.services.role_classifier import classify_analog_subrole


_IC_DESIGN_CONCEPTS_BY_SUBROLE = {
    "generic": """- ADC
- DAC
- PLL
- Bandgap Reference
- LDO
- Voltage Regulators
- Comparators
- Oscillators
- Sample and Hold Circuits
- Switched Capacitor Circuits""",
    "mixed_signal": """- ADC Architectures (SAR/Pipeline/Delta-Sigma)
- DAC Architectures
- Data Converter Specifications (SNR/ENOB/SFDR)
- Digital-Analog Interfacing
- Clock & Timing Generation for Mixed-Signal Systems
- Sampling & Aliasing""",
}

_IC_DESIGN_CONCEPTS_BY_SUBROLE_NO_RESUME = {
    "generic": """- ADC
- DAC
- PLL
- LDO
- Bandgap Reference
- Comparators
- Oscillators""",
    "mixed_signal": _IC_DESIGN_CONCEPTS_BY_SUBROLE["mixed_signal"],
}


def build_analog_design_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Analog Design interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium /Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_analog_subrole(role)
    ic_design_block = _IC_DESIGN_CONCEPTS_BY_SUBROLE[subrole]
    ic_design_block_no_resume = _IC_DESIGN_CONCEPTS_BY_SUBROLE_NO_RESUME[subrole]

    if resume_text:

        return f"""
You are an expert Analog Design interviewer hiring for leading semiconductor companies such as Texas Instruments, Analog Devices, Qualcomm, Intel, Apple, Infineon, Samsung, NXP and STMicroelectronics.

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
- Focus on analog circuit projects, internships, PCB design, analog IC design, simulations, debugging, optimizations, research work and achievements.

2. Analog Electronics Fundamentals (2)

Generate exactly 2 questions.

Difficulty Guidelines

Easy

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
- High-Speed Analog Circuits

Questions must strictly match the selected difficulty.

3. Circuit Analysis & Design (2)

Generate exactly 2 questions.

Topics include:

Easy

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
- Precision Circuits

4. Analog IC Design Concepts (3)

Generate exactly 3 questions.

Topics include:

{ic_design_block}

Adjust complexity according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced Analog Design interviewer would speak.
- Use simple, easy-to-understand English while preserving all important analog electronics terminology.
- The difficulty should come from the engineering concepts being tested, not from complicated wording.
- Do NOT simplify the engineering concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain circuit behavior, design decisions, assumptions and trade-offs.
- Questions should resemble real analog design interviews.

Avoid overly direct textbook-style questions such as:

- "Explain MOSFET."
- "Define Current Mirror."
- "What is an Op-Amp?"

Instead, naturally introduce topics using a variety of conversational styles such as:

- "Let's talk about..."
- "Suppose you're designing..."
- "Imagine you're debugging..."
- "Can you walk me through..."
- "How would you approach..."
- "What would happen if..."
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
- Cover different Analog Design competencies.
- Keep every question concise while still being conversational.
- Questions should resemble real interviews conducted at leading semiconductor companies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""
You are an expert Analog Design interviewer hiring for leading semiconductor companies such as Texas Instruments, Analog Devices, Qualcomm, Intel, Apple, Infineon, Samsung, NXP and STMicroelectronics.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Analog Design Questions (2)

Generate exactly 2 additional role-specific analog design questions because no resume is available.

2. Analog Electronics Fundamentals (2)

Generate exactly 2 questions.

Topics include:

Easy

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
- Noise Analysis

3. Circuit Analysis & Design (2)

Generate exactly 2 questions.

Topics include:

- Biasing
- Gain
- Active Filters
- Oscillators
- Feedback

4. Analog IC Design Concepts (3)

Generate exactly 3 questions.

Topics include:

{ic_design_block_no_resume}

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving all important analog electronics terminology.
- The difficulty should come from the concepts being tested, not from complicated wording.
- Encourage reasoning, circuit analysis and practical engineering thinking.
- Questions should resemble real analog design interviews.

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
- Cover different Analog Design competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions,markdown, bullet points or any text before or after the questions.
"""