"""
Topic practice prompt builder.

Generates a short, focused round of questions testing ONE specific
weak topic a candidate was flagged on in a past interview - used by
the weak-topic practice feature (api/topics.py). Output format
deliberately matches the existing numbered-list format used by the
main question-generation prompts (software_prompt.py etc.) so it can
be parsed by the exact same regex already in api/interview.py, with
no new parsing logic needed.
"""


def build_topic_practice_prompt(topic: str) -> str:
    """
    Build the Gemini prompt for a 3-question practice round on a
    single named topic, at a fixed Easy -> Medium -> Medium curve.

    Args:
        topic: The specific concept the candidate was flagged weak on
            (e.g. "Boyce-Codd Normal Form", "Deadlock Prevention").

    Returns:
        Complete topic-practice prompt.
    """

    return f"""
You are an expert interviewer creating a short focused practice round on
ONE specific topic a candidate needs to improve on.

Topic: {topic}

Generate EXACTLY 3 interview questions that test understanding of this
topic specifically - not a broad related subject, this exact concept.

Difficulty curve (follow this order exactly):
1. Question 1: Easy - tests the basic definition/understanding.
2. Question 2: Medium - tests applying the concept.
3. Question 3: Medium - tests a deeper or trickier aspect (an edge
   case, a trade-off, or a common mistake) of the same concept.

Formatting rules (must match exactly):

- Number each question "1.", "2.", "3." at the start of its line.
- If a question requires writing code to answer properly, add a line
  "TYPE: CODING" immediately after the question number for that
  question only. Most topics won't need this - only use it if the
  topic is inherently a coding/algorithm topic.
- Do NOT include answers, explanations, or hints.
- Do NOT include any text before question 1 or after question 3.
- Use simple, clear English - the difficulty should come from the
  concept being tested, not complicated wording.
""".strip()
