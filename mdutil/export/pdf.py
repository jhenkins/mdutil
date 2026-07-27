"""PDF exporter using fpdf2 for v3.0."""

from __future__ import annotations

from typing import Union

from fpdf import FPDF

from mdutil.export.base import Exporter


class PdfExporter(Exporter):
    """Export Markdown to PDF using fpdf2."""

    FONT_SIZE: float = 10
    MARGIN: float = 20

    # Use built-in fpdf2 fonts (no external files needed)
    FONT_REGULAR: str = "Helvetica"
    FONT_BOLD: str = "Helvetica"
    FONT_ITALIC: str = "Helvetica"
    FONT_MONO: str = "Courier"

    def supports(self, format: str) -> bool:
        return format.lower() == "pdf"

    def render(self, tokens: list[dict], theme: dict, options: dict) -> bytes:
        """Render tokens to PDF bytes."""
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=self.MARGIN)
        pdf.set_margins(left=self.MARGIN, top=self.MARGIN, right=self.MARGIN)
        pdf.add_page()

        self._render_tokens(pdf, tokens)

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

        pdf.set_font(self.FONT_BOLD, size=font_size)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    def _render_paragraph(self, pdf: FPDF, token: dict) -> None:
        """Render a paragraph token."""
        content = token.get("content", "")
        text = token.get("text", "")

        pdf.set_font(self.FONT_REGULAR, size=self.FONT_SIZE)
        pdf.multi_cell(0, 5, text, align="L")
        pdf.ln(3)

    def _render_code_block(self, pdf: FPDF, token: dict) -> None:
        """Render a code block with background."""
        content = token.get("content", "")
        lines = content.split("\n")

        pdf.set_font(self.FONT_MONO, size=9)
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
        pdf.set_font(self.FONT_BOLD, size=self.FONT_SIZE)
        pdf.set_fill_color(230, 230, 230)

        for i, header in enumerate(headers):
            align = alignments[i] if i < len(alignments) else "L"
            pdf.cell(col_width, 8, header, border=1, fill=True, align=align)
        pdf.ln()

        # Rows
        pdf.set_font(self.FONT_REGULAR, size=self.FONT_SIZE)
        for row in rows:
            for i, cell in enumerate(row):
                align = alignments[i] if i < len(alignments) else "L"
                pdf.cell(col_width, 6, cell, border=1, align=align)
            pdf.ln()

        pdf.ln(5)

    def _render_blockquote(self, pdf: FPDF, token: dict) -> None:
        """Render a blockquote."""
        content = token.get("content", "")
        text_lines = content.split("\n")

        pdf.set_font(self.FONT_REGULAR, size=self.FONT_SIZE)
        pdf.set_text_color(100, 100, 100)

        for line in text_lines:
            if line.startswith(">"):
                line = line.lstrip(">").strip()
            pdf.multi_cell(0, 5, f"> {line}", align="L")

        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    def _render_list(self, pdf: FPDF, token: dict) -> None:
        """Render an ordered or unordered list."""
        items = token.get("items", [])
        ordered = token.get("ordered", False)

        pdf.set_font(self.FONT_REGULAR, size=self.FONT_SIZE)

        for i, item in enumerate(items, 1):
            if ordered:
                prefix = f"{i}. "
            else:
                prefix = "- "

            pdf.multi_cell(0, 5, f"{prefix}{item}", align="L")

        pdf.ln(3)
