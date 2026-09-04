"""
Shared boilerplate for Marketing interview prompts.

Extracted from marketing_prompt.py so it can be reused by the
round-based builders in marketing_rounds.py without duplicating the
persona intro, optional-coding structure, and style-guideline text
a second time (it's already duplicated once in marketing_prompt.py,
between its resume/no-resume branches).

marketing_prompt.py itself is left untouched - nothing here changes
its behavior.
"""


OPTIONAL_CODING_STRUCTURE = """Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a marketing analytics role, or a Python snippet for attribution/A-B-test analysis), you may generate one of the Marketing Analytics Questions above as a coding question instead of a verbal one. Do NOT force this - most marketing roles should have zero coding questions, and that is the expected default.

If you do include one, keep its number, then on its own line write exactly `TYPE: CODING`, then immediately continue with EXACTLY the following structure:

Problem Statement

<Clearly describe the problem that the candidate has to solve.>

Input Format

<Describe the expected input format.>

Output Format

<Describe the expected output format.>

Constraints

<List the constraints applicable to the problem.>

Example 1

Input

<Sample Input>

Output

<Expected Output>

Example 2

Input

<Sample Input>

Output

<Expected Output>

Example 3

Input

<Sample Input>

Output

<Expected Output>

Rules:
- Generate exactly three examples.
- Examples must be valid.
- Do NOT provide the solution, hints, or an explanation of the approach.
- Never add a `TYPE: CODING` line to a question that is only meant to be explained verbally."""


STYLE_GUIDELINES = """Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced marketing interviewer would speak.
- Use simple, easy-to-understand English while preserving all important marketing terminology and concepts.
- The difficulty should come from the marketing concept or business problem being tested, not from complicated wording.
- Do NOT simplify the marketing concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, decision-making process and practical marketing approach.
- Questions should feel like a genuine conversation during a real marketing interview.

Avoid overly direct textbook-style questions such as:
- "Explain SEO."
- "Define Branding."
- "What is Customer Journey?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're launching..."
- "Imagine you're responsible for..."
- "Can you walk me through..."
- "How would you approach..."
- "What would you do if..."
- "Have you worked on..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview."""


QUESTION_LENGTH_STYLE = """Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required keyword(s) or concept name(s) directly (e.g. "SEO", "Attribution Models", "Customer Acquisition Cost") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above."""


def build_role_header(role: str, difficulty: str, resume_text: str | None = None) -> str:
    """
    The "You are an expert Marketing interviewer..." persona intro
    plus Candidate Role / Interview Difficulty / Candidate Resume (or
    "has NOT provided a resume") preamble, shared by every round
    builder in marketing_rounds.py.
    """

    resume_section = (
        f"Candidate Resume:\n{resume_text}"
        if resume_text
        else "The candidate has NOT provided a resume."
    )

    return f"""You are an expert Marketing interviewer hiring for leading organizations such as Google, Amazon, Meta, Adobe, Unilever, Procter & Gamble, HubSpot and Salesforce.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

{resume_section}"""
