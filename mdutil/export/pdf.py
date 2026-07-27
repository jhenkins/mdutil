"""PDF exporter using fpdf2 for v3.0."""

from __future__ import annotations

import re
from typing import Any

from fpdf import FPDF
from fpdf.outline import OutlineSection
from fpdf.syntax import DestinationXYZ

from mdutil.export.base import Exporter

# ---------------------------------------------------------------------------
# Unicode-capable TTF font paths (fallback from core fonts for non-Latin chars)
# ---------------------------------------------------------------------------
_UNICODE_FONTS: dict[str, str] = {}
import os

for _style, _path in (
    ("regular", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ("bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("mono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
):
    if os.path.exists(_path):
        _UNICODE_FONTS[_style] = _path


# fpdf2 paper size constants
PAPER_SIZES: dict[str, tuple[float, float]] = {
    "A4": (210, 297),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
}

ORIENTATIONS: dict[str, str] = {
    "portrait": "P",
    "landscape": "L",
}


class PdfExporter(Exporter):
    """Export Markdown to PDF using fpdf2."""

    FONT_SIZE: float = 10
    MARGIN: float = 20

    # Built-in fpdf2 fonts (Latin-1 only, used when no TTF fonts available)
    FONT_REGULAR: str = "Helvetica"
    FONT_BOLD: str = "Helvetica"
    FONT_ITALIC: str = "Helvetica"
    FONT_MONO: str = "Courier"

    def supports(self, format: str) -> bool:
        return format.lower() == "pdf"

    def _register_unicode_fonts(self, pdf: FPDF) -> None:
        """Register DejaVu TTF fonts for Unicode support if available."""
        if not _UNICODE_FONTS:
            return  # no unicode fonts found, fall back to core fonts

        pdf.add_font("UnicodeSans", "", _UNICODE_FONTS["regular"])  # type: ignore[call-arg]
        pdf.add_font("UnicodeSans", "B", _UNICODE_FONTS["bold"])  # type: ignore[call-arg]
        # Use DejaVu Sans Mono for monospace
        mono_path = _UNICODE_FONTS.get("mono", _UNICODE_FONTS["regular"])
        pdf.add_font("UnicodeMono", "", mono_path)  # type: ignore[call-arg]

        self._use_unicode = True

    def _font_for(self, style: str = "regular") -> str:
        """Return Unicode font family when registered, else built-in font name."""
        if self._use_unicode:
            if style == "mono":
                return "UnicodeMono"
            return "UnicodeSans"
        if style == "bold":
            return self.FONT_BOLD
        if style == "mono":
            return self.FONT_MONO
        return self.FONT_REGULAR

    def render(self, tokens: list[dict], theme: dict, options: dict) -> bytes:
        """Render tokens to PDF bytes."""
        paper_size = options.get("pdf_paper_size", "A4")
        orientation = options.get("pdf_orientation", "portrait")

        pdf = FPDF(
            orientation=ORIENTATIONS.get(orientation, "P"),
            unit="mm",
            format=PAPER_SIZES.get(paper_size, PAPER_SIZES["A4"]),
        )

        self._use_unicode = False
        self._register_unicode_fonts(pdf)

        margin_top = options.get("pdf_margin_top", self.MARGIN)
        margin_bottom = options.get("pdf_margin_bottom", self.MARGIN)
        margin_left = options.get("pdf_margin_left", self.MARGIN)
        margin_right = options.get("pdf_margin_right", self.MARGIN)

        pdf.set_auto_page_break(auto=True, margin=margin_bottom)
        pdf.set_margins(left=margin_left, top=margin_top, right=margin_right)
        pdf.add_page()

        # Track headings for PDF outlines/bookmarks
        self._heading_sections: list[tuple[str, int, int]] = []  # (title, level, page_number)

        # Store page header/footer text
        self._header_text = options.get("pdf_header", "")
        self._footer_text = options.get("pdf_footer", "")

        if self._header_text or self._footer_text:
            if self._header_text:
                def header_fn(pdf=pdf, text=self._header_text):
                    pdf.set_font(self.FONT_REGULAR, size=8)
                    pdf.set_text_color(128, 128, 128)
                    pdf.cell(0, 5, text, align="C", new_x="LMARGIN", new_y="NEXT")
                    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                    pdf.ln(3)

                pdf.header = header_fn  # type: ignore[attr-defined]

            if self._footer_text:

                def footer_fn(pdf=pdf, text=self._footer_text):
                    pdf.set_y(-15)
                    pdf.set_font(self.FONT_REGULAR, size=8)
                    pdf.set_text_color(128, 128, 128)
                    pdf.cell(0, 10, text, align="C")

                pdf.footer = footer_fn  # type: ignore[attr-defined]

        self._render_tokens(pdf, tokens)

        # Build PDF outline/bookmarks from tracked heading sections
        bookmarks_enabled = options.get("pdf_bookmarks", True)
        if bookmarks_enabled and self._heading_sections:
            outlines = []
            for title, level, page_num in self._heading_sections:
                outlines.append(
                    OutlineSection(
                        name=title,
                        level=level,
                        page_number=page_num,
                        dest=DestinationXYZ(
                            page=page_num,
                            top=pdf.t_margin * pdf.k,
                        ),
                    )
                )
            pdf._outline = outlines  # type: ignore[attr-defined]

        return bytes(pdf.output())

    def _render_tokens(self, pdf: FPDF, tokens: list[dict]) -> None:
        """Render a list of tokens to PDF."""
        for token in tokens:
            token_type = token.get("type")

            if token_type == "blank":
                pdf.ln(5)
                continue

            if token_type == "heading":
                self._render_heading(pdf, token)
                continue

            if token_type == "paragraph":
                self._render_paragraph(pdf, token)
                continue

            if token_type == "code":
                self._render_code_block(pdf, token)
                continue

            if token_type == "horizontal_rule":
                self._render_horizontal_rule(pdf, token)
                continue

            if token_type == "table":
                self._render_table(pdf, token)
                continue

            if token_type == "blockquote":
                self._render_blockquote(pdf, token)
                continue

            if token_type == "list":
                self._render_list(pdf, token)
                continue

    def _render_heading(self, pdf: FPDF, token: dict) -> None:
        """Render a heading token."""
        level = token.get("level", 1)
        text = token.get("text", "")

        sizes = {1: 24, 2: 20, 3: 16, 4: 14, 5: 12, 6: 10}
        font_size = sizes.get(level, self.FONT_SIZE)

        pdf.set_font(self._font_for("bold"), size=font_size)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Track heading for PDF outline (h1-h3)
        if level <= 3:
            self._heading_sections.append((text, level, pdf.page))

    def _render_paragraph(self, pdf: FPDF, token: dict) -> None:
        """Render a paragraph token."""
        text = token.get("content", "") or token.get("text", "")
        # Strip HTML inline tags that the parser produces in content
        text = re.sub(r"</?(?:strong|em|code|a[^>]*)>", "", text)

        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.multi_cell(0, 5, text, align="L")
        pdf.ln(3)

    def _render_code_block(self, pdf: FPDF, token: dict) -> None:
        """Render a code block with background."""
        content = token.get("content", "")
        lines = content.split("\n")

        pdf.set_font(self._font_for("mono"), size=9)
        pdf.set_fill_color(240, 240, 240)

        for line in lines:
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT", fill=True)

        pdf.ln(5)

    def _render_horizontal_rule(self, pdf: FPDF, token: dict) -> None:
        """Render a horizontal rule."""
        y = pdf.get_y()
        x = pdf.get_x()

        pdf.set_draw_color(0, 0, 0)
        pdf.line(x, y, pdf.w - self.MARGIN, y)
        pdf.ln(8)

    def _render_table(self, pdf: FPDF, token: dict) -> None:
        """Render a table with borders."""
        headers = token.get("headers", [])
        rows = token.get("rows", [])
        alignments = token.get("alignments", [])

        if not headers:
            return

        col_count = len(headers)
        col_width = (pdf.w - 2 * self.MARGIN) / col_count

        # Header
        pdf.set_font(self._font_for("bold"), size=self.FONT_SIZE)
        pdf.set_fill_color(230, 230, 230)

        for i, header in enumerate(headers):
            align = alignments[i] if i < len(alignments) and alignments[i] else "L"
            pdf.cell(col_width, 8, header, border=1, fill=True, align=align)
        pdf.ln()

        # Rows with alternating fill
        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        for row_idx, row in enumerate(rows):
            do_fill = row_idx % 2 == 1
            if do_fill:
                pdf.set_fill_color(245, 245, 245)
            for i, cell in enumerate(row):
                align = alignments[i] if i < len(alignments) and alignments[i] else "L"
                pdf.cell(col_width, 6, cell, border=1, align=align, fill=do_fill)
            pdf.ln()

        pdf.ln(5)

    def _render_blockquote(self, pdf: FPDF, token: dict) -> None:
        """Render a blockquote."""
        content = token.get("content", "")
        text_lines = content.split("\n")

        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.set_text_color(100, 100, 100)

        for line in text_lines:
            if line.startswith(">"):
                line = line.lstrip(">").strip()
            if not line:
                pdf.ln(3)
                continue
            effective_w = pdf.w - pdf.l_margin - pdf.r_margin
            if effective_w < 10:
                effective_w = 50
            pdf.multi_cell(effective_w, 5, f"> {line}", align="L")

        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    def _render_list(self, pdf: FPDF, token: dict) -> None:
        """Render an ordered or unordered list."""
        items = token.get("items", [])
        ordered = token.get("ordered", False)
        indent = 5

        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)

        # Save current x position for list indentation
        left_x = pdf.l_margin
        pdf.set_x(left_x + indent)

        for i, item in enumerate(items, 1):
            if ordered:
                prefix = f"{i}. "
            else:
                prefix = "- "

            pdf.set_x(left_x + indent)
            effective_w = pdf.w - left_x - pdf.r_margin - indent
            if effective_w < 10:
                effective_w = 50  # fallback for very narrow layouts
            pdf.multi_cell(effective_w, 5, f"{prefix}{item}", align="L")

        pdf.ln(3)
