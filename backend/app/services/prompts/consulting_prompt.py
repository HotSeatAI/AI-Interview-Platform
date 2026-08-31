"""
Consulting interview prompt builder.
"""

from app.services.role_classifier import classify_consulting_subrole


_FUNDAMENTALS_BY_SUBROLE = {
    "generic": """Easy
- SWOT Analysis
- Porter's Five Forces
- PESTLE Analysis

Medium
- Market Entry Strategy
- Profitability Framework
- Growth Strategy

Hard
- M&A Strategy
- Corporate Transformation
- Organizational Strategy
- Competitive Strategy
- Business Transformation""",
    "operations_consulting": """Easy
- Process Mapping
- Basic Supply Chain Concepts
- Cost Structures

Medium
- Lean & Six Sigma
- Process Optimization
- Inventory Management

Hard
- Supply Chain Redesign
- Operational Transformation
- Cost Reduction at Scale""",
    "digital_consulting": """Easy
- Digital Basics
- Technology Landscape
- Basic IT Systems

Medium
- Digital Transformation Strategy
- Cloud Strategy
- Data & Analytics Strategy

Hard
- Enterprise Technology Transformation
- Change Management for Digital Initiatives
- Platform & Ecosystem Strategy""",
}


def build_consulting_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Consulting interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_consulting_subrole(role)
    fundamentals_block = _FUNDAMENTALS_BY_SUBROLE[subrole]

    if resume_text:

        return f"""
You are an expert Management Consulting interviewer hiring for leading consulting firms such as McKinsey & Company, Boston Consulting Group (BCG), Bain & Company, Accenture Strategy, Deloitte Consulting, EY-Parthenon, Kearney and Oliver Wyman.

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
- Focus on internships, leadership experiences, business projects, achievements, problem-solving experience, impact created and decision making.

2. Consulting Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must match the selected difficulty.

3. Business Case Studies (2)

Generate exactly 2 consulting case interview questions.

Difficulty Guidelines:

Easy
- Simple business scenarios

Medium
- Structured business case interviews

Hard
- Multi-step strategic consulting cases involving analysis and recommendations

4. Business Analysis Questions (2)

Generate exactly 2 business analysis questions related to the selected consulting role.

Examples include:

- Strategy Consulting
- Operations Consulting
- Business Consulting
- Advisory
- Management Consulting
- Digital Consulting

Match the selected difficulty.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a business/data analyst role, or an Excel/Python data-manipulation task), you may generate one of the two Business Analysis Questions above as a coding question instead of a verbal one. Do NOT force this — most consulting roles should have zero coding questions, and that is the expected default.

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
- Never add a `TYPE: CODING` line to a question that is only meant to be explained verbally.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

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

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different consulting competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required framework or concept name(s) directly (e.g. "SWOT Analysis", "Porter's Five Forces", "Market Entry Strategy") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Business Analysis Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""

    return f"""
You are an expert Management Consulting interviewer hiring for leading consulting firms such as McKinsey & Company, Boston Consulting Group (BCG), Bain & Company, Accenture Strategy, Deloitte Consulting, EY-Parthenon, Kearney and Oliver Wyman.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Consulting Questions (2)

Generate exactly 2 consulting role-specific questions since no resume is available.

2. Consulting Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

3. Business Case Studies (2)

Generate exactly 2 consulting case interview questions.

Difficulty must match the selected level.

4. Business Analysis Questions (2)

Generate exactly 2 consulting role-specific analytical questions.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a business/data analyst role, or an Excel/Python data-manipulation task), you may generate one of the two Business Analysis Questions above as a coding question instead of a verbal one. Do NOT force this — most consulting roles should have zero coding questions, and that is the expected default.

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
- Never add a `TYPE: CODING` line to a question that is only meant to be explained verbally.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

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

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different consulting competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required framework or concept name(s) directly (e.g. "SWOT Analysis", "Porter's Five Forces", "Market Entry Strategy") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Business Analysis Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""