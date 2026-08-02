"""PDF exporter using fpdf2 for v3.0."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, cast

from fpdf import FPDF
from fpdf.outline import OutlineSection
from fpdf.syntax import DestinationXYZ

from mdutil.export.base import Exporter
from mdutil.parser import _parse_inline

# ---------------------------------------------------------------------------
# Unicode-capable TTF font paths (fallback from core fonts for non-Latin chars)
# ---------------------------------------------------------------------------
_UNICODE_FONTS: dict[str, str] = {}
import os

for _style, _path in (
    ("regular", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ("bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("italic", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
    ("bold_italic", "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
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


class _InlineHTMLParser(HTMLParser):
    """Convert parser-produced inline HTML into renderable PDF text segments."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.segments: list[dict[str, Any]] = []
        self._strong = 0
        self._emphasis = 0
        self._code = 0
        self._links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "strong":
            self._strong += 1
        elif tag == "em":
            self._emphasis += 1
        elif tag == "code":
            self._code += 1
        elif tag == "a":
            href = dict(attrs).get("href") or ""
            self._links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "strong" and self._strong:
            self._strong -= 1
        elif tag == "em" and self._emphasis:
            self._emphasis -= 1
        elif tag == "code" and self._code:
            self._code -= 1
        elif tag == "a" and self._links:
            self._links.pop()

    def handle_data(self, data: str) -> None:
        if not data:
            return
        self.segments.append(
            {
                "text": data,
                "strong": bool(self._strong),
                "emphasis": bool(self._emphasis),
                "code": bool(self._code),
                "href": self._links[-1] if self._links else "",
            }
        )


class PdfExporter(Exporter):
    """Export Markdown to PDF using fpdf2."""

    FONT_SIZE: float = 10
    HEADING_SCALE: float = 0.55
    MARGIN: float = 20

    _DOCUMENT_HEADER_LINE_RE = re.compile(
        r"^\*\*(?:author|version|last[-‑]updated|license|repository):\*\*\s+",
        re.IGNORECASE,
    )

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
        if "italic" in _UNICODE_FONTS:
            pdf.add_font("UnicodeSans", "I", _UNICODE_FONTS["italic"])  # type: ignore[call-arg]
        if "bold_italic" in _UNICODE_FONTS:
            pdf.add_font("UnicodeSans", "BI", _UNICODE_FONTS["bold_italic"])  # type: ignore[call-arg]
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

    def _font_style_for_segment(self, segment: dict[str, Any]) -> str:
        """Return fpdf font style for a parsed inline segment."""
        style = ""
        if segment.get("strong"):
            style += "B"
        if segment.get("emphasis"):
            style += "I"
        if segment.get("href"):
            style += "U"
        return style

    def _parse_inline_html(self, html: str) -> list[dict[str, Any]]:
        parser = _InlineHTMLParser()
        parser.feed(html)
        parser.close()
        return parser.segments

    def _plain_text_from_inline_html(self, html: str) -> str:
        return "".join(segment["text"] for segment in self._parse_inline_html(html))

    def _render_inline_html(self, pdf: FPDF, html: str, *, line_height: float = 5) -> None:
        """Render parser-produced inline HTML with PDF fonts and link annotations."""
        for segment in self._parse_inline_html(html):
            text = segment["text"]
            if not text:
                continue
            if segment.get("code"):
                pdf.set_font(self._font_for("mono"), size=9)
            else:
                pdf.set_font(
                    self._font_for("regular"),
                    style=self._font_style_for_segment(segment),
                    size=self.FONT_SIZE,
                )
            if segment.get("href"):
                pdf.set_text_color(0, 0, 180)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.write(line_height, text, link=segment.get("href") or "")
        pdf.set_text_color(0, 0, 0)

    def _is_document_header_metadata(self, token: dict) -> bool:
        """Return True when a paragraph is the spec-style document metadata header."""
        source_lines = token.get("source_lines", [])
        content_lines = token.get("content_lines", [])
        if len(source_lines) < 2 or len(source_lines) != len(content_lines):
            return False
        return all(
            isinstance(line, str) and self._DOCUMENT_HEADER_LINE_RE.match(line)
            for line in source_lines
        )

    def _pdf_align(self, align: str | None) -> str:
        return {"left": "L", "center": "C", "right": "R"}.get(str(align or "").lower(), "L")

    def render(self, tokens: list[dict], theme: dict, options: dict) -> bytes:
        """Render tokens to PDF bytes."""
        self._options = options  # Store options for use in code block rendering
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
        """Render a heading token with inline formatting."""
        level = token.get("level", 1)
        text = token.get("text", "")

        sizes = {1: 24, 2: 20, 3: 16, 4: 14, 5: 12, 6: 10}
        sizes = {level: size * self.HEADING_SCALE for level, size in sizes.items()}
        font_size = sizes.get(level, self.FONT_SIZE)

        # Parse inline formatting (backticks → code, bold, italic, links)
        inline = _parse_inline(text)
        inline_segments = self._parse_inline_html(inline["content"])

        # Render with heading-appropriate font size
        pdf.set_font(self._font_for("bold"), size=font_size)
        for segment in inline_segments:
            if not segment["text"]:
                continue
            if segment.get("code"):
                pdf.set_font(self._font_for("mono"), size=9)
            else:
                style = ""
                if segment.get("strong"):
                    style += "B"
                if segment.get("emphasis"):
                    style += "I"
                pdf.set_font(
                    self._font_for("regular"),
                    style=style,
                    size=font_size,
                )
            if segment.get("href"):
                pdf.set_text_color(0, 0, 180)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.write(10, segment["text"], link=segment.get("href") or "")

        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

        # Track heading for PDF outline (h1-h3)
        if level <= 3:
            self._heading_sections.append((text, level, pdf.page))

    def _render_paragraph(self, pdf: FPDF, token: dict) -> None:
        """Render a paragraph token."""
        if self._is_document_header_metadata(token):
            pdf.set_x(pdf.l_margin)
            for line in token["content_lines"]:
                self._render_inline_html(pdf, line)
                pdf.ln(5)
            pdf.ln(3)
            return

        content = token.get("content", "")
        if content:
            pdf.set_x(pdf.l_margin)
            self._render_inline_html(pdf, content)
            pdf.ln(8)
            return

        text = token.get("text", "")
        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.multi_cell(0, 5, text, align="L")
        pdf.ln(3)

    def _render_code_block(self, pdf: FPDF, token: dict) -> None:
        """Render a code block with syntax highlighting and preserved indentation."""
        content = token.get("content", "")
        language = token.get("language", "")
        syntax_theme = self._options.get("syntax_theme", "default")
        theme = self._options.get("theme", {})
        
        from mdutil.syntax_highlighter import highlight_code_pdf
        segments = highlight_code_pdf(content, language, theme, syntax_theme)
        
        pdf.set_font(self._font_for("mono"), size=9)
        pdf.set_fill_color(240, 240, 240)
        
        # Group segments by line and render each line together
        # This preserves indentation: leading whitespace and content are on the same line
        current_line_segments: list[dict[str, Any]] = []
        for segment in segments:
            text = segment["text"]
            rgb = segment.get("rgb")
            
            if "\n" in text:
                # Split at newlines — each part before a newline is its own line
                parts = text.split("\n")
                for i, part in enumerate(parts):
                    if part:
                        current_line_segments.append({"text": part, "rgb": rgb})
                    if i < len(parts) - 1:
                        # Render the accumulated line so far
                        self._render_code_line(pdf, current_line_segments)
                        current_line_segments = []
                continue
            
            current_line_segments.append(segment)
        
        # Render last line
        if current_line_segments:
            self._render_code_line(pdf, current_line_segments)
        
        pdf.ln(5)

    def _render_code_line(self, pdf: FPDF, line_segments: list[dict[str, Any]]) -> None:
        """Render a single line of code with syntax highlighting.

        Segments within a line are placed sequentially using tracked
        absolute X positioning so indentation is preserved.
        """
        start_x = pdf.get_x()
        current_x = start_x

        for i, segment in enumerate(line_segments):
            rgb = segment.get("rgb")
            if rgb:
                pdf.set_text_color(rgb["r"], rgb["g"], rgb["b"])
            else:
                pdf.set_text_color(0, 0, 0)

            text = segment["text"]
            width = pdf.get_string_width(text)

            # Place the cell at the current X position
            pdf.set_x(current_x)
            pdf.cell(
                width,
                5,
                text,
                new_x="LMARGIN",
                new_y="LAST",
                fill=True,
            )
            current_x += width

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
        table_width = pdf.w - pdf.l_margin - pdf.r_margin
        col_width = table_width / col_count
        line_height = 5
        padding = 1

        def cell_text(value: Any) -> str:
            parsed = _parse_inline(str(value))
            return self._plain_text_from_inline_html(parsed["content"])

        def cell_lines(value: Any) -> list[str]:
            text = cell_text(value)
            lines = cast(
                list[str],
                pdf.multi_cell(
                    col_width - 2 * padding,
                    line_height,
                    text,
                    dry_run=True,
                    output="LINES",
                ),
            )
            return lines or [""]

        def render_row(values: list[Any], *, bold: bool = False, fill: bool = False) -> None:
            row_lines = [cell_lines(value) for value in values]
            row_height = max(line_height * len(lines) + 2 * padding for lines in row_lines)
            if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
                pdf.add_page()
            x = pdf.l_margin
            y = pdf.get_y()
            for i, value in enumerate(values):
                align = self._pdf_align(alignments[i] if i < len(alignments) else None)
                pdf.rect(x, y, col_width, row_height, style="DF" if fill else "D")
                pdf.set_xy(x + padding, y + padding)
                pdf.multi_cell(
                    col_width - 2 * padding,
                    line_height,
                    cell_text(value),
                    border=0,
                    align=align,
                )
                x += col_width
                pdf.set_xy(x, y)
            pdf.set_xy(pdf.l_margin, y + row_height)

        # Header
        pdf.set_font(self._font_for("bold"), size=self.FONT_SIZE)
        pdf.set_fill_color(230, 230, 230)
        render_row(headers, bold=True, fill=True)

        # Rows with alternating fill
        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        for row_idx, row in enumerate(rows):
            do_fill = row_idx % 2 == 1
            if do_fill:
                pdf.set_fill_color(245, 245, 245)
            padded_row = list(row) + [""] * max(0, col_count - len(row))
            render_row(padded_row[:col_count], fill=do_fill)

        pdf.ln(5)

    def _render_blockquote(self, pdf: FPDF, token: dict) -> None:
        """Render a blockquote."""
        content = token.get("content", "")
        text_lines = content.split("\n")

        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.set_text_color(100, 100, 100)

        start_y = pdf.get_y()
        line_x = pdf.l_margin + 2
        text_x = pdf.l_margin + 6

        for line in text_lines:
            if line.startswith(">"):
                line = line.lstrip(">").strip()
            if not line:
                pdf.ln(3)
                continue
            effective_w = pdf.w - text_x - pdf.r_margin
            if effective_w < 10:
                effective_w = 50
            pdf.set_x(text_x)
            inline = _parse_inline(line)
            self._render_inline_html(pdf, inline["content"])
            pdf.ln(5)

        end_y = pdf.get_y()
        pdf.set_draw_color(160, 160, 160)
        pdf.line(line_x, start_y, line_x, end_y)

        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    def _render_list(self, pdf: FPDF, token: dict) -> None:
        """Render an ordered or unordered list."""
        parsed_items = token.get("parsed_items", [])
        ordered = token.get("ordered", False)
        indent = 5

        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)

        # Save current x position for list indentation
        left_x = pdf.l_margin
        pdf.set_x(left_x + indent)

        if parsed_items:
            items_to_render = parsed_items
        else:
            # Fallback for tokens without parsed_items (tests, legacy)
            items_to_render = token.get("items", [])

        for i, item in enumerate(items_to_render, 1):
            if ordered:
                prefix = f"{i}. "
            else:
                prefix = "- "

            if isinstance(item, dict):
                content = item.get("content", item.get("text", ""))
            else:
                content = str(item)
            # Strip HTML inline tags for PDF (fpdf2 can't render HTML)
            content = re.sub(r"</?(?:strong|em|code|a[^>]*)>", "", content)

            pdf.set_x(left_x + indent)
            effective_w = pdf.w - left_x - pdf.r_margin - indent
            if effective_w < 10:
                effective_w = 50  # fallback for very narrow layouts
            pdf.multi_cell(effective_w, 5, f"{prefix}{content}", align="L")

        pdf.ln(3)
