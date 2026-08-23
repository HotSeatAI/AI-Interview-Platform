import json

from app.services.role_classifier import RoleClassifier
from app.services.api_key_manager import api_key_manager
from app.services.prompts.software_prompt import build_software_prompt
from app.services.prompts.finance_prompt import build_finance_prompt
from app.services.prompts.consulting_prompt import build_consulting_prompt
from app.services.prompts.sales_prompt import build_sales_prompt
from app.services.prompts.marketing_prompt import build_marketing_prompt
from app.services.prompts.evaluation_prompt import (
    build_evaluation_prompt,
    build_follow_up_prompt,
    build_skipped_topics_prompt,
)

class AIService:

    def __init__(self):

        self.key_manager = api_key_manager

        self.role_classifier = RoleClassifier()

    def generate_questions(
        self,
        resume_text: str | None,
        role: str,
        difficulty: str,
    ):

        category = self.role_classifier.classify_role(role)

        if category == "software":

            prompt = build_software_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        elif category == "finance":

            prompt = build_finance_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        elif category == "consulting":

            prompt = build_consulting_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        elif category == "sales":

            prompt = build_sales_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        elif category == "marketing":

            prompt = build_marketing_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        else:

            prompt = build_software_prompt(
                role=role,
                difficulty=difficulty,
                resume_text=resume_text,
            )

        print("\n========== SELECTED ROLE ==========")
        print(role)

        print("\n========== INTERVIEW CATEGORY ==========")
        print(category)

        response = self.key_manager.generate_content(
            prompt,
            purpose="interview_question_generation",
        )

        print("\n===== GEMINI QUESTION RESPONSE =====\n")
        print(response)

        return response.text
    def build_combined_answer(
        self,
        voice_text: str | None,
        typed_text: str | None,
        code: str | None
    ) -> str:

        sections = []

        if voice_text and voice_text.strip():
            sections.append(
                f"Explanation:\n{voice_text.strip()}"
            )

        # TODO(backend migration): typed_text is always empty from the
        # frontend now — see the TODO on AnswerCreate.typed_text in
        # schemas/answer.py. Drop this parameter once nothing relies on it.
        if typed_text and typed_text.strip():
            sections.append(
                f"Additional Notes:\n{typed_text.strip()}"
            )

        if code and code.strip():
            sections.append(
                f"Code:\n{code.strip()}"
            )

        if not sections:
            raise ValueError(
                "At least one of voice_text, typed_text or code must be provided."
            )

        return "\n\n".join(sections)

    def parse_evaluation_response(
        self,
        response_text: str
    ) -> dict:

        try:
            parsed_response = json.loads(
                response_text.strip()
            )
        except json.JSONDecodeError:
            raise ValueError(
                "Gemini returned invalid JSON for answer evaluation."
            )

        required_keys = [
            "score",
            "feedback",
            "strengths",
            "improvements"
        ]

        for key in required_keys:
            if key not in parsed_response:
                raise ValueError(
                    f"Missing key '{key}' in Gemini evaluation response."
                )

        score = parsed_response["score"]
        feedback = parsed_response["feedback"]
        strengths = parsed_response["strengths"]
        improvements = parsed_response["improvements"]

        if not isinstance(score, int):
            raise ValueError("Gemini evaluation score must be an integer.")

        if score < 1 or score > 10:
            raise ValueError("Gemini evaluation score must be between 1 and 10.")

        if not isinstance(feedback, str):
            raise ValueError("Gemini evaluation feedback must be a string.")

        if not isinstance(strengths, list):
            raise ValueError("Gemini evaluation strengths must be a list.")

        if not isinstance(improvements, list):
            raise ValueError("Gemini evaluation improvements must be a list.")

        if not all(isinstance(item, str) for item in strengths):
            raise ValueError("All strengths must be strings.")

        if not all(isinstance(item, str) for item in improvements):
            raise ValueError("All improvements must be strings.")

        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements
        }

    def evaluate_answer(
        self,
        question_text: str,
        user_answer: str
    ) -> dict:

        prompt = build_evaluation_prompt(
            question_text=question_text,
            user_answer=user_answer
        )

        response = self.key_manager.generate_content(
            prompt,
            purpose="answer_evaluation",
        )

        print("\n===== GEMINI ANSWER EVALUATION RESPONSE =====\n")
        print(response)

        return self.parse_evaluation_response(
            response.text
        )
    
    def generate_follow_up_question(
        self,
        original_question: str,
        candidate_answer: str,
        evaluation: dict,
        follow_up_depth: int,
    ) -> str:
        """
        Generates a single follow-up interview question.

        Args:
            original_question: Main interview question.
            candidate_answer: Candidate's answer.
            evaluation: Evaluation dictionary returned by evaluate_answer().
            follow_up_depth: Current follow-up depth.

        Returns:
            Follow-up question.
        """

        prompt = build_follow_up_prompt(
            original_question=original_question,
            candidate_answer=candidate_answer,
            evaluation=evaluation,
            follow_up_depth=follow_up_depth,
        )

        response = self.key_manager.generate_content(
            prompt,
            purpose="follow_up_question_generation",
        )

        print("\n===== GEMINI FOLLOW-UP QUESTION =====\n")
        print(response.text)

        return response.text.strip()

    def generate_skipped_topics(
        self,
        question_texts: list[str],
    ) -> list[str]:
        """
        For a batch of skipped interview questions, returns the
        single study topic for each, in the same order. One
        Gemini call handles the whole batch regardless of how
        many questions were skipped.

        Falls back to a generic per-question label instead of
        raising if Gemini's response can't be parsed, so a
        malformed response never breaks the final report.
        """

        if not question_texts:
            return []

        prompt = build_skipped_topics_prompt(
            question_texts
        )

        try:

            response = self.key_manager.generate_content(
                prompt
            )

            topics = json.loads(
                response.text.strip()
            )

            if (
                not isinstance(topics, list)
                or len(topics) != len(question_texts)
                or not all(
                    isinstance(topic, str) and topic.strip()
                    for topic in topics
                )
            ):
                raise ValueError(
                    "Unexpected skipped-topics response shape."
                )

            return [
                topic.strip()
                for topic in topics
            ]

        except Exception as exc:

            print(
                "\n===== SKIPPED TOPICS GENERATION FAILED =====\n"
                f"{exc}"
            )

            return [
                "Review This Topic"
                for _ in question_texts
            ]