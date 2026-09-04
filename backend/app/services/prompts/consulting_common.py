"""
Shared boilerplate for Consulting interview prompts.

Extracted from consulting_prompt.py so it can be reused by the
round-based builders in consulting_rounds.py without duplicating the
persona intro, optional-coding structure, and style-guideline text
a second time (it's already duplicated once in consulting_prompt.py,
between its resume/no-resume branches).

consulting_prompt.py itself is left untouched - nothing here changes
its behavior.
"""


OPTIONAL_CODING_STRUCTURE = """Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a business/data analyst role, or an Excel/Python data-manipulation task), you may generate one of the Business Analysis Questions above as a coding question instead of a verbal one. Do NOT force this - most consulting roles should have zero coding questions, and that is the expected default.

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

- Ask every question in a natural, conversational and professional manner, similar to how an experienced consulting interviewer would speak.
- Use simple, easy-to-understand English while preserving all important consulting terminology, frameworks and business concepts.
- The difficulty should come from the business problem and analytical thinking being tested, not from complicated wording.
- Do NOT simplify the consulting concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, structured thinking, assumptions and decision-making process.
- Questions should feel like a genuine consulting interview rather than an academic examination.

Avoid overly direct textbook-style questions such as:
- "Explain SWOT Analysis."
- "Define Porter's Five Forces."
- "What is Market Entry Strategy?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose a client approaches you..."
- "Imagine you're advising..."
- "Can you walk me through..."
- "How would you approach..."
- "What factors would you consider..."
- "A client is facing..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview."""


QUESTION_LENGTH_STYLE = """Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required framework or concept name(s) directly (e.g. "SWOT Analysis", "Porter's Five Forces", "Market Entry Strategy") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above."""


def build_role_header(role: str, difficulty: str, resume_text: str | None = None) -> str:
    """
    The "You are an expert Management Consulting interviewer..."
    persona intro plus Candidate Role / Interview Difficulty /
    Candidate Resume (or "has NOT provided a resume") preamble,
    shared by every round builder in consulting_rounds.py.
    """

    resume_section = (
        f"Candidate Resume:\n{resume_text}"
        if resume_text
        else "The candidate has NOT provided a resume."
    )

    return f"""You are an expert Management Consulting interviewer hiring for leading consulting firms such as McKinsey & Company, Boston Consulting Group (BCG), Bain & Company, Accenture Strategy, Deloitte Consulting, EY-Parthenon, Kearney and Oliver Wyman.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

{resume_section}"""
