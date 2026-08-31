"""
Finance interview prompt builder.
"""

from app.services.role_classifier import classify_finance_subrole


_FUNDAMENTALS_BY_SUBROLE = {
    "generic": """Easy
- Accounting
- Financial Statements
- Ratio Analysis

Medium
- DCF
- Valuation
- CAPM
- NPV
- IRR

Hard
- Derivatives
- Portfolio Theory
- Financial Modeling
- Advanced Valuation
- Risk Management""",
    "investment_banking_pe": """Easy
- Accounting
- Financial Statements
- Enterprise vs Equity Value

Medium
- DCF
- Comparable Company Analysis
- Precedent Transactions

Hard
- LBO Modeling
- Deal Structuring
- Synergies & Accretion/Dilution""",
    "equity_research": """Easy
- Financial Statements
- Ratio Analysis
- Industry Basics

Medium
- DCF
- Comparable Company Analysis
- Earnings Models

Hard
- Advanced Valuation
- Portfolio Theory
- CAPM""",
    "corporate_finance_treasury": """Easy
- Accounting
- Financial Statements
- Working Capital Basics

Medium
- Capital Budgeting
- Cost of Capital
- Cash Flow Forecasting

Hard
- Capital Structure Decisions
- Liquidity & Cash Management
- Financial Risk Hedging""",
    "risk_management": """Easy
- Risk Types (Market/Credit/Operational)
- Financial Statements
- Basic Ratio Analysis

Medium
- Value at Risk (VaR)
- Hedging Strategies
- Credit Risk Assessment

Hard
- Derivatives
- Stress Testing
- Regulatory Capital (Basel)""",
    "venture_capital": """Easy
- Startup Basics
- Cap Tables
- Financial Statements

Medium
- Startup Valuation Methods (VC Method)
- Market Sizing (TAM/SAM/SOM)
- Term Sheets

Hard
- Due Diligence for Early-Stage Deals
- Follow-on Investment Strategy
- Exit Strategies""",
}


def build_finance_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Finance interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_finance_subrole(role)
    fundamentals_block = _FUNDAMENTALS_BY_SUBROLE[subrole]

    if resume_text:

        return f"""
You are an expert Finance interviewer hiring for leading organizations such as Goldman Sachs, JPMorgan Chase, Morgan Stanley, BlackRock, KPMG, Deloitte, EY and PwC.

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

- Ask exactly 2 questions from the candidate's resume.
- Focus on internships, financial projects, certifications, investment experience, accounting knowledge, leadership and achievements.

2. Finance Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must match the selected difficulty.

3. Finance Case Studies (2)

Generate exactly 2 real interview case-study questions.

Difficulty Guidelines:

Easy
- Simple business situations

Medium
- Financial analysis and investment decisions

Hard
- Multi-step valuation, risk analysis and strategic financial decisions

4. Role-Specific Technical Questions (2)

Generate exactly 2 questions specifically related to the selected role.

Examples include:

- Investment Banking
- Equity Research
- Corporate Finance
- Risk Management
- Financial Analyst
- Treasury
- Asset Management
- Private Equity
- Venture Capital

Match the difficulty.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a data or financial analyst role, or a Python/R snippet for a quantitative finance role), you may generate one of the two Role-Specific Technical Questions above as a coding question instead of a verbal one. Do NOT force this — most finance roles should have zero coding questions, and that is the expected default.

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

- Ask every question in a natural, conversational and professional manner, similar to how an experienced finance interviewer would speak.
- Use simple, easy-to-understand English while preserving all important finance terminology and concepts.
- The difficulty should come from the financial concept, analysis or business problem being tested, not from complicated wording.
- Do NOT simplify the finance concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, analytical thinking and financial decision-making process.
- Questions should feel like a genuine conversation during a real finance interview.

Avoid overly direct textbook-style questions such as:
- "Explain DCF."
- "Define CAPM."
- "What is NPV?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're analyzing..."
- "Imagine you're evaluating..."
- "Can you walk me through..."
- "How would you approach..."
- "What factors would you consider..."
- "Have you worked on..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different finance competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required technical keyword(s) or concept name(s) directly (e.g. "DCF", "CAPM", "Working Capital") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Role-Specific Technical Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""

    return f"""
You are an expert Finance interviewer hiring for leading organizations such as Goldman Sachs, JPMorgan Chase, Morgan Stanley, BlackRock, KPMG, Deloitte, EY and PwC.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Questions (2)

Generate exactly 2 additional finance role-specific questions because no resume is available.

2. Finance Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

3. Finance Case Studies (2)

Generate exactly 2 case-study questions.

Difficulty must match the selected level.

4. Role-Specific Technical Questions (2)

Generate exactly 2 questions related to the selected finance role.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a data or financial analyst role, or a Python/R snippet for a quantitative finance role), you may generate one of the two Role-Specific Technical Questions above as a coding question instead of a verbal one. Do NOT force this — most finance roles should have zero coding questions, and that is the expected default.

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

- Ask every question in a natural, conversational and professional manner, similar to how an experienced finance interviewer would speak.
- Use simple, easy-to-understand English while preserving all important finance terminology and concepts.
- The difficulty should come from the financial concept, analysis or business problem being tested, not from complicated wording.
- Do NOT simplify the finance concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, analytical thinking and financial decision-making process.
- Questions should feel like a genuine conversation during a real finance interview.

Avoid overly direct textbook-style questions such as:
- "Explain DCF."
- "Define CAPM."
- "What is NPV?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're analyzing..."
- "Imagine you're evaluating..."
- "Can you walk me through..."
- "How would you approach..."
- "What factors would you consider..."
- "Have you worked on..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different finance competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required technical keyword(s) or concept name(s) directly (e.g. "DCF", "CAPM", "Working Capital") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Role-Specific Technical Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""