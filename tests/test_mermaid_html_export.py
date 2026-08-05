"""Unit tests for HTML exporter mermaid integration (KB-022)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from mdutil.export.html import HtmlExporter
from mdutil.parser import parse_markdown


@pytest.fixture
def exporter():
    return HtmlExporter()


def _make_mermaid_token(source: str) -> dict:
    """Create a mermaid token as the parser would produce."""
    return {
        "type": "mermaid",
        "content": source,
        "language": "mermaid",
        "text": source,
    }


def _make_paragraph_token(text: str) -> dict:
    return {
        "type": "paragraph",
        "content": text,
        "text": text,
    }


class TestMermaidRendering:
    """Tests for mermaid SVG rendering in HTML export."""

    def test_mermaid_token_rendered_as_mermaid_type(self):
        """Parser should produce 'mermaid' type for mermaid blocks."""
        md = "```mermaid\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

    def test_render_without_binary_falls_back_to_code_block(self, exporter):
        """When merman-cli binary is unavailable, mermaid renders as code block."""
        tokens = [_make_mermaid_token("graph TD; A-->B;")]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch(
            "mdutil.export.html.MermanRenderer"
        ) as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, theme, options)

        # Should contain escaped code block, not <svg>
        assert "<svg" not in result
        assert "mermaid" in result.lower() or "graph TD" in result
        assert "language-mermaid" in result or "<code>" in result

    def test_render_with_mock_svg(self, exporter, tmp_path):
        """When merman-cli succeeds, SVG is embedded in a <div class='mermaid'>."""
        tokens = [_make_mermaid_token("graph TD; A-->B;")]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        fake_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>'

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]

            result = exporter.render(tokens, theme, options)

        assert "mermaid" in result
        assert "<svg" in result
        assert '<div class="mermaid">' in result

    def test_render_disabled_mermaid_as_code_block(self, exporter):
        """--no-mermaid should render mermaid blocks as plain code blocks."""
        tokens = [_make_mermaid_token("graph TD; A-->B;")]
        theme = {}
        options = {"mermaid": False, "syntax_theme": "default"}

        result = exporter.render(tokens, theme, options)

        assert "<svg" not in result
        assert "language-mermaid" in result or "<code>" in result

    def test_render_mixed_content(self, exporter):
        """Document with mermaid and regular code blocks."""
        tokens = [
            _make_paragraph_token("Some intro text."),
            _make_mermaid_token("graph TD; A-->B;"),
            _make_paragraph_token("Some more text."),
            {"type": "code", "content": "print('hello')", "language": "python", "text": "print('hello')"},
        ]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, theme, options)

        # Should have a paragraph, mermaid fallback, another paragraph, and code block
        assert "<p>" in result
        assert "Some intro text" in result
        assert "print" in result

    def test_css_includes_mermaid_styles(self, exporter):
        """Rendered HTML should include .mermaid CSS class."""
        tokens = [_make_mermaid_token("graph TD; A-->B;")]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, theme, options)

        assert ".mermaid" in result
        assert "text-align: center" in result

    def test_error_svg_shows_error_comment_and_code(self, exporter):
        """When SVG rendering fails, show error note and raw mermaid code."""
        tokens = [_make_mermaid_token("invalid mermaid [[[")]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            error_svg = "<!-- render error: invalid syntax -->"
            instance.render_diagrams.return_value = [("invalid mermaid [[[", 0, error_svg)]

            result = exporter.render(tokens, theme, options)

        assert "could not be rendered" in result.lower()
        assert "invalid mermaid [[[" in result

    def test_mermaid_theme_passed_to_renderer(self, exporter):
        """mermaid_theme option should be passed to MermanRenderer."""
        tokens = [_make_mermaid_token("graph TD; A-->B;")]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default", "mermaid_theme": "dark"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, "<svg/>")]
            exporter.render(tokens, theme, options)

            # Verify the theme was passed via keyword argument
            call_args = instance.render_diagrams.call_args
            assert call_args[1]["theme"] == "dark"

    def test_multiple_mermaid_diagrams(self, exporter):
        """Multiple mermaid diagrams in one document."""
        tokens = [
            _make_mermaid_token("graph TD; A-->B;"),
            _make_mermaid_token("sequenceDiagram\n  A->>B: hi"),
        ]
        theme = {}
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                ("graph TD; A-->B;", 0, '<svg>svg1</svg>'),
                ("sequenceDiagram\n  A->>B: hi", 1, '<svg>svg2</svg>'),
            ]
            result = exporter.render(tokens, theme, options)

        assert result.count("<svg") == 2
        assert result.count('<div class="mermaid">') == 2
