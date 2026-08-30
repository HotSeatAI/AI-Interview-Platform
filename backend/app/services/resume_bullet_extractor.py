import re

from app.schemas.resume_analysis import ResumeBullet
from app.services.resume_structure_analyzer import SECTION_SYNONYMS

_BULLET_PREFIX_PATTERN = re.compile(r"^\s*([•▪*\-]|\d+[.)])\s+")

# A leading digit run immediately followed by "%" or "+" is a
# metric fragment ("30%,", "100%", "10,000+") — never a year-header
# line, which is always followed by a space/dash ("2023 - Present").
_METRIC_CONTINUATION_PATTERN = re.compile(r"^\d[\d,.]*[%+]")

_BULLET_SECTIONS = ("experience", "skills")
_MIN_FALLBACK_WORD_COUNT = 5


def _normalize(line: str) -> str:

    return re.sub(r"[^a-z0-9 ]", "", line.lower()).strip()


def _matched_section(line: str) -> str | None:

    normalized = _normalize(line)

    for section, synonyms in SECTION_SYNONYMS.items():
        if normalized in synonyms:
            return section

    return None


def extract_bullets_from_text(
    resume_text: str,
) -> list[tuple[ResumeBullet, str]]:
    """
    Zero-LLM fallback bullet extraction, used by the standalone
    ATS scoring path when no Gemini-structured ResumeProfile is
    already cached for this resume. Groups bullet-marker lines
    under the nearest preceding recognized section header.

    Deliberately produces bullets with empty metrics/technologies
    (regex can't reliably pull those out) — this loses some of the
    partial-credit signal ResumeOptimizer's quantification/
    specificity scoring would otherwise get from a Gemini-
    structured bullet, an accepted tradeoff for a free, instant
    fallback.
    """

    lines = resume_text.splitlines()

    has_bullet_markers = any(
        _BULLET_PREFIX_PATTERN.match(line.strip())
        for line in lines
        if line.strip()
    )

    results: list[tuple[ResumeBullet, str]] = []
    current_section = "other"

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        section_hit = _matched_section(line)

        if section_hit:
            current_section = section_hit
            continue

        is_bullet_line = bool(_BULLET_PREFIX_PATTERN.match(line))

        if is_bullet_line:
            text = _BULLET_PREFIX_PATTERN.sub("", line).strip()

            if not text:
                continue

            results.append(
                (
                    ResumeBullet(
                        text=text,
                        action_verbs=[],
                        technologies=[],
                        metrics=[],
                        achievements=[],
                        jd_relevant_claims=[],
                    ),
                    current_section,
                )
            )
            continue

        looks_like_continuation = (
            line[0].isalpha() and line[0].islower()
        ) or bool(_METRIC_CONTINUATION_PATTERN.match(line))

        if (
            has_bullet_markers
            and results
            and results[-1][1] == current_section
            and looks_like_continuation
        ):
            # Plain-text extraction discards PDF geometry, so a
            # wrapped bullet's second physical line arrives with no
            # marker of its own. Line-wraps overwhelmingly land
            # mid-clause on a lowercase function word (a/using/via)
            # or a metric fragment (30%, 10,000+), while a genuine
            # new record (job title, company, date) starts uppercase
            # or with a bare year — so this merges only the former,
            # leaving the latter dropped as before.
            previous_bullet, previous_section = results[-1]

            results[-1] = (
                previous_bullet.model_copy(
                    update={
                        "text": (
                            f"{previous_bullet.text} {line}"
                        ),
                    }
                ),
                previous_section,
            )
            continue

        if (
            not has_bullet_markers
            and current_section in _BULLET_SECTIONS
            and len(line.split()) >= _MIN_FALLBACK_WORD_COUNT
        ):
            results.append(
                (
                    ResumeBullet(
                        text=line,
                        action_verbs=[],
                        technologies=[],
                        metrics=[],
                        achievements=[],
                        jd_relevant_claims=[],
                    ),
                    current_section,
                )
            )

    return results
