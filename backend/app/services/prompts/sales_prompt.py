"""
Sales interview prompt builder.
"""

from app.services.role_classifier import classify_sales_subrole


_FUNDAMENTALS_BY_SUBROLE = {
    "generic": """Easy
- Sales Funnel
- CRM
- Lead Generation

Medium
- Negotiation
- Prospecting
- Pipeline Management

Hard
- Enterprise Sales
- Sales Forecasting
- Strategic Selling
- Key Account Management
- Sales Metrics""",
    "customer_success": """Easy
- Customer Onboarding
- Customer Health Scores
- Basic Account Management

Medium
- Renewals
- Upsell & Cross-sell
- Churn Prevention

Hard
- Strategic Account Growth
- Enterprise Renewal Negotiations
- Customer Advocacy Programs""",
}


def build_sales_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Sales interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy /Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_sales_subrole(role)
    fundamentals_block = _FUNDAMENTALS_BY_SUBROLE[subrole]

    if resume_text:

        return f"""
You are an expert Sales interviewer hiring for leading organizations such as Salesforce, Oracle, HubSpot, Microsoft, Amazon, Adobe, SAP and Cisco.

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
- Focus on sales experience, internships, achievements, targets, client handling, negotiations, leadership and measurable business impact.

2. Sales Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must strictly match the selected difficulty.

3. Customer Scenarios (2)

Generate exactly 2 customer-based scenario questions.

Difficulty Guidelines:

Easy
- Basic customer interactions

Medium
- Handling objections
- Closing deals
- Customer negotiations

Hard
- Enterprise customer scenarios
- Strategic negotiations
- Multi-stakeholder selling

4. Sales Strategy Questions (2)

Generate exactly 2 questions specific to the selected sales role.

Examples include:

- Business Development
- Account Executive
- Account Manager
- Customer Success
- Relationship Manager
- Inside Sales
- Enterprise Sales

Questions should assess practical sales thinking.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a sales/revenue operations or sales analytics role), you may generate one of the two Sales Strategy Questions above as a coding question instead of a verbal one. Do NOT force this — most sales roles should have zero coding questions, and that is the expected default.

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

- Ask every question in a natural, conversational and professional manner, similar to how an experienced interviewer would speak.
- Use simple, easy-to-understand English while preserving all important sales terminology and concepts.
- The difficulty should come from the business scenario or sales concept being tested, not from complicated wording.
- Do NOT simplify the business concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, decision-making process and practical approach.
- Questions should feel like a genuine conversation during a real sales interview.

Avoid overly direct textbook-style questions such as:
- "Explain CRM."
- "Define Lead Generation."
- "What is Enterprise Sales?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're meeting..."
- "Imagine you're handling..."
- "Can you walk me through..."
- "How would you approach..."
- "What would you do if..."
- "Have you experienced..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different sales competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required keyword(s) or concept name(s) directly (e.g. "CRM", "Pipeline Management", "Enterprise Sales") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Sales Strategy Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""

    return f"""
You are an expert Sales interviewer hiring for leading organizations such as Salesforce, Oracle, HubSpot, Microsoft, Amazon, Adobe, SAP and Cisco.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Sales Questions (2)

Generate exactly 2 additional role-specific sales questions because no resume is available.

2. Sales Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

3. Customer Scenarios (2)

Generate exactly 2 customer scenario questions.

Difficulty must match the selected level.

4. Sales Strategy Questions (2)

Generate exactly 2 role-specific sales strategy questions.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a sales/revenue operations or sales analytics role), you may generate one of the two Sales Strategy Questions above as a coding question instead of a verbal one. Do NOT force this — most sales roles should have zero coding questions, and that is the expected default.

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

- Ask every question in a natural, conversational and professional manner, similar to how an experienced interviewer would speak.
- Use simple, easy-to-understand English while preserving all important sales terminology and concepts.
- The difficulty should come from the business scenario or sales concept being tested, not from complicated wording.
- Do NOT simplify the business concepts. Only simplify the language used to ask the question.
- Encourage candidates to explain their reasoning, decision-making process and practical approach.
- Questions should feel like a genuine conversation during a real sales interview.

Avoid overly direct textbook-style questions such as:
- "Explain CRM."
- "Define Lead Generation."
- "What is Enterprise Sales?"

Instead, naturally introduce topics using a variety of conversational styles such as:
- "Let's talk about..."
- "Suppose you're meeting..."
- "Imagine you're handling..."
- "Can you walk me through..."
- "How would you approach..."
- "What would you do if..."
- "Have you experienced..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different sales competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required keyword(s) or concept name(s) directly (e.g. "CRM", "Pipeline Management", "Enterprise Sales") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Sales Strategy Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


# Public re-export for sales_rounds.py - added without touching any
# existing prompt text/structure above. Lets the round-based builders
# reuse the same per-sub-role fundamentals content without reaching
# into this module's underscore-prefixed name.
FUNDAMENTALS_BY_SUBROLE = _FUNDAMENTALS_BY_SUBROLE