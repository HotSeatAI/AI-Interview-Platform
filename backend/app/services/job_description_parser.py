import json
from io import BytesIO

from fastapi import UploadFile
from google.genai import types
from pypdf import PdfReader
from app.core.config import GEMINI_MODEL

from app.services.api_key_manager import (
    api_key_manager,
)
from app.schemas.resume_analysis import JDProfile


class JobDescriptionParser:

    async def extract_pdf_text(
        self,
        file: UploadFile,
    ) -> str:

        content = await file.read()

        reader = PdfReader(
            BytesIO(content)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text and text.strip():
                pages.append(
                    text.strip()
                )

        extracted_text = "\n\n".join(
            pages
        ).strip()

        if not extracted_text:
            extracted_text = self._extract_pdf_text_via_ocr(
                content
            )

        return extracted_text

    def _extract_pdf_text_via_ocr(
        self,
        pdf_bytes: bytes,
    ) -> str:

        prompt = """
You are extracting a Job Description from a PDF that has no usable text layer (it is scanned or image-based).

Read every page carefully.

Extract the COMPLETE visible job description, preserving:
- Job title
- Responsibilities
- Required qualifications
- Preferred qualifications
- Technical skills
- Soft skills
- Experience requirements
- Education requirements
- Certifications
- Years of experience
- Named technologies
- Frameworks
- Programming languages
- Tools
- Cloud platforms
- Important numbers

Do NOT summarize.

Do NOT invent missing information.

Do NOT add information that is not visible.

Return only the extracted job description text.
"""

        response = api_key_manager.generate_content(
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf",
                ),
                prompt,
            ],
            purpose="jd_pdf_ocr",
        )

        text = (
            response.text or ""
        ).strip()

        if not text:
            raise ValueError(
                "Could not extract text from the PDF."
            )

        return text

    async def extract_image_text(
        self,
        file: UploadFile,
    ) -> str:

        image_bytes = await file.read()

        mime_type = file.content_type

        allowed_types = {
            "image/png",
            "image/jpeg",
            "image/webp",
            "image/heic",
            "image/heif",
        }

        if mime_type not in allowed_types:
            raise ValueError(
                "Unsupported image format."
            )

        prompt = """
You are extracting a Job Description from an image.

Read the image carefully.

Extract the COMPLETE visible job description.

Preserve:
- Job title
- Responsibilities
- Required qualifications
- Preferred qualifications
- Technical skills
- Soft skills
- Experience requirements
- Education requirements
- Certifications
- Years of experience
- Named technologies
- Frameworks
- Programming languages
- Tools
- Cloud platforms
- Important numbers

Do NOT summarize.

Do NOT invent missing information.

Do NOT add information that is not visible.

Return only the extracted job description text.
"""

        response = api_key_manager.generate_content(
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
            prompt,
            ],
            purpose="jd_image_ocr",
        )

        text = (
            response.text or ""
        ).strip()

        if not text:
            raise ValueError(
                "Could not extract text from the image."
            )

        return text

    async def extract_job_description(
        self,
        text: str | None = None,
        file: UploadFile | None = None,
    ) -> str:

        if text and text.strip():
            return text.strip()

        if not file:
            raise ValueError(
                "Provide either JD text or a JD file."
            )

        content_type = (
            file.content_type or ""
        ).lower()

        if content_type == "application/pdf":
            return await self.extract_pdf_text(
                file
            )

        if content_type.startswith("image/"):
            return await self.extract_image_text(
                file
            )

        raise ValueError(
            "Unsupported JD format. "
            "Supported formats: PDF, PNG, JPEG, WEBP."
        )

    def structure_job_description(
        self,
        job_description: str,
    ) -> JDProfile:

        prompt = f"""
You are the Job Description Intelligence Engine
for Hot Seat.

Analyze the following job description.

JOB DESCRIPTION
================
{job_description}
================

Your job is to convert it into a structured representation.

STRICT RULES:

1. Extract ONLY information supported by the JD.

2. NEVER invent requirements.

3. Separate:
   - technical skills
   - responsibilities
   - soft skills
   - experience
   - education
   - certifications
   - domain knowledge
   - tools

4. Determine whether each requirement is:
   - required
   - preferred
   - nice_to_have
   - unclear

5. Assign importance from 1 to 10.

10:
Explicitly required or central to the role.

8-9:
Very important requirement.

6-7:
Important requirement.

4-5:
Preferred requirement.

1-3:
Minor / nice-to-have requirement.

6. Extract important keywords.

Do NOT include generic words such as:
candidate
company
team
work
skills
experience

unless they are part of a meaningful requirement.

7. Normalize obvious aliases.

Valid examples:

Postgres → PostgreSQL
JS → JavaScript
CRM → Customer Relationship Management
GAAP → Generally Accepted Accounting Principles

8. DO NOT treat different technologies as aliases.

For example:

AWS != Azure
Docker != Kubernetes

Related-but-different tools like these should instead be
captured via "adjacent_alternatives" — see rule 14 below.

9. Preserve evidence from the JD supporting
each important requirement.

10. Do not infer a requirement merely because
it is common for the role.

11. If the JD is ambiguous, mark the requirement
as "unclear".

12. The final representation must be useful for
matching the JD against a candidate's resume.

13. COMPOUND REQUIREMENTS:

Some requirement names conjoin two or more distinct
concepts, usually joined by "and", "&", "/", or a comma.

Examples of compound requirement names:

"Frontend Technologies & Web Services"
"Collaborative Coding Experience"
"Client Relationship Management & Account Growth"

For each requirement whose name bundles multiple
distinct concepts together, populate "components"
with short, atomic concept names — one per distinct
concept, using plain lowercase phrases.

Examples:

"Frontend Technologies & Web Services"
components: ["frontend technologies", "web services"]

"Collaborative Coding Experience"
components: ["collaborative coding experience"]
(a single concept — do NOT invent a split that
is not actually present in the requirement name)

"Client Relationship Management & Account Growth"
components: ["client relationship management", "account growth"]

If a requirement already names exactly one concept,
leave "components" empty. Do NOT split a single
concept into unrelated fragments merely to populate
this field.

14. ADJACENT (RELATED BUT NOT EQUIVALENT) ALTERNATIVES:

For each requirement, if there is a well-known tool,
platform, framework, or standard that professionals in
this field would recognize as RELATED to this requirement
but NOT a substitute for it, populate
"adjacent_alternatives" with that alternative's name
(lowercase, short). Only include alternatives with strong,
common professional recognition — do not guess obscure
ones. Leave the list empty if none apply.

Examples:

Requirement: "AWS"
adjacent_alternatives: ["azure", "gcp"]

Requirement: "Salesforce"
adjacent_alternatives: ["hubspot", "zoho crm"]

Requirement: "GAAP"
adjacent_alternatives: ["ifrs"]

Requirement: "Docker"
adjacent_alternatives: ["kubernetes"]

Requirement: "5+ years of project management experience"
adjacent_alternatives: []
(a general experience requirement has no well-known
"related but different" alternative — do not force this
field)

15. INDIRECT EVIDENCE HINTS:

For each requirement — especially soft skills,
responsibilities, and abstract/conceptual requirements
that are NOT a concrete named tool — populate
"evidence_hints" with short, literal resume phrases (2-5
words) that a resume would plausibly contain VERBATIM as
indirect proof of this requirement, even if the
requirement's own name or aliases never appear. These are
search terms only, not proof by themselves — a resume
must still contain the literal phrase.

Examples:

Requirement: "Client Relationship Management"
evidence_hints: ["account management", "client retention",
"renewals", "upsells", "relationship building"]

Requirement: "Production Safety"
evidence_hints: ["on-call", "incident response", "rollback",
"post-mortem"]

Requirement: "GAAP Compliance"
evidence_hints: ["financial statements", "audit",
"reconciliation", "month-end close"]

Leave "evidence_hints" empty for requirements that are
already concrete named tools/technologies (e.g. "Python",
"Salesforce") where a direct name match is sufficient.

16. DEALBREAKER FLAG:

Set "is_dealbreaker" to true ONLY for a genuine hard gate a
real recruiter would screen a candidate OUT on if missing —
regardless of how strong everything else is. This is RARE.

Valid dealbreakers:
- An explicit hard floor on years of experience ("minimum 5
  years required")
- A required license or professional certification (e.g. a
  nursing license, a bar admission, a PE license)
- Required work authorization / security clearance

NOT dealbreakers (leave false): a required technical skill,
a required degree, a required tool/technology, or any other
"required" item that a strong candidate could still plausibly
compensate for elsewhere. Most requirements, including most
"required" ones, are NOT dealbreakers — default to false
unless a requirement clearly matches one of the valid
categories above.

17. COMPLETENESS OF REQUIRED/PREFERRED QUALIFICATIONS:

Every distinct qualification named anywhere under a
Required/Minimum Qualifications or Preferred Qualifications
section MUST end up represented somewhere in the output —
either as its own requirement in "requirements", or folded
into an existing requirement's "aliases"/"evidence_hints" if
it is a close variant of something already captured. Do not
silently drop a named qualification because it seems minor
or because another requirement already covers something
similar.

This especially applies to a SINGLE bullet that names several
distinct sub-qualifications joined by commas/"or"/"and" —
every named term in that bullet must be individually
represented, not just the first or most prominent one.

Example — this input bullet:

"Understanding of software engineering fundamentals,
including testing, code quality, and maintainability."

must NOT be dropped entirely, and must not collapse to only
one of its three named concepts. Represent it as its own
requirement with components ["testing", "code quality",
"maintainability"], or, if closely related to an existing
requirement, add "testing", "code quality", and
"maintainability" into that requirement's "evidence_hints".

Example — this input bullet:

"Exposure to telemetry, data analysis, statistics, or cloud
data platforms."

If a requirement already exists for "telemetry" and "data
analysis", still add "statistics" and "cloud data platforms"
into that requirement's "aliases" or "evidence_hints" rather
than leaving them unrepresented anywhere in the output.

Return ONLY structured data matching the schema.
"""

        response = api_key_manager.generate_content(
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JDProfile,
                temperature=0.0,
            ),
            purpose="jd_structuring",
        )

        raw_response = (
            response.text or ""
        ).strip()

        if not raw_response:
            raise ValueError(
                "Gemini returned an empty JD analysis."
            )

        try:

            parsed = json.loads(
                raw_response
            )

            return JDProfile.model_validate(
                parsed
            )

        except Exception as exc:

            raise ValueError(
                "Gemini returned an invalid "
                "structured JD response."
            ) from exc