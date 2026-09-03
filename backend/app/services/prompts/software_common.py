"""
Shared boilerplate for Software Engineering interview prompts.

Extracted from software_prompt.py so it can be reused by the
round-based builders in software_rounds.py without duplicating the
persona intro, coding-question structure, and style-guideline text
a second time (it's already duplicated once in software_prompt.py,
between its resume/no-resume branches).

software_prompt.py itself is left untouched - nothing here changes
its behavior.
"""


CODING_QUESTION_STRUCTURE = """For EVERY coding question, keep the question number, then on its own line write exactly:

TYPE: CODING

Then immediately continue with EXACTLY the following structure.

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
- Include at least one edge-case example whenever appropriate.
- Do NOT provide the solution.
- Do NOT provide hints.
- Do NOT explain the algorithm.
- Do NOT include time complexity or space complexity.
- Do NOT include any text before or after the required structure."""


STYLE_GUIDELINES = """Interview Style Guidelines:

- Ask every question in a natural, conversational and professional manner, similar to how an experienced interviewer at a top technology company would speak.
- Use simple, easy-to-understand English while preserving all important technical terms and concepts.
- The difficulty should come from the technical concept being tested, not from complicated wording.
- Do NOT simplify the technical concepts. Only simplify the language used to ask the question.
- Questions should encourage the candidate to explain their reasoning rather than simply recall definitions.
- Questions should resemble a real one-to-one interview conversation.

Avoid overly direct textbook-style questions such as:
- "Explain X."
- "Define Y."
- "What is Z?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're working on..."
- "Imagine you're designing..."
- "Can you walk me through..."
- "How would you approach..."
- "What do you think happens when..."
- "Have you worked with..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview."""


QUESTION_LENGTH_STYLE = """Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required technical keyword(s) or concept name(s) directly (e.g. "API", "DBMS", "Consistent Hashing", "CAP Theorem") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above."""


def build_role_header(role: str, difficulty: str, resume_text: str | None = None) -> str:
    """
    The "You are an expert Software Engineering interviewer..." persona
    intro plus Candidate Role / Interview Difficulty / Candidate Resume
    (or "has NOT provided a resume") preamble, shared by every round
    builder in software_rounds.py.
    """

    resume_section = (
        f"Candidate Resume:\n{resume_text}"
        if resume_text
        else "The candidate has NOT provided a resume."
    )

    return f"""You are an expert Software Engineering interviewer at top product-based companies like Google, Amazon, Microsoft, Meta, Apple, Netflix and Uber.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

{resume_section}"""
