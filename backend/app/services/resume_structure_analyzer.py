import re

from app.schemas.resume_analysis import StructureReport

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\-.\s()]{7,}\d)")

# Canonical section name -> known header phrase variants. "summary"
# is tracked but intentionally excluded from REQUIRED_SECTIONS —
# many perfectly ATS-friendly resumes skip a summary/objective.
SECTION_SYNONYMS: dict[str, set[str]] = {
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "relevant experience",
    },
    "education": {
        "education",
        "academic background",
        "education and training",
    },
    "skills": {
        "skills",
        "technical skills",
        "core competencies",
        "key skills",
        "skills and tools",
    },
    "summary": {
        "summary",
        "professional summary",
        "objective",
        "profile",
        "career objective",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
    },
    "certifications": {
        "certifications",
        "licenses and certifications",
        "certificates",
        "licenses",
    },
    "achievements": {
        "achievements",
        "accomplishments",
        "honors and awards",
        "awards",
        "honors",
    },
    "publications": {
        "publications",
    },
    "volunteer": {
        "volunteer experience",
        "volunteering",
        "community involvement",
    },
    "leadership": {
        "leadership",
        "leadership experience",
    },
    "activities": {
        "activities",
        "extracurricular activities",
        "extracurriculars",
    },
    "languages": {
        "languages",
    },
    "interests": {
        "interests",
        "hobbies",
    },
    "references": {
        "references",
    },
}

REQUIRED_SECTIONS = ("experience", "education", "skills")

MAX_HEADER_LINE_LENGTH = 40
MAX_HEADER_WORD_COUNT = 5
MAX_UNRECOGNIZED_HEADERS = 10

_BULLET_PREFIX_PATTERN = re.compile(r"^\s*([•▪*\-]|\d+[.)])\s+")

# Common degree abbreviations — a degree line ("B.S. Computer
# Science") passes every other header heuristic (short, no
# digits, title case) but is never itself a section header.
_DEGREE_PATTERN = re.compile(
    r"\b(b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|ph\.?d\.?|mba|"
    r"b\.?tech|m\.?tech|bachelor'?s?|master'?s?|associate'?s?)\b",
    re.IGNORECASE,
)

# A short Title-Case line containing one of these words is
# virtually always a job/role title ("Interim Engineering
# Intern", "Website Analytics Intern") sitting inside an
# already-recognized Experience section — never a section
# header itself, even though it passes every other heuristic
# below (short, no digits, no trailing punctuation, Title Case).
_JOB_TITLE_PATTERN = re.compile(
    r"\b(intern|engineer|developer|manager|analyst|specialist|"
    r"coordinator|assistant|associate|director|lead|consultant|"
    r"designer|scientist|architect|administrator|representative|"
    r"executive|officer|supervisor|technician|strategist)\b",
    re.IGNORECASE,
)


class ResumeStructureAnalyzer:
    """
    Deterministic, LLM-free check of standard-section-header and
    contact-info presence over the already-extracted plain resume
    text — the parts of an ATS score that don't need a job
    description to evaluate.
    """

    def analyze(self, resume_text: str) -> StructureReport:

        has_email = bool(EMAIL_PATTERN.search(resume_text))
        has_phone = bool(PHONE_PATTERN.search(resume_text))

        found_sections = {
            section: False for section in SECTION_SYNONYMS
        }
        unrecognized_headers: list[str] = []
        non_empty_seen = 0
        seen_recognized_section = False

        for line in resume_text.splitlines():

            stripped = line.strip()

            if not stripped:
                continue

            non_empty_seen += 1
            is_first_line = non_empty_seen == 1

            if not self._is_candidate_header(stripped):
                continue

            normalized = self._normalize(stripped)
            matched_section = None

            for section, synonyms in SECTION_SYNONYMS.items():
                if normalized in synonyms:
                    matched_section = section
                    break

            if matched_section:
                found_sections[matched_section] = True
                seen_recognized_section = True
                continue

            if is_first_line:
                # Almost always the candidate's own name line —
                # never a section header, never worth flagging.
                continue

            # Once we're past the first recognized section, a
            # Title-Case candidate is far more likely to be an
            # entry title WITHIN that section (a job title, a
            # project name, a certification name — "Interim
            # Engineering Intern", "Personal Portfolio Site")
            # than an attempt at a new section header. ALL CAPS
            # remains a reliable "this is meant as a header"
            # signal even in that position, since resumes
            # conventionally reserve it for section dividers,
            # not entry titles.
            if seen_recognized_section and not stripped.isupper():
                continue

            if len(unrecognized_headers) < MAX_UNRECOGNIZED_HEADERS:
                unrecognized_headers.append(stripped)

        contact_hits = sum([has_email, has_phone])

        if contact_hits == 2:
            contact_score = 100.0
        elif contact_hits == 1:
            contact_score = 60.0
        else:
            contact_score = 0.0

        required_found = sum(
            found_sections[section]
            for section in REQUIRED_SECTIONS
        )

        section_score = (
            required_found / len(REQUIRED_SECTIONS)
        ) * 100.0

        completeness_score = (
            contact_score * 0.5 + section_score * 0.5
        )

        return StructureReport(
            has_email=has_email,
            has_phone=has_phone,
            found_sections=found_sections,
            unrecognized_headers=unrecognized_headers,
            contact_score=contact_score,
            section_score=section_score,
            completeness_score=completeness_score,
        )

    def _is_candidate_header(self, line: str) -> bool:

        if not line or len(line) > MAX_HEADER_LINE_LENGTH:
            return False

        if line.endswith((".", ",", ";")):
            return False

        if _BULLET_PREFIX_PATTERN.match(line):
            return False

        if any(char.isdigit() for char in line):
            return False

        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            return False

        if _DEGREE_PATTERN.search(line):
            return False

        if _JOB_TITLE_PATTERN.search(line):
            return False

        word_count = len(line.split())

        if word_count == 0 or word_count > MAX_HEADER_WORD_COUNT:
            return False

        # Headers are conventionally styled distinctly (Title Case
        # or ALL CAPS) — this is the main filter that keeps normal
        # sentence-case bullet fragments out of unrecognized_headers.
        return line.istitle() or (
            line.isupper() and any(char.isalpha() for char in line)
        )

    def _normalize(self, line: str) -> str:

        return re.sub(
            r"[^a-z0-9 ]", "", line.lower()
        ).strip()
