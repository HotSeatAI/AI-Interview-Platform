"""
Shared boilerplate for VLSI interview prompts.

Extracted from vlsi_prompt.py so it can be reused by the round-based
builders in vlsi_rounds.py without duplicating the persona intro and
style-guideline text a second time (it's already duplicated once in
vlsi_prompt.py, between its resume/no-resume branches).

Unlike the business domains (finance/consulting/sales/marketing),
vlsi_prompt.py has no "optional coding" structured question block at
all - RTL/Verilog questions are asked conversationally, not in the
TYPE: CODING format - so there is no OPTIONAL_CODING_STRUCTURE or
CODING_QUESTION_STRUCTURE constant here. It also has no "Question
Length & Style" section, unlike every other domain's prompt.

vlsi_prompt.py itself is left untouched - nothing here changes its
behavior.
"""


STYLE_GUIDELINES = """Interview Style Guidelines

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

Vary the wording naturally throughout the interview."""


def build_role_header(role: str, difficulty: str, resume_text: str | None = None) -> str:
    """
    The "You are an expert VLSI interviewer..." persona intro plus
    Candidate Role / Interview Difficulty / Candidate Resume (or "has
    NOT provided a resume") preamble, shared by every round builder
    in vlsi_rounds.py.
    """

    resume_section = (
        f"Candidate Resume:\n{resume_text}"
        if resume_text
        else "The candidate has NOT provided a resume."
    )

    return f"""You are an expert VLSI interviewer hiring for leading semiconductor companies such as NVIDIA, AMD, Intel, Qualcomm, Apple, Broadcom, Samsung, Micron, Texas Instruments and MediaTek.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

{resume_section}"""
