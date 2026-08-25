"""
Evaluation prompt builder.

This module contains the prompt used to evaluate a candidate's interview
answer. The prompt is intentionally separated from AIService so that all
prompt engineering lives under the prompts package.

IMPORTANT:
- Do NOT modify the JSON response schema without updating the parser.
- Do NOT modify the score range unless the parser is updated.
"""


def build_evaluation_prompt(
    question_text: str,
    user_answer: str,
) -> str:
    """
    Build the Gemini prompt for evaluating interview answers.

    Args:
        question_text: Interview question.
        user_answer: Candidate's combined answer.

    Returns:
        Complete evaluation prompt.
    """

    return f"""
You are an expert technical interviewer evaluating a candidate's interview answer.

Your task is to evaluate the candidate's answer for the given interview question.

Evaluate the answer on these 3 dimensions:

1. Technical Correctness
   - Are the concepts factually correct?
   - Is the explanation technically sound?
   - Are important technical terms used properly?

2. Completeness should be judged based on whether the candidate covered the key concepts required by the question, NOT by the length of the answer.

A concise answer that correctly addresses all important concepts should receive a high score.

Do NOT penalize an answer simply because it is brief.

Do NOT recommend "add more detail", "explain more", or "elaborate further" unless the answer actually omitted important technical concepts.

3.Communication Clarity

- Is the technical explanation logically organized?
- Are the ideas presented in a coherent order?
- Is the reasoning easy to follow?

Do NOT score based on fluency, speaking style, verbosity, or answer length.
   
Never include feedback about the candidate's speaking style, answer length, or presentation unless the interview question explicitly evaluates communication skills.

Focus only on the technical accuracy, completeness of the required concepts, and relevance to the question.

Scoring Rules:

- Return a single overall score from 1 to 10.

- 1–3:
  Major conceptual misunderstandings, incorrect technical explanations, or failure to answer the question.

- 4–6:
  Demonstrates partial understanding but misses one or more important technical concepts or contains notable inaccuracies.

- 7–8:
  Technically correct and covers most of the important concepts.
  Minor omissions or inaccuracies may exist, but they do not significantly affect the overall correctness.
  A concise answer that correctly covers the required concepts should still receive a score in this range.

- 9–10:
  Technically accurate, complete, logically structured, and demonstrates interview-ready understanding.
  The answer should correctly explain all major concepts, mention important trade-offs or practical considerations where appropriate, and contain no significant technical mistakes.

Do NOT increase or decrease the score based on answer length.
Score only based on technical correctness, relevance, completeness of the required concepts, and logical reasoning.

Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
Do not include explanations outside JSON.
Do not include any extra text before or after the JSON.

The JSON must follow exactly this structure:
{{
  "score": 8,
  "feedback": "Overall evaluation summary here",
  "strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "improvements": [
    "Improvement 1",
    "Improvement 2"
  ]
}}

Rules for the JSON fields:

- "score" must be an integer from 1 to 10.

- "feedback" should be a personalized coaching summary written in 2–4 sentences.
  Explain what the candidate understood well and what prevented them from achieving a higher score.
  Do not criticize the communication style unless it prevented understanding of the technical content.
  Focus the feedback on technical concepts rather than presentation style.
  Mention only concepts that appeared in the question or were expected in the answer.
  Whenever possible, explicitly mention the concepts listed in the "strengths" and "improvements" fields so that the summary aligns with the detailed feedback.
  Do NOT simply say "good answer" or "needs improvement".
  Make the feedback sound like advice from an experienced interviewer.

- "strengths" must contain ONLY specific concepts, technologies, principles or technical topics that the candidate demonstrated correctly.
  Examples:
  - "JWT Authentication"
  - "Binary Search"
  - "Database Normalization"
  - "TCP Three-Way Handshake"

  Do NOT write generic statements such as:
  - "Good explanation"
  - "Clear communication"
  - "Well structured answer"

-"improvements" must contain ONLY the specific concepts, principles, technologies, algorithms or design ideas that the candidate should study further.

Every improvement should answer the question:

"What exact technical topic should the candidate revise?"

If a concept is only partially understood, return the specific sub-topic rather than the broader subject.

For example:

Instead of:
- Database Normalization

Prefer:
- Boyce-Codd Normal Form (BCNF)
- Functional Dependencies
- Candidate Keys

Instead of:
- Operating Systems

Prefer:
- Deadlock Detection
- Deadlock Prevention
- Banker's Algorithm

Instead of:
- Networking

Prefer:
- TCP Congestion Control
- Sliding Window Protocol
- DNS Resolution

Avoid generic feedback such as:

- Explain better
- Give more details
- Improve clarity
- Use more examples
- Better communication
- Detailed use case explanation

Instead return precise technical concepts.

Examples:

Question: Explain polymorphism.

Good improvements:
- Runtime Polymorphism
- Strategy Pattern
- Method Overriding
- Interface-based Design

Bad improvements:
- Explain in more detail
- Give more examples
- Better explanation

- Return between 2 and 5 strengths.
- Return between 2 and 5 improvements.
- Avoid duplicate concepts.
- Every concept should be concise (typically 2–5 words).
- All values must be based only on the interview question and candidate answer provided below.

Interview Question:
{question_text}

Candidate Answer:
{user_answer}
""".strip()

def build_follow_up_prompt(
    original_question: str,
    candidate_answer: str,
    evaluation: dict,
    follow_up_depth: int,
) -> str:
    """
    Builds a prompt for generating a follow-up interview question.

    Args:
        original_question: The main interview question.
        candidate_answer: The candidate's answer.
        evaluation: Parsed evaluation dictionary returned by Gemini.
        follow_up_depth: Current follow-up depth (1 or 2).

    Returns:
        Prompt string for Gemini.
    """

    next_depth = follow_up_depth + 1

    return f"""
You are an expert interviewer conducting a professional interview.

The candidate answered the following interview question well enough that you want
to explore the SAME topic in greater depth.

Generate EXACTLY ONE follow-up interview question.

Original Question:
{original_question}

Candidate Answer:
{candidate_answer}

Evaluation Score:
{evaluation["score"]}/10

Evaluation Summary:
{evaluation["feedback"]}

Strengths:
{chr(10).join("- " + s for s in evaluation["strengths"])}

Areas for Improvement:
{chr(10).join("- " + i for i in evaluation["improvements"])}

Current Follow-up Depth:
{follow_up_depth}

Next Follow-up Depth:
{next_depth}

Requirements

- Stay on EXACTLY the same topic.
- Do NOT introduce a completely new topic.
- The follow-up should naturally continue the discussion.
- Make the question slightly more challenging than the previous one.
- Encourage reasoning, practical thinking and trade-offs.
- Do NOT repeat the original question.
- Do NOT ask a definition that has already been answered.
- Assume the candidate has demonstrated a reasonable understanding of the topic.

Interview Style Guidelines

- Ask the follow-up question in a natural, conversational and professional manner.
- Use simple, easy-to-understand English while preserving all important technical or domain terminology.
- The difficulty should come from the concepts being tested, not from complicated wording.
- The follow-up should feel like a natural continuation of the discussion.
- Encourage the candidate to explain reasoning, implementation decisions, trade-offs or design choices.

Avoid textbook-style questions such as:

- Explain...
- Define...
- What is...

Instead naturally continue the discussion using phrases such as:

- Let's go a little deeper into that...
- You mentioned...
- Could you expand on...
- Suppose we change the situation slightly...
- Imagine you're working on...
- Can you walk me through...
- How would your approach change if...
- Why do you think...
- What trade-offs would you consider...

Do NOT start every follow-up with the same phrase.

Vary the wording naturally.

Difficulty Progression

If Next Follow-up Depth is 1:
- Ask about application.
- Ask for an example.
- Ask about practical implementation.

If Next Follow-up Depth is 2:
- Ask about trade-offs.
- Ask about edge cases.
- Ask about optimization.
- Ask about real-world scenarios.
- Ask about architecture or design decisions.

General Rules

- Generate EXACTLY ONE follow-up question.
- Return ONLY the question.
- Do NOT number the question.
- Do NOT provide answers.
- Do NOT provide explanations.
- Do NOT include markdown.
""".strip()


def build_skipped_topics_prompt(
    question_texts: list[str],
) -> str:
    """
    Builds a prompt that identifies, for each skipped interview
    question, the single specific topic the candidate should
    study. Batched into one request for every skipped question
    in a session, instead of one Gemini call per skipped
    question.
    """

    numbered_questions = "\n\n".join(
        f"Question {index + 1}:\n{text}"
        for index, text in enumerate(question_texts)
    )

    return f"""
You are helping a student understand exactly what they should
study after skipping interview questions.

For EACH question below, identify ONE specific topic or concept
the student should study to be able to answer it.

Rules:

- Return exactly one topic per question, in the same order as
  the questions.
- The topic must be a specific, concrete concept - not vague
  advice.
- Keep each topic short: roughly 2-6 words.
- Use simple, clear wording a student can immediately understand
  and search for.

Do NOT return generic advice such as:
- Study fundamentals
- Improve technical knowledge
- Practice more
- Learn the basics
- Prepare better
- Review concepts

Instead identify the exact concept being tested.

Examples:

Question: What are the ACID properties in DBMS?
Topic: ACID Properties

Question: How does binary search work?
Topic: Binary Search

Question: How does TCP establish a connection?
Topic: TCP Three-Way Handshake

If a question is clearly based on the candidate's own resume,
project, or experience (it references a specific project name,
a technology used in a project, an internship, or similar), the
topic MUST name that specific project or technology so the
student knows exactly what to revise.

Examples:

Question: How would you implement JWT authentication in your
HotSeat AI project?
Topic: JWT Authentication in HotSeat AI

Question: Walk me through the database design in your project.
Topic: Database Design in Your Project

Question: You mentioned using Docker in your resume - how did
you use it?
Topic: Docker Containerization

Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
Do not include explanations outside JSON.

The JSON must be an array of exactly {len(question_texts)}
strings, one topic per question, in the same order as the
questions below:

["Topic 1", "Topic 2", ...]

Questions:

{numbered_questions}
""".strip()