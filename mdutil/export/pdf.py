"""PDF exporter using fpdf2 for v3.0."""

from __future__ import annotations

import logging
import re
import sys
import html.parser
from io import BytesIO
from typing import Any, cast

from fpdf import FPDF
from fpdf.outline import OutlineSection
from fpdf.syntax import DestinationXYZ

from mdutil.export.base import Exporter
from PIL import Image as PILImage

from mdutil.export.svg_to_image import (
    MermanBinaryNotFoundError,
    MermanRenderError,
    SvgToImageError,
)
from mdutil.parser import _parse_inline

_logger = logging.getLogger("mdutil.export.pdf")


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


class _InlineHTMLParser(html.parser.HTMLParser):
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
            # Strip non-ASCII characters for PDF rendering
            text = self._strip_non_ascii(text)
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
        _logger.debug("Starting PDF export with %d tokens", len(tokens))
        self._options = options  # Store options for use in code block rendering
        paper_size = options.get("pdf_paper_size", "A4")
        orientation = options.get("pdf_orientation", "portrait")

        _logger.debug("Using paper size %s, orientation %s", paper_size, orientation)

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
        # Collect mermaid diagrams and render them upfront (batched).
        mermaid_diagrams: list[tuple[dict, int]] = []
        rendered_svgs: dict[int, bytes] = {}
        for i, token in enumerate(tokens):
            if token.get("type") == "mermaid":
                mermaid_diagrams.append((token, i))

        if mermaid_diagrams:
            mermaid_enabled = self._options.get("mermaid", True)
            if mermaid_enabled:
                # Clip wide diagrams to page width before rasterization.
                # Convert mm → CSS pixels (96 dpi): mm * 96 / 25.4 ≈ mm * 3.7795
                fit_width = pdf.epw * 3.7795275591
                rendered_svgs = self._render_mermaid_batch(mermaid_diagrams, fit_width=fit_width)
            else:
                pass

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

            if token_type == "mermaid":
                self._render_mermaid(pdf, token, rendered_svgs)
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

            if token_type == "footnote_definition":
                self._render_footnote_definition(pdf, token)
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
        pdf.ln(10)

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
            # Replace <fnref id="N"> tags with Unicode superscript
            content = re.sub(
                r'<fnref\s+id="(\d+)">',
                lambda m: self._superscript(m.group(1)),
                content,
            )
            pdf.set_x(pdf.l_margin)
            self._render_inline_html(pdf, content)
            pdf.ln(8)
            return

        text = token.get("text", "")
        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.multi_cell(0, 5, text, align="L")
        pdf.ln(3)

    def _render_code_block(self, pdf: FPDF, token: dict) -> None:
        """Render a code block with syntax highlighting and preserved indentation.
        
        Code blocks are kept together on one page unless they exceed page length.
        Multi-page code blocks get a separate background rect per page section.
        """
        content = str(token.get("content", "")).expandtabs(4)
        language = token.get("language", "")
        syntax_theme = self._options.get("syntax_theme", "default")
        theme = self._options.get("theme", {})
        
        from mdutil.syntax_highlighter import highlight_code_pdf
        segments = highlight_code_pdf(content, language, theme, syntax_theme)
        
        pdf.set_font(self._font_for("mono"), size=9)
        
        # Split segments at newlines to preserve source line structure.
        # Append even empty lines so blank lines inside code blocks don't collapse.
        lines: list[list[dict[str, Any]]] = []
        current_line_segments: list[dict[str, Any]] = []

        for segment in segments:
            text = segment["text"]
            rgb = segment.get("rgb")

            parts = text.split("\n")
            for i, part in enumerate(parts):
                if part:
                    current_line_segments.append({"text": part, "rgb": rgb})
                if i < len(parts) - 1:
                    lines.append(current_line_segments)
                    current_line_segments = []

        if current_line_segments:
            lines.append(current_line_segments)

        if not lines:
            lines = [[{"text": content, "rgb": None}]]

        # Calculate total height needed for this code block.
        start_x = pdf.l_margin
        right_edge = pdf.w - pdf.r_margin
        line_height = 5
        num_lines = len(lines)
        estimated_bg_height = num_lines * line_height + 1
        
        # Check if the code block fits on the current page.
        spacing_buffer = 3.0
        remaining_height = pdf.h - pdf.b_margin - pdf.get_y() - spacing_buffer
        
        # Add page break if code block doesn't fit and we're past the top margin.
        if estimated_bg_height > remaining_height and pdf.get_y() > pdf.t_margin:
            pdf.add_page()
        
        # Render the code block, splitting across pages if necessary.
        self._render_code_block_section(
            pdf, lines, start_x, right_edge, line_height, num_lines, section_start=0
        )
        
        pdf.ln(5)
    
    def _render_code_block_section(
        self,
        pdf: FPDF,
        lines: list[list[dict[str, Any]]],
        start_x: float,
        right_edge: float,
        line_height: float,
        total_lines: int,
        section_start: int,
    ) -> None:
        """Render a section of a code block (possibly spanning multiple pages).
        
        Splits the section into page-sized chunks, each with its own background rect.
        """
        # Calculate how many lines fit on one page.
        available_height = pdf.h - pdf.t_margin - pdf.b_margin - 6.0  # 3mm buffer top and bottom
        max_lines_per_page = max(1, int(available_height / line_height))
        
        i = section_start
        while i < total_lines:
            # Calculate remaining lines in this chunk.
            remaining = total_lines - i
            chunk_size = min(max_lines_per_page, remaining)
            chunk_bg_height = chunk_size * line_height + 1
            
            # Check if this chunk fits.
            fits = pdf.h - pdf.b_margin - pdf.get_y() >= chunk_bg_height
            
            if not fits and pdf.get_y() > pdf.t_margin:
                pdf.add_page()
            
            # Draw background rect for this chunk.
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(start_x, pdf.get_y(), right_edge - start_x, chunk_bg_height, style="F")
            
            # Render the lines for this chunk.
            for _ in range(chunk_size):
                self._render_code_line(pdf, lines[i], is_code_block=True)
                i += 1

    def _render_mermaid_batch(
        self,
        diagrams: list[tuple[dict, int]],
        *,
        fit_width: float | None = None,
    ) -> dict[int, bytes]:
        """Render multiple Mermaid diagrams to PNG bytes.

        Returns a dict mapping token id → PNG bytes.
        Failed renders produce (None, index) which results in a code-block fallback.

        Args:
            diagrams: List of (token, index) tuples.
            fit_width: CSS-pixel width to fit diagrams to via merman-cli
                       ``--raster-fit-width``. Clips wide diagrams before
                       rasterization so the PNG doesn't bloat.
        """
        from mdutil.export.svg_to_image import SvgToImageRenderer

        renderer = SvgToImageRenderer()
        if not renderer.available:
            return {}

        theme = self._options.get("mermaid_theme", "default")
        background = self._options.get("mermaid_background", "transparent")
        scale = self._options.get("mermaid_scale", 2.0)

        code_index_pairs = [(d.get("content", ""), i) for i, (d, _) in enumerate(diagrams)]
        results = renderer.render_diagrams_png(
            code_index_pairs,
            theme=theme,
            background=background,
            scale=scale,
            fit_width=fit_width,
        )

        rendered: dict[int, bytes] = {}
        for png, idx in results:
            if png is not None:
                token = diagrams[idx][0]
                rendered[id(token)] = png
        return rendered

    def _get_png_dimensions(self, png: bytes) -> tuple[int, int]:
        """Return (width_px, height_px) of a PNG byte array.

        Uses PIL for robustness; falls back to reading the PNG IHDR chunk
        directly if PIL is unavailable.
        """
        try:
            with PILImage.open(BytesIO(png)) as img:
                return img.size  # (width, height)
        except Exception:
            # Fallback: parse PNG IHDR chunk directly.
            if len(png) < 24 or png[:8] != b'\x89PNG\r\n\x1a\n':
                return (0, 0)
            # IHDR is the 8 bytes after the signature.
            import struct
            ihdr = png[8:16]
            width, height = struct.unpack(">HH", ihdr[:4])
            return (width, height)

    def _render_mermaid(self, pdf: FPDF, token: dict, rendered_svgs: dict[int, bytes]) -> None:
        """Render a Mermaid diagram token as an embedded PNG in the PDF.

        Handles:
        - Getting pre-rendered PNG from batch render
        - Computing actual diagram dimensions in mm using PNG pixel size
        - Page-break logic based on real diagram height
        - Centering narrower diagrams on the page
        - Aspect-ratio preservation (scale to fit page width)
        - Error fallback: render as code block when conversion fails
        """
        mermaid_enabled = self._options.get("mermaid", True)
        if not mermaid_enabled:
            self._render_code_block(pdf, token)
            return

        # Try to get pre-rendered PNG from batch render.
        png = rendered_svgs.get(id(token))
        if png is None:
            # Render failed or binary unavailable — fall back to code block.
            self._render_code_block(pdf, token)
            return

        # Validate PNG header.
        if png[:4] != b'\x89PNG':
            self._render_code_block(pdf, token)
            return

        # Get PNG pixel dimensions.
        png_w_px, png_h_px = self._get_png_dimensions(png)
        if png_w_px <= 0 or png_h_px <= 0:
            self._render_code_block(pdf, token)
            return

        # Calculate diagram dimensions on the PDF page in mm.
        # fpdf2 uses 72 dpi. merman-cli renders at scale=2.0 (2× CSS pixels).
        # CSS pixels at 96 dpi → fpdf2 mm: px / dpi * 25.4
        # So: rendered_mm = px / (scale * 96) * 25.4 = px * 25.4 / (scale * 96)
        scale = self._options.get("mermaid_scale", 2.0)
        px_to_mm = 25.4 / (scale * 96.0)  # ≈ 0.002604 mm/px at scale=2

        diagram_w_mm = png_w_px * px_to_mm
        diagram_h_mm = png_h_px * px_to_mm

        # Available width on the page (in mm).
        available_width = pdf.epw

        # Determine rendered width: use available_width, but if the diagram
        # is narrower, render at its natural width (for centering).
        if diagram_w_mm <= available_width:
            rendered_w = diagram_w_mm
        else:
            rendered_w = available_width

        # Calculate actual rendered height preserving aspect ratio.
        if png_w_px > 0:
            rendered_h = rendered_w * (png_h_px / png_w_px)
        else:
            rendered_h = diagram_h_mm

        # Page-break logic: check if diagram fits on current page.
        spacing_buffer = 8.0  # mm buffer around diagram
        remaining_height = pdf.h - pdf.b_margin - pdf.get_y() - spacing_buffer

        # Add page break if diagram doesn't fit and we're past the top margin.
        if rendered_h > remaining_height and pdf.get_y() > pdf.t_margin:
            pdf.add_page()
            remaining_height = pdf.h - pdf.b_margin - pdf.get_y() - spacing_buffer

        # X position: center the diagram if it's narrower than available width.
        if diagram_w_mm < available_width:
            x = pdf.l_margin + (available_width - rendered_w) / 2
        else:
            x = pdf.l_margin

        try:
            buf = BytesIO(png)
            pdf.image(
                buf,
                x=x,
                w=rendered_w,
                keep_aspect_ratio=True,
            )
        except Exception:
            # If image rendering fails for any reason, fall back to code block.
            self._render_code_block(pdf, token)
            return

        pdf.ln(spacing_buffer)

    def _strip_non_ascii(self, text: str) -> str:
        """Replace non-ASCII characters with ASCII equivalents or spaces."""
        result = []
        for char in text:
            if ord(char) < 128:
                result.append(char)
            elif char == "←":
                result.append("<-")
            elif char == "→":
                result.append("->")
            elif char == "←":
                result.append("<-")
            elif char == "→":
                result.append("->")
            elif char == "⚠":
                result.append("!")
            else:
                result.append(" ")
        return "".join(result)

    def _render_code_line(
        self, pdf: FPDF, line_segments: list[dict[str, Any]], *, is_code_block: bool = False
    ) -> None:
        """Render one source code line, wrapping before the right margin."""
        start_x = pdf.get_x()
        current_x = start_x
        right_edge = pdf.w - pdf.r_margin
        line_height = 5

        if not line_segments:
            pdf.ln(line_height)
            return

        line_text = "".join(segment["text"] for segment in line_segments)
        leading_spaces = len(line_text) - len(line_text.lstrip(" "))
        indent_width = pdf.get_string_width(line_text[:leading_spaces])
        continuation_x = min(start_x + indent_width, right_edge)

        # Background rect is drawn once per code block by _render_code_block.
        # Skip per-line background draws to avoid hairline gaps between rects.
        def draw_line_background() -> None:
            if not is_code_block:
                pdf.rect(start_x, pdf.get_y(), right_edge - start_x, line_height, style="F")

        draw_line_background()

        for segment in line_segments:
            rgb = segment.get("rgb")
            if rgb:
                pdf.set_text_color(rgb["r"], rgb["g"], rgb["b"])
            else:
                pdf.set_text_color(0, 0, 0)

            text = segment["text"]
            while text:
                remaining_width = right_edge - current_x
                if remaining_width <= 0:
                    pdf.ln(line_height)
                    current_x = continuation_x
                    remaining_width = right_edge - current_x
                    draw_line_background()

                chunk = self._fit_text_to_width(pdf, text, remaining_width)
                if not chunk:
                    if current_x != continuation_x:
                        pdf.ln(line_height)
                        current_x = continuation_x
                        draw_line_background()
                        continue
                    chunk = text[0]

                width = pdf.get_string_width(chunk)
                pdf.set_x(current_x)
                pdf.cell(
                    width,
                    line_height,
                    chunk,
                    new_x="LMARGIN",
                    new_y="LAST",
                    fill=False,
                )
                current_x += width
                text = text[len(chunk):]

        pdf.ln(line_height)

    def _fit_text_to_width(self, pdf: FPDF, text: str, max_width: float) -> str:
        """Return the longest prefix of text that fits within max_width."""
        if pdf.get_string_width(text) <= max_width:
            return text

        chunk = ""
        last_whitespace_break = 0
        for char in text:
            candidate = chunk + char
            if pdf.get_string_width(candidate) > max_width:
                if not chunk:
                    return ""
                if last_whitespace_break > 0:
                    return chunk[:last_whitespace_break]
                if not char.isspace():
                    return ""
                return chunk
            chunk = candidate
            if char.isspace():
                last_whitespace_break = len(chunk)
        return chunk

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

    def _render_footnote_ref(self, pdf: FPDF, span: dict[str, Any]) -> str:
        """Render a footnote reference span as a Unicode superscript."""
        fn_id = span.get("id", "")
        return self._superscript(fn_id)

    def _render_footnote_definition(self, pdf: FPDF, token: dict) -> None:
        """Render a footnote definition token.

        Format:  "    ¹  Footnote text..."  with a horizontal rule above.
        """
        if pdf.get_y() > pdf.h - pdf.b_margin - 25:
            pdf.add_page()

        # Horizontal rule separator
        y = pdf.get_y()
        x = pdf.l_margin + 2
        pdf.set_draw_color(160, 160, 160)
        pdf.line(x, y, pdf.w - pdf.r_margin, y)
        pdf.ln(4)

        fn_id = token.get("id", "")
        content = token.get("content", "")
        plain_text = self._plain_text_from_inline_html(content)
        superscript = self._superscript(fn_id)

        # Render indented footnote with superscript prefix
        pdf.set_font(self._font_for("regular"), size=self.FONT_SIZE)
        pdf.set_text_color(100, 100, 100)

        # Indent for footnote block
        start_x = pdf.l_margin + 8
        pdf.set_x(start_x)

        # Render superscript + text
        effective_w = pdf.w - start_x - pdf.r_margin
        if effective_w < 10:
            effective_w = 50
        pdf.multi_cell(effective_w, 5, f"{superscript}  {plain_text}", align="L")

        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    @staticmethod
    def _superscript(n: str) -> str:
        """Convert a number string to Unicode superscript characters."""
        super_map = {
            "0": "\u2070", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3",
            "4": "\u2074", "5": "\u2075", "6": "\u2076", "7": "\u2077",
            "8": "\u2078", "9": "\u2079",
        }
        return "".join(super_map.get(c, c) for c in n)

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
            # But replace footnote refs with superscript first
            content = re.sub(
                r'<fnref\s+id="(\d+)">',
                lambda m: self._superscript(m.group(1)),
                content,
            )
            content = re.sub(r"</?(?:strong|em|code|a[^>]*)>", "", content)

            pdf.set_x(left_x + indent)
            effective_w = pdf.w - left_x - pdf.r_margin - indent
            if effective_w < 10:
                effective_w = 50  # fallback for very narrow layouts
            pdf.multi_cell(effective_w, 5, f"{prefix}{content}", align="L")

        pdf.ln(3)
