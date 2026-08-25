import pymupdf
from google.genai import types

from app.services.api_key_manager import api_key_manager

RESUME_OCR_PROMPT = """
You are extracting the full text of a resume from a PDF that has no usable text layer (it is scanned or image-based).

Read every page carefully.

Extract the COMPLETE visible content, preserving structure such as:
- Name and contact details
- Summary / objective
- Work experience (titles, companies, dates, bullet points)
- Education
- Skills
- Certifications
- Projects
- Links (portfolio, LinkedIn, GitHub, etc.)

Do NOT summarize.

Do NOT invent missing information.

Do NOT add information that is not visible.

Return only the extracted resume text.
"""


def extract_text_via_gemini_ocr(pdf_bytes: bytes) -> str:

    response = api_key_manager.generate_content(
        contents=[
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf",
            ),
            RESUME_OCR_PROMPT,
        ],
        purpose="resume_pdf_ocr",
    )

    text = (response.text or "").strip()

    if not text:
        raise ValueError(
            "Could not extract text from the resume."
        )

    return text


def _get_background_color(page: pymupdf.Page) -> tuple[int, int, int]:
    """
    Estimates the page's background color by sampling its four
    corners — resume content essentially never starts exactly at
    the page edge, so this is a cheap, reliable stand-in for a
    full background-detection pass.
    """

    pixmap = page.get_pixmap()

    width, height = pixmap.width, pixmap.height

    margin = 5

    sample_points = [
        (margin, margin),
        (max(width - margin - 1, 0), margin),
        (margin, max(height - margin - 1, 0)),
        (max(width - margin - 1, 0), max(height - margin - 1, 0)),
    ]

    samples = [
        pixmap.pixel(x, y)[:3]
        for x, y in sample_points
        if 0 <= x < width and 0 <= y < height
    ]

    if not samples:
        return (255, 255, 255)

    return (
        sum(sample[0] for sample in samples) // len(samples),
        sum(sample[1] for sample in samples) // len(samples),
        sum(sample[2] for sample in samples) // len(samples),
    )


def _color_distance(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> float:

    return sum(
        (a - b) ** 2
        for a, b in zip(first, second)
    ) ** 0.5


def _is_visible_span(
    span: dict,
    page_rect: pymupdf.Rect,
    background: tuple[int, int, int],
) -> bool:
    """
    Filters out text that a human reading the rendered PDF would
    never actually see, so it can't reach the resume/JD
    structuring prompts: near-zero-size text, text positioned
    entirely off the visible page, and text colored to match
    (or nearly match) the page background — the classic
    hidden-text prompt-injection technique.
    """

    if span.get("size", 0) < 1:
        return False

    bbox = pymupdf.Rect(span["bbox"])

    if not bbox.intersects(page_rect):
        return False

    color_int = span.get("color", 0)

    text_color = (
        (color_int >> 16) & 255,
        (color_int >> 8) & 255,
        color_int & 255,
    )

    if _color_distance(text_color, background) < 12:
        return False

    return True


def _group_into_visual_lines(
    spans: list[dict],
) -> list[tuple[str, pymupdf.Rect]]:
    """
    Some PDF templates (common in resume builders) store each
    differently-formatted run of text — e.g. a bold keyword
    inline within a sentence — as its OWN separate PyMuPDF
    "line" object, even when several of them sit on the same
    printed line. Treating each dict-level "line" as one printed
    line (as PyMuPDF's own block/line nesting suggests) shreds
    a single sentence into fragments.

    This groups spans by vertical position instead — spans
    whose y-centers fall within one another's height tolerance
    are the same printed line — then sorts each group left to
    right, mirroring the reading-order reconstruction
    page.get_text("text", sort=True) already does internally,
    while still allowing per-span visibility filtering.

    Returns (text, bbox) pairs — the bbox is the union of every
    span's box in that line, used to match hyperlink annotations
    back to the visible text they sit under.
    """

    if not spans:
        return []

    ordered = sorted(
        spans,
        key=lambda span: (
            (span["bbox"][1] + span["bbox"][3]) / 2,
            span["bbox"][0],
        ),
    )

    lines: list[list[dict]] = []

    for span in ordered:

        y_center = (span["bbox"][1] + span["bbox"][3]) / 2
        tolerance = max(span["bbox"][3] - span["bbox"][1], 1) / 2

        if lines:

            last_line = lines[-1]

            last_y_center = sum(
                (item["bbox"][1] + item["bbox"][3]) / 2
                for item in last_line
            ) / len(last_line)

            if abs(y_center - last_y_center) <= tolerance:
                last_line.append(span)
                continue

        lines.append([span])

    results: list[tuple[str, pymupdf.Rect]] = []

    for line in lines:

        ordered_spans = sorted(
            line,
            key=lambda span: span["bbox"][0],
        )

        text = "".join(
            span["text"]
            for span in ordered_spans
        )

        bbox = pymupdf.Rect(ordered_spans[0]["bbox"])

        for span in ordered_spans[1:]:
            bbox |= pymupdf.Rect(span["bbox"])

        results.append((text, bbox))

    return results


def _attach_links(
    lines: list[tuple[str, pymupdf.Rect]],
    links: list[dict],
) -> list[str]:
    """
    Hyperlink URLs in a PDF are stored as separate clickable-
    area annotations, not as part of the visible text — a
    resume's "Github" label and the actual github.com URL
    behind it are two unrelated pieces of data as far as plain
    text extraction is concerned. Without this, every link on a
    resume (portfolio, GitHub, LinkedIn, live project links)
    is invisible to the LLM structuring step downstream.

    Each link is matched to whichever visible line's bounding
    box it overlaps, and the URL is appended inline next to that
    line's text. A link that doesn't overlap any visible text
    (e.g. an icon-only link) is still surfaced as a standalone
    line rather than silently dropped.
    """

    if not links:
        return [text for text, _ in lines]

    results = [text for text, _ in lines]
    attached_uris: set[str] = set()

    for link in links:

        uri = link.get("uri")

        if not uri:
            continue

        link_rect = pymupdf.Rect(link["from"])

        best_index = None
        best_overlap = 0.0

        for index, (_, bbox) in enumerate(lines):

            intersection = bbox & link_rect

            if intersection.is_empty:
                continue

            overlap = intersection.get_area()

            if overlap > best_overlap:
                best_overlap = overlap
                best_index = index

        if best_index is not None:
            results[best_index] += f" ({uri})"
            attached_uris.add(uri)
        elif uri not in attached_uris:
            results.append(f"[Link: {uri}]")
            attached_uris.add(uri)

    return results


def extract_text_from_pdf(file_path: str) -> str:

    extracted_text = ""

    with pymupdf.open(file_path) as document:

        for page in document:

            background = _get_background_color(page)

            page_dict = page.get_text("dict", sort=True)

            visible_spans = [
                span
                for block in page_dict.get("blocks", [])
                for line in block.get("lines", [])
                for span in line.get("spans", [])
                if span.get("text")
                and _is_visible_span(
                    span,
                    page.rect,
                    background,
                )
            ]

            visual_lines = [
                (text, bbox)
                for text, bbox in _group_into_visual_lines(
                    visible_spans
                )
                if text.strip()
            ]

            page_lines = _attach_links(
                visual_lines,
                page.get_links(),
            )

            if page_lines:
                extracted_text += "\n".join(page_lines) + "\n"

    return extracted_text
