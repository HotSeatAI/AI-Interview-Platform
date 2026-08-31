"""
Product Management interview prompt builder.
"""

from app.services.role_classifier import classify_product_management_subrole


_PRODUCT_SENSE_TOPICS = """Easy

- User Personas
- MVP
- Product Lifecycle
- User Research
- Feature Ideas

Medium

- Product Design
- Feature Prioritization
- User Experience
- Customer Journey
- Product Roadmaps

Hard

- Platform Strategy
- Marketplace Products
- Ecosystem Design
- Product Trade-offs
- Long-term Vision"""

_PRODUCT_SENSE_TOPICS_NO_RESUME = """Easy

- User Personas
- MVP
- Product Lifecycle

Medium

- Product Design
- Feature Prioritization
- Product Roadmaps

Hard

- Platform Strategy
- Product Trade-offs
- Ecosystem Design"""

_TECHNICAL_PM_TOPICS = """Easy

- Technical Basics for PMs
- APIs 101
- System Components Overview

Medium

- System Architecture Trade-offs
- API Design as Product
- Technical Feasibility Assessment

Hard

- Engineering Collaboration at Scale
- Technical Debt vs Feature Trade-offs
- Platform & Infrastructure Decisions"""

_PRODUCT_SENSE_BLOCK_BY_SUBROLE = {
    "generic": _PRODUCT_SENSE_TOPICS,
    "technical_pm": _TECHNICAL_PM_TOPICS,
}

_PRODUCT_SENSE_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _PRODUCT_SENSE_TOPICS_NO_RESUME,
    "technical_pm": _TECHNICAL_PM_TOPICS,
}

_PRODUCT_STRATEGY_TOPICS = """Easy

- Business Goals
- Product Vision

Medium

- Market Entry
- Growth Strategy
- Competitive Analysis
- Monetization

Hard

- Pricing Strategy
- Network Effects
- Platform Economics
- Go-to-Market Strategy
- Business Trade-offs"""

_PRODUCT_STRATEGY_TOPICS_NO_RESUME = """- Growth Strategy
- Monetization
- Competitive Analysis
- Pricing
- Go-to-Market Strategy"""

_GROWTH_PM_TOPICS = """Easy

- Growth Basics
- User Acquisition Channels

Medium

- AARRR Framework (Pirate Metrics)
- Growth Loops
- Referral & Virality Mechanics

Hard

- Growth Experimentation at Scale
- Retention & Engagement Levers
- Compounding Growth Strategy"""

_PRODUCT_STRATEGY_BLOCK_BY_SUBROLE = {
    "generic": _PRODUCT_STRATEGY_TOPICS,
    "growth_pm": _GROWTH_PM_TOPICS,
}

_PRODUCT_STRATEGY_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _PRODUCT_STRATEGY_TOPICS_NO_RESUME,
    "growth_pm": _GROWTH_PM_TOPICS,
}

_PRODUCT_ANALYTICS_TOPICS = """- North Star Metrics
- DAU / MAU
- Funnel Analysis
- Retention
- Churn
- A/B Testing
- Feature Success Metrics
- Prioritization Frameworks
- Product Execution
- Stakeholder Management
- Cross-functional Collaboration"""

_PRODUCT_ANALYTICS_TOPICS_NO_RESUME = """- Product Metrics
- Funnel Analysis
- A/B Testing
- Retention
- Churn
- Prioritization
- Product Execution
- Stakeholder Management"""

_PRODUCT_ANALYST_TOPICS = """- Metrics Design & North Star Frameworks
- Cohort Analysis
- Funnel Analysis
- Experimentation Design (A/B Testing Rigor)
- Data-Informed Prioritization
- Statistical Significance in Product Experiments"""

_PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE = {
    "generic": _PRODUCT_ANALYTICS_TOPICS,
    "product_analyst": _PRODUCT_ANALYST_TOPICS,
}

_PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE_NO_RESUME = {
    "generic": _PRODUCT_ANALYTICS_TOPICS_NO_RESUME,
    "product_analyst": _PRODUCT_ANALYST_TOPICS,
}


def build_product_management_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Builds the Gemini prompt for Product Management interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Prompt string for Gemini.
    """

    subrole = classify_product_management_subrole(role)
    product_sense_block = _PRODUCT_SENSE_BLOCK_BY_SUBROLE.get(subrole, _PRODUCT_SENSE_TOPICS)
    product_sense_block_no_resume = _PRODUCT_SENSE_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, _PRODUCT_SENSE_TOPICS_NO_RESUME
    )
    product_strategy_block = _PRODUCT_STRATEGY_BLOCK_BY_SUBROLE.get(subrole, _PRODUCT_STRATEGY_TOPICS)
    product_strategy_block_no_resume = _PRODUCT_STRATEGY_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, _PRODUCT_STRATEGY_TOPICS_NO_RESUME
    )
    product_analytics_block = _PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE.get(subrole, _PRODUCT_ANALYTICS_TOPICS)
    product_analytics_block_no_resume = _PRODUCT_ANALYTICS_BLOCK_BY_SUBROLE_NO_RESUME.get(
        subrole, _PRODUCT_ANALYTICS_TOPICS_NO_RESUME
    )

    if resume_text:

        return f"""
You are an expert Product Management interviewer hiring for leading companies such as Google, Microsoft, Amazon, Meta, Uber, Atlassian, Salesforce, Adobe, Flipkart, PhonePe, Razorpay and Swiggy.

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
- Focus on product initiatives, internships, leadership, product launches, business impact, user problems solved, metrics, cross-functional collaboration and achievements.

2. Product Sense & Product Design (2)

Generate exactly 2 questions.

Difficulty Guidelines

{product_sense_block}

Questions must strictly match the selected difficulty.

3. Product Strategy & Business Thinking (2)

Generate exactly 2 questions.

Topics include:

{product_strategy_block}

4. Product Analytics & Execution (3)

Generate exactly 3 questions.

Topics include:

{product_analytics_block}

Adjust complexity according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner, similar to how an experienced Product Manager would conduct an interview.
- Use simple, easy-to-understand English while preserving important product management terminology.
- The difficulty should come from the product problem being discussed, not from complicated wording.
- Encourage candidates to explain their assumptions, thought process and trade-offs.
- Questions should resemble real Product Management interviews.

Avoid overly direct textbook-style questions such as:

- "Explain MVP."
- "Define Product Lifecycle."
- "What is A/B Testing?"

Instead, naturally introduce topics using a variety of conversational styles such as:

- "Let's talk about..."
- "Suppose you've just joined..."
- "Imagine you're the Product Manager for..."
- "Can you walk me through..."
- "How would you approach..."
- "A product's user engagement suddenly drops..."
- "What factors would you consider..."
- "Could you explain..."
- "Why do you think..."

Do NOT start every question with the same phrase.

Vary the wording naturally throughout the interview.

Important Instructions

- Product Management interviews often do not have a single correct answer.
- Ask open-ended questions that evaluate structured thinking, user empathy, prioritization, decision-making and business understanding.
- Encourage the candidate to think aloud and justify their assumptions.
- Avoid trivia or definition-based questions whenever possible.
- Prefer practical product scenarios over theoretical questions.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Product Management competencies.
- Keep every question concise while still being conversational.
- Questions should resemble real interviews conducted by leading technology companies.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""

    return f"""
You are an expert Product Management interviewer hiring for leading companies such as Google, Microsoft, Amazon, Meta, Uber, Atlassian, Salesforce, Adobe, Flipkart, PhonePe, Razorpay and Swiggy.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure

1. Role-Specific Product Management Questions (2)

Generate exactly 2 additional role-specific Product Management questions because no resume is available.

2. Product Sense & Product Design (2)

Generate exactly 2 questions.

Topics include:

{product_sense_block_no_resume}

3. Product Strategy & Business Thinking (2)

Generate exactly 2 questions.

Topics include:

{product_strategy_block_no_resume}

4. Product Analytics & Execution (3)

Generate exactly 3 questions.

Topics include:

{product_analytics_block_no_resume}

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines

- Ask every question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving important Product Management terminology.
- The difficulty should come from solving product problems, not from complicated wording.
- Encourage structured thinking, user empathy and business reasoning.
- Questions should resemble real Product Management interviews.

Avoid textbook-style questions.

Use conversational openings such as:

- "Let's talk about..."
- "Suppose you've just joined..."
- "Imagine you're the Product Manager for..."
- "Can you walk me through..."
- "How would you approach..."

Do NOT start every question with the same phrase.

Important Instructions

- Product Management interviews often do not have a single correct answer.
- Evaluate structured thinking rather than factual recall.
- Encourage the candidate to justify decisions and discuss trade-offs.

General Rules

- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different Product Management competencies.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Return ONLY the numbered interview questions.

Do not include headings, introductions, markdown, bullet points or any text before or after the questions.
"""