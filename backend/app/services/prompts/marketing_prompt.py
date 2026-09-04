"""
Marketing interview prompt builder.
"""

from app.services.role_classifier import classify_marketing_subrole


_FUNDAMENTALS_BY_SUBROLE = {
    "generic": """Easy
- Branding
- Marketing Mix (4Ps)
- SEO
- Consumer Behaviour
- Market Segmentation

Medium
- SEM
- Campaign Optimization
- Marketing Analytics
- Customer Journey
- Content Strategy

Hard
- Growth Marketing
- Attribution Models
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- Marketing Automation
- Performance Marketing
- Omnichannel Strategy""",
    "brand_management": """Easy
- Branding
- Brand Positioning
- Consumer Behaviour

Medium
- Brand Equity
- Brand Architecture
- Brand Tracking & Perception Studies

Hard
- Brand Portfolio Strategy
- Rebranding & Repositioning
- Long-term Brand Value Building""",
    "seo": """Easy
- SEO Basics
- Keyword Research
- On-page Optimization

Medium
- Technical SEO
- Link Building
- Search Algorithm Fundamentals

Hard
- Large-scale SEO Strategy
- Core Web Vitals & Technical Performance
- SEO for Competitive Markets""",
    "content_marketing": """Easy
- Content Basics
- Content Formats
- Editorial Planning

Medium
- Content Strategy
- Storytelling
- Content Distribution

Hard
- Content-led Growth
- SEO for Content
- Content Performance & ROI""",
    "product_marketing": """Easy
- Positioning Basics
- Messaging
- Market Basics

Medium
- Go-to-Market Strategy
- Competitive Analysis
- Sales Enablement

Hard
- Multi-product Positioning
- Launch Strategy at Scale
- Cross-functional GTM Leadership""",
}


def build_marketing_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Marketing interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_marketing_subrole(role)
    fundamentals_block = _FUNDAMENTALS_BY_SUBROLE[subrole]

    if resume_text:

        return f"""
You are an expert Marketing interviewer hiring for leading organizations such as Google, Amazon, Meta, Adobe, Unilever, Procter & Gamble, HubSpot and Salesforce.

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
- Focus on marketing campaigns, internships, projects, branding initiatives, leadership, certifications, measurable results and achievements.
- Use the resume extensively.

2. Marketing Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

Questions must strictly match the selected difficulty.

3. Campaign Case Studies (2)

Generate exactly 2 campaign-based case study questions.

Difficulty Guidelines:

Easy
- Basic campaign planning
- Product promotion
- Brand awareness

Medium
- Campaign optimization
- Budget allocation
- Performance improvement

Hard
- Multi-channel marketing strategy
- Growth experiments
- Data-driven campaign decisions
- Scaling marketing initiatives

4. Marketing Analytics Questions (2)

Generate exactly 2 role-specific marketing questions.

Examples include:

- Digital Marketing
- Brand Management
- Product Marketing
- Performance Marketing
- Growth Marketing
- SEO Specialist
- Content Marketing
- Marketing Analytics

Questions should evaluate practical marketing knowledge and decision-making.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a marketing analytics role, or a Python snippet for attribution/A-B-test analysis), you may generate one of the two Marketing Analytics Questions above as a coding question instead of a verbal one. Do NOT force this — most marketing roles should have zero coding questions, and that is the expected default.

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

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover different marketing competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required keyword(s) or concept name(s) directly (e.g. "SEO", "Attribution Models", "Customer Acquisition Cost") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Marketing Analytics Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""

    return f"""
You are an expert Marketing interviewer hiring for leading organizations such as Google, Amazon, Meta, Adobe, Unilever, Procter & Gamble, HubSpot and Salesforce.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Marketing Questions (2)

Generate exactly 2 additional role-specific marketing questions because no resume is available.

2. Marketing Fundamentals (3)

Generate exactly 3 questions.

Difficulty Guidelines:

{fundamentals_block}

3. Campaign Case Studies (2)

Generate exactly 2 campaign case-study questions.

Difficulty must match the selected level.

4. Marketing Analytics Questions (2)

Generate exactly 2 role-specific marketing analytics questions.

Optional Coding Question

If, and only if, the selected role would realistically involve writing or running a query, script, or formula-as-code in a real interview (for example, a SQL query for a marketing analytics role, or a Python snippet for attribution/A-B-test analysis), you may generate one of the two Marketing Analytics Questions above as a coding question instead of a verbal one. Do NOT force this — most marketing roles should have zero coding questions, and that is the expected default.

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

Vary the wording naturally throughout the interview.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different marketing competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required keyword(s) or concept name(s) directly (e.g. "SEO", "Attribution Models", "Customer Acquisition Cost") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.

If a Marketing Analytics Question was generated as a coding question, keep its `TYPE: CODING` line exactly as specified above; do not add this line to any other question.
"""


# Public re-export for marketing_rounds.py - added without touching
# any existing prompt text/structure above. Lets the round-based
# builders reuse the same per-sub-role fundamentals content without
# reaching into this module's underscore-prefixed name.
FUNDAMENTALS_BY_SUBROLE = _FUNDAMENTALS_BY_SUBROLE