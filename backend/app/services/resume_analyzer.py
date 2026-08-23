import json

from google.genai import types

from app.core.config import GEMINI_MODEL

from app.services.api_key_manager import (
    api_key_manager,
)
from app.schemas.resume_analysis import ResumeProfile


class ResumeAnalyzer:
    """
    Converts raw resume text into a structured,
    evidence-grounded resume profile.

    This service does NOT generate recommendations.

    Its only responsibility is to determine what
    the resume actually contains.
    """

    def analyze(
        self,
        resume_text: str,
    ) -> ResumeProfile:

        if not resume_text or not resume_text.strip():
            raise ValueError(
                "Resume does not contain extracted text."
            )

        prompt = f"""
You are the Resume Intelligence Engine for HotSeat.

Your job is to convert the candidate's resume into
a structured representation of ONLY what the resume
actually proves.

RESUME
==================================================

{resume_text}

==================================================

STRICT EVIDENCE RULES
==================================================

1. NEVER invent information.

2. NEVER infer a technology simply because another
technology appears.

Examples:

Python does NOT imply Django.

AWS does NOT imply Azure.

Salesforce does NOT imply HubSpot.

Salesforce does NOT imply HubSpot.

GAAP knowledge does NOT imply IFRS knowledge.

3. Every important claim must have supporting
source text from the resume.

4. Preserve the original wording when possible.

5. Identify the section where each claim appears.

6. Extract technologies explicitly mentioned.

7. Extract measurable information.

Examples:

"20% improvement"
"500 users"
"95% accuracy"

8. NEVER create metrics that are not present.

9. NEVER convert vague statements into specific
measurements.

For example:

"improved performance"

must NOT become:

"improved performance by 30%"

10. Identify action verbs used in bullets.

Examples:

Developed
Optimized
Led

11. Identify achievements separately from ordinary
responsibilities.

12. Preserve the distinction between:

- Skills
- Technologies
- Responsibilities
- Achievements
- Projects
- Experience
- Education
- Certifications

"Technologies" includes not only software languages and
frameworks but any named professional tool, platform,
system, or standard relevant to the candidate's field
(e.g. Salesforce, GAAP, Epic/Cerner clinical systems,
AutoCAD, Adobe Creative Suite).

13. If a claim is ambiguous, preserve it as ambiguous.
Do NOT upgrade its confidence.

14. Do not infer seniority from technology names alone.

15. Do not infer years of experience unless explicitly
stated or clearly supported by dates.

16. Do not infer ownership.

For example:

"Worked on a project"

does NOT prove:

"Led the project."

17. Do not infer leadership from collaboration.

18. Do not infer production usage unless the resume
explicitly indicates production/deployment/use.

19. Extract all relevant evidence even if it appears
multiple times.

20. Avoid duplicate evidence when possible.

==================================================

The final result will later be compared against
a Job Description.

Therefore accuracy and evidence preservation are
more important than making the resume sound impressive.

Return ONLY structured data matching the schema.
"""

        response = api_key_manager.generate_content(
            contents=prompt,
            config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ResumeProfile,
            temperature=0.0,
            ),
            purpose="resume_structuring",
        )

        raw_response = (
            response.text or ""
        ).strip()

        if not raw_response:
            raise ValueError(
                "Gemini returned an empty resume analysis."
            )

        try:
            parsed = json.loads(
                raw_response
            )

            return ResumeProfile.model_validate(
                parsed
            )

        except Exception as exc:
            raise ValueError(
                "Gemini returned invalid structured "
                "resume analysis."
            ) from exc