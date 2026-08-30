import re

import pymupdf

from app.schemas.resume_analysis import LayoutReport
from app.services.pdf_parser import (
    _get_background_color,
    _group_into_visual_lines,
    _is_visible_span,
)

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\-.\s()]{7,}\d)")

# A column is only "real" once it holds enough lines that it can't
# just be a stray label/date sitting beside a section header.
MIN_LINES_PER_COLUMN = 6

# Top/bottom slice of the page treated as the PDF header/footer
# band, where many ATS parsers never look.
HEADER_FOOTER_BAND_RATIO = 0.08

# A table has to cover a meaningful chunk of the page to count —
# a one-cell box around a skill rating icon shouldn't trigger this.
MIN_TABLE_AREA_RATIO = 0.05

# More than this many distinct visible font families is a real
# consistency problem, not normal body/heading/monospace variety.
MAX_FONT_FAMILIES = 3

# Font resource names carrying no real body-text signal — bullet
# glyphs and dingbats render through these, not prose.
_ICON_FONT_PREFIXES = ("symbol", "zapfdingbats", "wingdings")

# Below this margin (points; 18pt ≈ 0.25in) text is crowding the
# page edge. Bottom margin is intentionally excluded — unused
# trailing whitespace on a short resume isn't a formatting problem.
MIN_MARGIN_POINTS = 18.0

# A page is "image-heavy" once images cover most of it AND there's
# too little real text alongside them to have captured the content
# as selectable text instead.
IMAGE_AREA_RATIO_THRESHOLD = 0.5
IMAGE_HEAVY_MAX_TEXT_CHARS = 300

LAYOUT_SCORE_PENALTIES = {
    "multi_column": 40,
    "has_tables": 25,
    "was_ocr": 20,
    "image_heavy_content": 18,
    "content_in_header_footer": 15,
    "font_inconsistency": 10,
    "narrow_margins": 10,
    "too_many_pages": 5,
}


class ResumeLayoutAnalyzer:
    """
    Deterministic, LLM-free structural check of the ORIGINAL pdf
    (reopened from Resume.filepath) — layout/column/table/font
    information that extract_text_from_pdf() intentionally
    discards after flattening to plain text.
    """

    def analyze(self, pdf_path: str) -> LayoutReport:

        multi_column = False
        has_tables = False
        content_in_header_footer = False
        narrow_margins = False
        image_heavy_content = False
        low_text_pages = 0
        page_count = 0
        font_families: set[str] = set()

        try:
            document = pymupdf.open(pdf_path)
        except (FileNotFoundError, RuntimeError):
            # The original file can go missing independently of
            # anything the user did — e.g. an ephemeral hosting
            # filesystem that doesn't persist uploads across a
            # redeploy. Every other part of the pipeline only
            # needs Resume.extracted_text (already in the DB), so
            # this is the first path that ever reopens the file
            # post-upload. Degrade instead of 500ing: report the
            # layout check as unavailable rather than guessing.
            return LayoutReport(
                file_available=False,
                page_count=0,
                multi_column=False,
                has_tables=False,
                content_in_header_footer=False,
                was_ocr=False,
                font_inconsistency=False,
                narrow_margins=False,
                image_heavy_content=False,
                layout_score=0.0,
                parseability_gate_triggered=False,
                gate_reasons=[],
            )

        with document:

            page_count = document.page_count

            for page in document:

                background = _get_background_color(page)
                page_dict = page.get_text("dict", sort=True)

                visible_spans = [
                    span
                    for block in page_dict.get("blocks", [])
                    for line in block.get("lines", [])
                    for span in line.get("spans", [])
                    if span.get("text")
                    and _is_visible_span(span, page.rect, background)
                ]

                visual_lines = [
                    (text, bbox)
                    for text, bbox in _group_into_visual_lines(
                        visible_spans
                    )
                    if text.strip()
                ]

                if self._is_multi_column(
                    visible_spans, page.rect
                ):
                    multi_column = True

                if self._has_table(page):
                    has_tables = True

                page_text_length = len(
                    page.get_text("text").strip()
                )

                if page_text_length < 20:
                    low_text_pages += 1

                if self._contact_in_header_footer(
                    visual_lines, page.rect
                ):
                    content_in_header_footer = True

                font_families.update(
                    self._visible_font_families(visible_spans)
                )

                if self._has_narrow_margins(
                    visible_spans, page.rect
                ):
                    narrow_margins = True

                if self._is_image_heavy(
                    page, page_text_length
                ):
                    image_heavy_content = True

        was_ocr = (
            page_count > 0
            and (low_text_pages / page_count) > 0.5
        )

        font_inconsistency = len(font_families) > MAX_FONT_FAMILIES

        layout_score = 100.0
        gate_reasons: list[str] = []

        if multi_column:
            layout_score -= LAYOUT_SCORE_PENALTIES["multi_column"]
            gate_reasons.append(
                "Resume uses a multi-column layout, which most "
                "ATS parsers read left-to-right and top-to-bottom, "
                "scrambling column content."
            )

        if has_tables:
            layout_score -= LAYOUT_SCORE_PENALTIES["has_tables"]
            gate_reasons.append(
                "Resume contains tables — ATS parsers often drop "
                "or misread table content."
            )

        if content_in_header_footer:
            layout_score -= (
                LAYOUT_SCORE_PENALTIES["content_in_header_footer"]
            )
            gate_reasons.append(
                "Contact info appears in the page header/footer, "
                "which many ATS parsers ignore entirely."
            )

        if was_ocr:
            layout_score -= LAYOUT_SCORE_PENALTIES["was_ocr"]
            gate_reasons.append(
                "This PDF has no real text layer (looks scanned "
                "or image-based) — most ATS systems cannot read "
                "it at all."
            )

        if image_heavy_content:
            layout_score -= (
                LAYOUT_SCORE_PENALTIES["image_heavy_content"]
            )
            gate_reasons.append(
                "A large portion of this resume appears to be an "
                "embedded image rather than selectable text — ATS "
                "parsers can't read image content."
            )

        if font_inconsistency:
            layout_score -= (
                LAYOUT_SCORE_PENALTIES["font_inconsistency"]
            )

        if narrow_margins:
            layout_score -= (
                LAYOUT_SCORE_PENALTIES["narrow_margins"]
            )

        if page_count > 2:
            layout_score -= (
                LAYOUT_SCORE_PENALTIES["too_many_pages"]
            )

        layout_score = max(0.0, layout_score)

        parseability_gate_triggered = (
            multi_column
            or has_tables
            or was_ocr
            or image_heavy_content
        )

        return LayoutReport(
            page_count=page_count,
            multi_column=multi_column,
            has_tables=has_tables,
            content_in_header_footer=content_in_header_footer,
            was_ocr=was_ocr,
            font_inconsistency=font_inconsistency,
            narrow_margins=narrow_margins,
            image_heavy_content=image_heavy_content,
            layout_score=layout_score,
            parseability_gate_triggered=parseability_gate_triggered,
            gate_reasons=gate_reasons,
        )

    def _is_multi_column(
        self,
        visible_spans: list[dict],
        page_rect: pymupdf.Rect,
    ) -> bool:
        """
        Operates on raw, pre-merge spans rather than
        _group_into_visual_lines()'s output — that grouping
        merges any spans sharing a y-center into one line
        regardless of horizontal gap (by design, for stitching
        split text runs back into one sentence during plain-text
        extraction), which would silently erase the exact
        left/right x-gap this check depends on whenever two
        columns' rows happen to align vertically — a common case,
        not an edge case, in real 2-column resume templates.
        """

        if len(visible_spans) < MIN_LINES_PER_COLUMN * 2:
            return False

        # Column splits happen at all sorts of ratios in real
        # templates (a narrow 30% sidebar, an even 50/50 split,
        # ...) — a fixed left-third/right-third band misses most
        # of them. Instead, find the single largest gap between
        # consecutive span-start x-positions: a genuine second
        # column starts at a meaningfully different left margin
        # than the first, whereas a single-column resume's spans
        # (headers, bullets, dates) all start within a few points
        # of the same margin, leaving no large gap to find.
        sorted_bboxes = sorted(
            (
                pymupdf.Rect(span["bbox"])
                for span in visible_spans
            ),
            key=lambda bbox: bbox.x0,
        )

        x0_values = [bbox.x0 for bbox in sorted_bboxes]

        max_gap = 0.0
        split_index = None

        for index in range(1, len(x0_values)):

            gap = x0_values[index] - x0_values[index - 1]

            if gap > max_gap:
                max_gap = gap
                split_index = index

        min_gap_threshold = page_rect.width * 0.12

        if split_index is None or max_gap < min_gap_threshold:
            return False

        left_lines = sorted_bboxes[:split_index]
        right_lines = sorted_bboxes[split_index:]

        if (
            len(left_lines) < MIN_LINES_PER_COLUMN
            or len(right_lines) < MIN_LINES_PER_COLUMN
        ):
            return False

        # Confirm the two bands actually interleave vertically —
        # rules out a single narrow column with an unrelated
        # sidebar date/label stacked above or below it rather than
        # beside it.
        overlap_count = 0

        for left_bbox in left_lines:

            for right_bbox in right_lines:

                overlap = (
                    min(left_bbox.y1, right_bbox.y1)
                    - max(left_bbox.y0, right_bbox.y0)
                )

                if overlap > 0:
                    overlap_count += 1
                    break

        return overlap_count >= MIN_LINES_PER_COLUMN // 2

    def _has_table(self, page: pymupdf.Page) -> bool:

        try:
            tables = page.find_tables()
        except Exception:
            return False

        page_area = page.rect.width * page.rect.height

        if page_area <= 0:
            return False

        for table in tables.tables:

            bbox = pymupdf.Rect(table.bbox)

            if bbox.get_area() / page_area > MIN_TABLE_AREA_RATIO:
                return True

        return False

    def _visible_font_families(
        self,
        visible_spans: list[dict],
    ) -> set[str]:
        """
        Normalizes each span's font resource name down to a family
        (stripping the PDF subset prefix like "ABCDEE+" and style
        suffixes like ",Bold"/"-Italic") and drops icon/dingbat
        fonts, which render bullet glyphs rather than body text and
        would otherwise inflate the family count on a resume that
        visually uses only one or two real typefaces.
        """

        families: set[str] = set()

        for span in visible_spans:

            font_name = span.get("font", "")

            if "+" in font_name:
                font_name = font_name.split("+", 1)[1]

            family = re.split(r"[,-]", font_name)[0].strip().lower()

            if not family:
                continue

            if family.startswith(_ICON_FONT_PREFIXES):
                continue

            families.add(family)

        return families

    def _has_narrow_margins(
        self,
        visible_spans: list[dict],
        page_rect: pymupdf.Rect,
    ) -> bool:

        if not visible_spans:
            return False

        bboxes = [
            pymupdf.Rect(span["bbox"]) for span in visible_spans
        ]

        left_margin = min(bbox.x0 for bbox in bboxes)
        right_margin = page_rect.width - max(
            bbox.x1 for bbox in bboxes
        )
        top_margin = min(bbox.y0 for bbox in bboxes)

        return (
            left_margin < MIN_MARGIN_POINTS
            or right_margin < MIN_MARGIN_POINTS
            or top_margin < MIN_MARGIN_POINTS
        )

    def _is_image_heavy(
        self,
        page: pymupdf.Page,
        page_text_length: int,
    ) -> bool:

        if page_text_length >= IMAGE_HEAVY_MAX_TEXT_CHARS:
            return False

        page_area = page.rect.width * page.rect.height

        if page_area <= 0:
            return False

        try:
            image_info = page.get_image_info()
        except Exception:
            return False

        image_area = sum(
            pymupdf.Rect(info["bbox"]).get_area()
            for info in image_info
        )

        return (image_area / page_area) > IMAGE_AREA_RATIO_THRESHOLD

    def _contact_in_header_footer(
        self,
        visual_lines: list[tuple[str, pymupdf.Rect]],
        page_rect: pymupdf.Rect,
    ) -> bool:

        height = page_rect.height
        top_band = height * HEADER_FOOTER_BAND_RATIO
        bottom_band = height * (1 - HEADER_FOOTER_BAND_RATIO)

        for text, bbox in visual_lines:

            in_band = (
                bbox.y1 <= top_band or bbox.y0 >= bottom_band
            )

            if in_band and (
                EMAIL_PATTERN.search(text)
                or PHONE_PATTERN.search(text)
            ):
                return True

        return False
