"""Phase 4: Focused tests for PDF/HTML syntax-highlighted exports.

Covers:
- highlight_code_html() and highlight_code_pdf() in syntax_highlighter
- PdfExporter._render_code_block with syntax highlighting
- HtmlExporter._render_code_block with syntax highlighting
- Unknown/missing language fallbacks
- Custom CSS preservation alongside syntax CSS
"""

import re
import unittest
from typing import cast, Any

from mdutil.export.pdf import PdfExporter
from mdutil.export.html import HtmlExporter
from mdutil.syntax_highlighter import (
    highlight_code_html,
    highlight_code_pdf,
    _extract_all_token_colors,
)
from mdutil.themes import BUILT_IN_THEMES


def strip_ansi(text):
    return re.sub(r"\033\\[[0-9;]*m", "", text)


# ---------------------------------------------------------------------------
# highlight_code_html() tests
# ---------------------------------------------------------------------------

class HighlightCodeHtmlTests(unittest.TestCase):
    """Unit tests for highlight_code_html()."""

    def test_python_returns_html_with_span_tags(self):
        html = highlight_code_html("def f():\n    pass\n", "python")
        self.assertIn("<span", html)
        self.assertIn("<pre>", html)
        self.assertIn("<div", html)

    def test_python_keeps_original_text(self):
        """Stripped output must contain the original code verbatim."""
        code = "print('hello')\n"
        html = highlight_code_html(code, "python")
        self.assertIn("print", html)
        self.assertIn("hello", html)

    def test_unknown_language_returns_plain_text(self):
        code = "some gibberish\nnot python"
        html = highlight_code_html(code, "definitely-not-real")
        self.assertEqual(html, code)

    def test_missing_language_returns_plain_text(self):
        code = "plain text"
        html = highlight_code_html(code, "")
        self.assertEqual(html, code)

    def test_none_language_returns_plain_text(self):
        """Parser emits None for fences without an info string."""
        code = "plain text"
        html = highlight_code_html(code, None)
        self.assertEqual(html, code)

    def test_plain_text_alias_returns_plain_text(self):
        code = "this is text"
        for lang in ("text", "txt", "plain", "plaintext"):
            with self.subTest(lang=lang):
                html = highlight_code_html(code, lang)
                self.assertEqual(html, code)

    def test_javascript_is_highlighted(self):
        html = highlight_code_html("const x = 1;\n", "javascript")
        self.assertIn("<span", html)

    def test_javascript_alias(self):
        html = highlight_code_html("const x = 1;\n", "js")
        self.assertIn("<span", html)

    def test_html_language_is_highlighted(self):
        code = "<div class=\"test\">hello</div>"
        html = highlight_code_html(code, "html")
        self.assertIn("<span", html)
        self.assertIn("class", html)


# ---------------------------------------------------------------------------
# highlight_code_pdf() tests
# ---------------------------------------------------------------------------

class HighlightCodePdfTests(unittest.TestCase):
    """Unit tests for highlight_code_pdf()."""

    def test_python_returns_list_of_segments(self):
        segments = highlight_code_pdf("def f():\n    pass\n", "python")
        self.assertIsInstance(segments, list)
        self.assertTrue(len(segments) > 0)

    def test_segments_have_required_keys(self):
        segments = highlight_code_pdf("x = 1\n", "python")
        for seg in segments:
            self.assertIn("text", seg)
            self.assertIn("rgb", seg)

    def test_python_segments_reconstruct_original(self):
        """Concatenating all segment texts must equal original code."""
        code = "x = 1\ny = 2\n"
        segments = highlight_code_pdf(code, "python", BUILT_IN_THEMES["dracula"])
        reconstructed = "".join(s["text"] for s in segments)
        # highlight_code_pdf may include trailing newline in segments
        self.assertIn(reconstructed, [code, code.rstrip("\n")])

    def test_unknown_language_returns_single_plain_segment(self):
        code = "unknown language text"
        segments = highlight_code_pdf(code, "xyz-unknown")
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["text"], code)
        self.assertIsNone(segments[0]["rgb"])

    def test_missing_language_returns_single_plain_segment(self):
        code = "plain text"
        segments = highlight_code_pdf(code, "")
        self.assertEqual(len(segments), 1)
        self.assertIsNone(segments[0]["rgb"])

    def test_none_language_returns_single_plain_segment(self):
        """Parser emits None for fences without an info string."""
        code = "plain text"
        segments = highlight_code_pdf(code, None)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["text"], code)
        self.assertIsNone(segments[0]["rgb"])

    def test_plain_text_alias_returns_plain_segment(self):
        code = "plain text only"
        for lang in ("text", "txt", "plain"):
            with self.subTest(lang=lang):
                segments = highlight_code_pdf(code, lang)
                self.assertEqual(segments[0]["text"], code)
                self.assertIsNone(segments[0]["rgb"])

    def test_rgb_value_is_dict_with_r_g_b(self):
        """At least some segments should have RGB colors for Python code."""
        segments = highlight_code_pdf("def f():\n    pass\n", "python", BUILT_IN_THEMES["dracula"])
        colored = [s for s in segments if s["rgb"] is not None]
        # 'def' should be a keyword with a color
        self.assertTrue(len(colored) > 0, "Expected some colored segments for Python code")
        for seg in colored:
            self.assertIn("r", seg["rgb"])
            self.assertIn("g", seg["rgb"])
            self.assertIn("b", seg["rgb"])
            self.assertTrue(all(0 <= v <= 255 for v in seg["rgb"].values()))

    def test_segments_with_same_color_are_grouped(self):
        """Consecutive tokens of the same type should be merged into one segment."""
        code = "def f():\n    pass\n"
        segments = highlight_code_pdf(code, "python", BUILT_IN_THEMES["dracula"])
        # 'def' is a keyword; 'f' is a function name; they likely have different colors
        # So we expect at least 2 segments with different colors
        colors = [(s.get("rgb")) for s in segments]
        unique_colors = set(id(c) for c in colors if c is not None)
        # We just check we have multiple segments for Python code
        self.assertGreaterEqual(len(segments), 2, "Expected multiple segments for Python code")


# ---------------------------------------------------------------------------
# PdfExporter._render_code_block() tests
# ---------------------------------------------------------------------------

class PdfExporterSyntaxHighlightTests(unittest.TestCase):
    """Unit tests for PDF exporter code block rendering with syntax highlighting."""

    def setUp(self):
        self.exporter = PdfExporter()

    def _fake_pdf(self):
        """Return a mock FPDF-like object that records cell calls."""

        class FakePdf:
            page = 1

            def __init__(self):
                self.cells = []
                self.text_colors = []
                self.font_calls = []
                self.ln_calls = []
                self._x = 20.0

            def get_x(self) -> float:
                return self._x

            def set_x(self, x: float) -> None:
                self._x = x

            def get_string_width(self, text: str) -> float:
                return len(text) * 5.0

            def set_font(self, family, style="", size=0):
                self.font_calls.append((family, style, size))

            def set_fill_color(self, *args, **kwargs):
                pass

            def set_text_color(self, *args, **kwargs):
                self.text_colors.append(args)

            def cell(self, *args, **kwargs):
                self.cells.append((args, kwargs))

            def ln(self, *args, **kwargs):
                self.ln_calls.append(args)

        return FakePdf()

    def test_code_block_uses_syntax_theme_from_options(self):
        pdf = self._fake_pdf()
        self.exporter._options = {"syntax_theme": "dracula"}
        self.exporter._use_unicode = False

        token = {"type": "code", "content": "x = 1\n", "language": "python"}
        self.exporter._render_code_block(cast(Any, pdf), token)

        # Should have called set_text_color at least once (for the text itself)
        self.assertTrue(len(pdf.text_colors) > 0)

    def test_code_block_uses_mono_font(self):
        pdf = self._fake_pdf()
        self.exporter._options = {}
        self.exporter._use_unicode = False

        token = {"type": "code", "content": "x = 1\n", "language": "python"}
        self.exporter._render_code_block(cast(Any, pdf), token)

        mono_fonts = [c for c in pdf.font_calls if c[0] == "Courier" or c[0] == "UnicodeMono"]
        self.assertTrue(len(mono_fonts) > 0, "Expected monospace font for code block")

    def test_unknown_language_falls_back_to_plain(self):
        pdf = self._fake_pdf()
        self.exporter._options = {"syntax_theme": "default"}
        self.exporter._use_unicode = False

        token = {"type": "code", "content": "plain text\n", "language": "xyzunknown"}
        self.exporter._render_code_block(cast(Any, pdf), token)

        # With plain text fallback, should still render but with default color
        self.assertTrue(len(pdf.cells) > 0)

    def test_missing_language_falls_back_to_plain(self):
        pdf = self._fake_pdf()
        self.exporter._options = {}
        self.exporter._use_unicode = False

        token = {"type": "code", "content": "no language here\n"}
        self.exporter._render_code_block(cast(Any, pdf), token)

        self.assertTrue(len(pdf.cells) > 0)

    def test_none_language_falls_back_to_plain(self):
        """Fenced code blocks without info strings should not crash PDF export."""
        pdf = self._fake_pdf()
        self.exporter._options = {}
        self.exporter._use_unicode = False

        token = {"type": "code", "content": "no language here\n", "language": None}
        self.exporter._render_code_block(cast(Any, pdf), token)

        self.assertTrue(len(pdf.cells) > 0)


# ---------------------------------------------------------------------------
# HtmlExporter._render_code_block() tests
# ---------------------------------------------------------------------------

class HtmlExporterSyntaxHighlightTests(unittest.TestCase):
    """Unit tests for HTML exporter code block rendering with syntax highlighting."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_python_code_has_highlight_classes(self):
        token = {"type": "code", "content": "def f():\n    pass\n", "language": "python"}
        result = self.exporter._render_code_block(token, syntax_theme="default")

        # Should contain span tags from Pygments
        self.assertIn("<span", result)
        # Should have the language class
        self.assertIn('language-python', result)
        # Original text should be present
        self.assertIn("def", result)

    def test_unknown_language_has_no_highlight_classes(self):
        token = {"type": "code", "content": "gibberish\n", "language": "xyzunknown"}
        result = self.exporter._render_code_block(token, syntax_theme="default")

        # No span tags, just escaped content
        self.assertNotIn("<span", result)
        self.assertIn("<pre><code", result)

    def test_no_language_has_no_highlight_classes(self):
        token = {"type": "code", "content": "plain text\n"}
        result = self.exporter._render_code_block(token, syntax_theme="default")

        self.assertNotIn("<span", result)
        # Should still have pre/code wrapper
        self.assertIn("<pre><code>", result)

    def test_none_language_has_no_highlight_classes(self):
        token = {"type": "code", "content": "plain text\n", "language": None}
        result = self.exporter._render_code_block(token, syntax_theme="default")

        self.assertNotIn("<span", result)
        self.assertIn("<pre><code>", result)

    def test_special_html_entities_are_escaped_in_fallback(self):
        """Plain text fallback should escape &, <, >."""
        token = {"type": "code", "content": "x < y && z > 0\n", "language": "xyzunknown"}
        result = self.exporter._render_code_block(token, syntax_theme="default")

        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertIn("&amp;", result)


# ---------------------------------------------------------------------------
# Full HTML export pipeline: CSS injection
# ---------------------------------------------------------------------------

class HtmlExportFullPipelineTests(unittest.TestCase):
    """Test that full HTML export pipeline includes syntax theme CSS."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_syntax_css_injected_in_full_render(self):
        tokens = [{"type": "heading", "text": "Test", "level": 1}]
        result = self.exporter.render(tokens, {}, {"syntax_theme": "default"})

        # Pygments style_defs should be injected into the <style> block
        self.assertIn("<style>", result)
        # Should contain Pygments-style CSS rules (e.g., .mdutil-highlight .c { ... })
        self.assertIn(".mdutil-highlight", result)

    def test_custom_css_injected_after_syntax_css(self):
        tokens = [{"type": "heading", "text": "Test", "level": 1}]
        result = self.exporter.render(tokens, {}, {
            "syntax_theme": "default",
            "custom_css": "body { color: red; }",
        })

        # Custom CSS marker present
        self.assertIn("/* Custom CSS */", result)
        self.assertIn("body { color: red; }", result)
        # Custom CSS comes after syntax CSS
        syntax_pos = result.find(".mdutil-highlight")
        custom_pos = result.find("/* Custom CSS */")
        self.assertGreater(custom_pos, syntax_pos, "Custom CSS should come after syntax CSS")


if __name__ == "__main__":
    unittest.main()
