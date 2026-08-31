"""
Software interview prompt builder.

This module contains the original software interview prompt that was
previously embedded inside ai_service.py.

IMPORTANT:
- Do NOT modify the interview structure.
- Do NOT modify the question distribution.
- Do NOT modify the difficulty behavior.
- Do NOT modify the resume/no-resume behavior.

This prompt has only been moved into its own module to support
clean routing for multiple interview categories.

Sub-role awareness: the "Core Computer Science Fundamentals" and
"System Design Concepts" sections below have their topic lists
chosen per sub-role (see classify_software_subrole in
role_classifier.py) rather than being fixed to OS/DBMS/OOP and
generic backend-scaling topics for every software role - e.g. an
ML Engineer gets Python/ML Fundamentals instead of OS/DBMS. The
"generic" bucket (backend/full-stack/SDE/unmatched roles) keeps
the original OS/DBMS/OOP + backend-scaling topics unchanged. This
does NOT change the interview structure, question counts,
difficulty behavior, or resume/no-resume behavior above - it only
substitutes the content of those two topic lists.
"""

from app.services.role_classifier import classify_software_subrole


_FUNDAMENTALS_BY_SUBROLE = {
    "generic": """Focus primarily on:
- Operating Systems
- Database Management Systems (DBMS)
- Object-Oriented Programming (OOP)

Use Computer Networks only if it is relevant to the selected role.""",
    "ml_data_science": """Focus primarily on:
- Python
- Machine Learning Fundamentals (bias-variance tradeoff, overfitting/underfitting, gradient descent)
- Statistics & Probability
- Model Evaluation Metrics""",
    "data_engineering": """Focus primarily on:
- SQL & Database Design
- ETL / Data Pipelines
- Distributed Data Processing
- Data Warehousing""",
    "frontend": """Focus primarily on:
- JavaScript / TypeScript Fundamentals
- DOM & Browser Rendering
- Web Performance
- Accessibility & Responsive Design""",
    "mobile": """Focus primarily on:
- Object-Oriented Programming (OOP)
- Mobile App Lifecycle & Memory Management
- Concurrency / Threading on Mobile
- Platform-Specific Fundamentals (Android / iOS)""",
    "devops_sre": """Focus primarily on:
- Operating Systems
- Networking
- Containers & Orchestration
- CI/CD Fundamentals""",
    "qa_testing": """Focus primarily on:
- Software Testing Fundamentals
- Test Automation
- Object-Oriented Programming (OOP) for automation scripting
- Bug / Defect Lifecycle Management""",
}

_SYSTEM_DESIGN_BY_SUBROLE = {
    "generic": """- Caching
- Load Balancing
- Database Indexing
- Replication
- Sharding
- Horizontal vs Vertical Scaling
- CAP Theorem
- Message Queues
- API Gateway
- Microservices
- CDN
- Rate Limiting
- Consistency
- Fault Tolerance""",
    "ml_data_science": """- Feature Stores
- Model Serving & Inference
- Model Versioning & Monitoring
- Training Data Pipelines
- Batch vs Real-time Inference
- A/B Testing for Models""",
    "data_engineering": """- Data Pipeline Architecture
- Data Lake vs Data Warehouse
- Batch vs Streaming Processing
- Schema Design & Partitioning
- Data Quality & Governance""",
    "frontend": """- Component Architecture & State Management
- Client-side Caching & Performance
- Rendering Strategies (CSR / SSR / SSG)
- API Integration Patterns
- Micro-frontends""",
    "mobile": """- App Architecture (MVVM / MVC)
- Offline-First & Local Storage
- Battery & Network Efficiency
- Push Notifications & Background Sync
- App State Management""",
    "qa_testing": """- Test Automation Architecture
- CI/CD Test Pipelines
- Test Environment Management
- Flaky Test Mitigation
- Test Data Management""",
}
# DevOps/SRE keeps the same backend-scaling topics as "generic" -
# caching, load balancing, replication, fault tolerance etc. are
# genuinely accurate System Design topics for this role.
_SYSTEM_DESIGN_BY_SUBROLE["devops_sre"] = _SYSTEM_DESIGN_BY_SUBROLE["generic"]


def build_software_prompt(
    role: str,
    difficulty: str,
    resume_text: str | None = None,
) -> str:
    """
    Build the Gemini prompt for Software Engineering interviews.

    Args:
        role: Candidate's selected role.
        difficulty: Easy / Medium / Hard.
        resume_text: Parsed resume text if available.

    Returns:
        Complete prompt string to send to Gemini.
    """

    subrole = classify_software_subrole(role)
    fundamentals_block = _FUNDAMENTALS_BY_SUBROLE[subrole]
    system_design_block = _SYSTEM_DESIGN_BY_SUBROLE[subrole]

    if resume_text:

        return f"""
You are an expert Software Engineering interviewer at top product-based companies like Google, Amazon, Microsoft, Meta, Apple, Netflix and Uber.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

Candidate Resume:
{resume_text}

Generate EXACTLY 10 interview questions.

Interview Structure:

1. Resume-Based Questions (2)
- Ask exactly 2 questions based on the candidate's resume.
- Focus on projects, internships, technologies used, architecture, implementation choices, optimizations, challenges faced and achievements.
- Use the resume extensively.

2. Core Computer Science Fundamentals (3)
Generate exactly 3 questions.

{fundamentals_block}

Adjust the complexity according to the interview difficulty:
- Easy → basic concepts and definitions
- Medium → application-based interview questions
- Hard → advanced concepts, trade-offs and real interview scenarios

3. Coding / DSA (2)

Generate exactly 2 coding interview questions.

Requirements:

- Use famous interview problems commonly asked in Software Engineering interviews.
- Select problems appropriate for the chosen difficulty.
    - Easy → Comparable to LeetCode Easy
    - Medium → Comparable to LeetCode Medium
    - Hard → Comparable to LeetCode Hard

For EVERY coding question, keep the question number, then on its own line write exactly:

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
- Do NOT include any text before or after the required structure.

4. System Design Concepts (2)
Generate exactly 2 conceptual System Design questions.

DO NOT ask candidates to design systems such as:
- Design Twitter
- Design WhatsApp
- Design YouTube
- Design Uber

Instead ask conceptual interview questions on topics such as:
{system_design_block}

Increase the conceptual depth according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines:

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

Vary the wording naturally throughout the interview.

General Rules:
- Generate EXACTLY 10 questions.
- Questions must match the selected role.
- Questions must match the selected difficulty.
- Avoid duplicate concepts.
- Cover a variety of topics.
- Questions should resemble real Software Engineering interviews.
- Keep every question concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required technical keyword(s) or concept name(s) directly (e.g. "API", "DBMS", "Consistent Hashing", "CAP Theorem") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the 10 numbered interview questions.

For resume, CS fundamentals, system design and behavioral questions, return only the numbered question.

For coding questions, keep the numbering, then on its own line write exactly `TYPE: CODING`, then immediately follow the required coding question structure exactly as specified above. Do NOT add a `TYPE: CODING` line to any other question.

Do not include introductions, conclusions, markdown, or any additional explanatory text outside the questions.
"""

    return f"""
You are an expert Software Engineering interviewer at top product-based companies like Google, Amazon, Microsoft, Meta, Apple, Netflix and Uber.

You are conducting a live interview, not creating an exam paper.

Candidate Role:
{role}

Interview Difficulty:
{difficulty}

The candidate has NOT provided a resume.

Generate EXACTLY 10 interview questions.

Interview Structure:

1. Role-Specific Technical Questions (2)

Since there is no resume, generate 2 additional role-specific technical questions.

2. Core Computer Science Fundamentals (3)

{fundamentals_block}

Adjust the complexity according to the selected difficulty:
- Easy → basic concepts
- Medium → application-based interview questions
- Hard → advanced concepts and scenarios

3. Coding / DSA (2)

Generate exactly 2 coding interview questions.

Requirements:

- Use famous interview problems commonly asked in Software Engineering interviews.
- Select problems appropriate for the chosen difficulty.
    - Easy → Comparable to LeetCode Easy
    - Medium → Comparable to LeetCode Medium
    - Hard → Comparable to LeetCode Hard

For EVERY coding question, keep the question number, then on its own line write exactly:

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
- Do NOT include any text before or after the required structure.

4. System Design Concepts (2)

Generate exactly 2 conceptual System Design questions.

DO NOT ask candidates to design complete systems.

Instead ask conceptual interview questions about:
{system_design_block}

Increase the conceptual depth according to the selected difficulty.

5. Behavioral Question (1)

Generate exactly 1 behavioral interview question.

Interview Style Guidelines:

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

Vary the wording naturally throughout the interview.

General Rules:
- Generate EXACTLY 10 questions.
- Match the selected role.
- Match the selected difficulty.
- Avoid duplicate concepts.
- Cover different topics.
- Keep questions concise while still being conversational.
- Do NOT provide answers, hints or explanations.

Question Length & Style:
- Keep every question to at most 2-3 sentences (roughly 25-40 words).
- State the required technical keyword(s) or concept name(s) directly (e.g. "API", "DBMS", "Consistent Hashing", "CAP Theorem") instead of explaining or describing what they mean.
- Do NOT spend a sentence building a long scenario before asking the actual question - get to the question quickly.
- This does NOT apply to the Coding/DSA question structure (Problem Statement / Input Format / Output Format / Constraints / Examples), which must stay exactly as specified above.

Return ONLY the 10 numbered interview questions.

For role specific questions,CS fundamentals, system design and behavioral questions, return only the numbered question.

For coding questions, keep the numbering, then on its own line write exactly `TYPE: CODING`, then immediately follow the required coding question structure exactly as specified above. Do NOT add a `TYPE: CODING` line to any other question.

Do not include introductions, conclusions, markdown, or any additional explanatory text outside the questions.
"""