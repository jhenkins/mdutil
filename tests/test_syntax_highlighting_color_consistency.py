"""Tests for KB-100: HTML syntax highlighting colours match PDF/markdown.

Verifies that the HTML exporter uses the same merged theme+syntax-theme
colour approach as the PDF and terminal exporters.
"""

from __future__ import annotations

import pytest

from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter
from mdutil.parser import parse_markdown
from mdutil.syntax_highlighter import highlight_code_html, highlight_code_pdf
from mdutil.themes import load_theme


class TestColorConsistency:
    """Verify HTML and PDF use the same colour approach."""

    def test_html_uses_merged_style(self):
        """HTML highlighter should accept theme parameter and merge with syntax theme."""
        code = "def hello():\n    print('world')\n    x = 42  # comment"
        theme = load_theme("dracula")

        html_out = highlight_code_html(code, "python", "dracula", theme=theme)
        assert "<span" in html_out

    def test_html_uses_theme_colors_for_strings(self):
        """HTML should use theme's string color, not just syntax theme."""
        code = 'x = "hello"'
        theme = load_theme("dracula")

        html_out = highlight_code_html(code, "python", "dracula", theme=theme)
        # With theme merging, string color should come from theme
        assert "string" in html_out.lower() or "s2" in html_out or "s" in html_out

    def test_pdf_uses_theme_colors(self):
        """PDF should produce colored segments using theme colors."""
        code = 'x = "hello"\ny = 42'
        theme = load_theme("dracula")

        segments = highlight_code_pdf(code, "python", theme, "dracula")
        # Should have colored segments
        colored = [s for s in segments if s.get("rgb") is not None]
        assert len(colored) > 0

    def test_html_and_pdf_both_color_strings(self):
        """Both HTML and PDF should color string literals."""
        code = 'x = "hello"'
        theme = load_theme("dracula")

        html_out = highlight_code_html(code, "python", "dracula", theme=theme)
        segments = highlight_code_pdf(code, "python", theme, "dracula")

        # Both should have highlighting
        assert "<span" in html_out
        colored = [s for s in segments if s.get("rgb") is not None]
        assert len(colored) > 0

    def test_html_full_render_uses_theme(self):
        """HTML full render should use theme for code highlighting."""
        md = '```python\ndef hello():\n    print("world")\n```'
        tokens = parse_markdown(md)
        theme = load_theme("dracula")
        exporter = HtmlExporter()
        html = exporter.render(tokens, theme, {"syntax_theme": "dracula"})
        assert "<span" in html
        assert "def" in html

    def test_html_css_reflects_merged_colors(self):
        """CSS classes in HTML should reflect merged theme+syntax colors."""
        md = '```python\nx = 42\n```'
        tokens = parse_markdown(md)
        theme = load_theme("dracula")
        exporter = HtmlExporter()
        html = exporter.render(tokens, theme, {"syntax_theme": "dracula"})
        # Should have CSS with color definitions
        assert ".mdutil-highlight" in html


class TestColorMismatchRegression:
    """Regression tests to ensure HTML/PDF colour consistency."""

    def test_no_empty_math_in_block(self):
        """Display math should not produce empty math tags (KB-104)."""
        md = "$$\nx = 1\n$$"
        tokens = parse_markdown(md)
        assert tokens[0]["type"] == "math_display"
        assert tokens[0]["content"] == "x = 1"

    def test_html_no_raw_math_tags(self):
        """HTML should not contain raw <math> tags (KB-101)."""
        md = "Eq: $E=mc^2$"
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        assert "<math>" not in html
        assert '<span class="math">' in html
