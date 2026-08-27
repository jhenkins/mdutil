"""Tests for block-level display math ($$...$$) parsing and rendering.

Covers KB-104: block-level math should not leak into inline parsing.
"""

from __future__ import annotations

import pytest

from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter
from mdutil.parser import parse_markdown
from mdutil.renderer import render


class TestDisplayMathParser:
    """Parser tests for $$...$$ display math."""

    def test_single_line_display_math(self):
        tokens = parse_markdown("$$E=mc^2$$")
        assert len(tokens) == 1
        assert tokens[0]["type"] == "math_display"
        assert tokens[0]["content"] == "E=mc^2"
        assert tokens[0]["language"] is None

    def test_multi_line_display_math(self):
        tokens = parse_markdown("$$\nx = -b ± √(b² - 4ac)\n$$")
        assert len(tokens) == 1
        assert tokens[0]["type"] == "math_display"
        assert "x = -b" in tokens[0]["content"]
        assert "4ac" in tokens[0]["content"]

    def test_display_math_with_text_around(self):
        """$$...$$ embedded in text still leaks into inline parsing (out of scope for KB-104)."""
        tokens = parse_markdown("The equation $$E=mc^2$$ is famous.")
        assert tokens[0]["type"] == "paragraph"
        # The $$ still leaks into inline parsing for embedded cases
        assert "<math>" in tokens[0]["content"]

    def test_display_math_in_document(self):
        md = "Some text.\n\n$$\nE = mc^2\n$$\n\nMore text."
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        assert "math_display" in types
        math_idx = types.index("math_display")
        assert types[math_idx - 1] == "blank" or types[math_idx - 1] == "paragraph"

    def test_multiple_display_math_blocks(self):
        md = "$$\na = b\n$$\n\n$$\nc = d\n$$"
        tokens = parse_markdown(md)
        math_tokens = [t for t in tokens if t["type"] == "math_display"]
        assert len(math_tokens) == 2


class TestDisplayMathRenderer:
    """Terminal renderer tests for display math."""

    def test_render_single_line(self):
        md = "$$E=mc^2$$"
        tokens = parse_markdown(md)
        result = render(tokens)
        assert isinstance(result, str)
        # Should render as centered text
        assert "E=mc^2" in result

    def test_render_multi_line(self):
        md = "$$\nx = 1\ny = 2\n$$"
        tokens = parse_markdown(md)
        result = render(tokens)
        assert isinstance(result, str)
        assert "x = 1" in result
        assert "y = 2" in result


class TestDisplayMathHtmlExporter:
    """HTML exporter tests for display math."""

    def test_export_single_line(self):
        md = "$$E=mc^2$$"
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        assert "math-display" in html
        assert "E=mc^2" in html

    def test_export_multi_line(self):
        md = "$$\nx = 1\ny = 2\n$$"
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        assert "math-display" in html
        assert "x = 1" in html
        assert "y = 2" in html

    def test_math_display_css_present(self):
        md = "$$x = 1$$"
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        assert ".math-display" in html


class TestDisplayMathPdfExporter:
    """PDF exporter tests for display math."""

    def test_export_single_line(self):
        md = "$$E=mc^2$$"
        tokens = parse_markdown(md)
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        assert pdf_bytes.startswith(b"%PDF")
        assert len(pdf_bytes) > 100

    def test_export_multi_line(self):
        md = "$$\nx = 1\ny = 2\n$$"
        tokens = parse_markdown(md)
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        assert pdf_bytes.startswith(b"%PDF")
        assert len(pdf_bytes) > 100
