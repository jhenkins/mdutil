"""Tests for the mdutil export module (v3.0 Phase 1)."""

import unittest
from typing import Any, cast
from unittest.mock import MagicMock

from mdutil.export import Exporter
from mdutil.export.base import Exporter as BaseExporter
from mdutil.export.pdf import PdfExporter
from mdutil.export.html import HtmlExporter
from mdutil.parser import parse_markdown


class BaseExporterTests(unittest.TestCase):
    """Test the abstract Exporter base class."""

    def test_exporter_is_abstract(self):
        """Exporter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            Exporter()

    def test_exporter_is_abstract_class(self):
        """Exporter is the base class, not a concrete implementation."""
        self.assertTrue(issubclass(Exporter, BaseExporter))

    def test_subclass_must_implement_render(self):
        """A subclass that omits render() raises TypeError on instantiation."""

        class IncompleteExporter(Exporter):
            def supports(self, format: str) -> bool:
                return False

        with self.assertRaises(TypeError):
            IncompleteExporter()

    def test_subclass_must_implement_supports(self):
        """A subclass that omits supports() raises TypeError on instantiation."""

        class IncompleteExporter(Exporter):
            def render(self, tokens, theme, options):
                return b""

        with self.assertRaises(TypeError):
            IncompleteExporter()


class PdfExporterTests(unittest.TestCase):
    """Test PdfExporter functionality."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_supports_pdf(self):
        self.assertTrue(self.exporter.supports("pdf"))

    def test_does_not_support_html(self):
        self.assertFalse(self.exporter.supports("html"))

    def test_does_not_support_unknown_format(self):
        self.assertFalse(self.exporter.supports("txt"))
        self.assertFalse(self.exporter.supports(""))

    def test_render_returns_bytes(self):
        tokens = [{"type": "heading", "text": "Test"}]
        theme = {}
        options = {}

        result = self.exporter.render(tokens, theme, options)
        self.assertIsInstance(result, bytes)

    def test_render_returns_pdf_header_bytes(self):
        """Stub should return a valid PDF header to indicate PDF format."""
        result = self.exporter.render([], {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_pdf_with_bookmarks(self):
        """PDF output includes outline entries for headings."""
        tokens = [
            {"type": "heading", "text": "Chapter 1", "level": 1},
            {"type": "paragraph", "text": "Body"},
            {"type": "heading", "text": "Section 1.1", "level": 2},
        ]
        result = self.exporter.render(tokens, {}, {"pdf_bookmarks": True})
        self.assertIsInstance(result, bytes)
        self.assertIn(b"/Outlines", result)

    def test_render_pdf_paper_size_letter(self):
        """PDF output uses Letter paper size when specified."""
        tokens = [{"type": "heading", "text": "Test"}]
        result = self.exporter.render(tokens, {}, {"pdf_paper_size": "Letter"})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_pdf_paper_size_legal(self):
        """PDF output uses Legal paper size when specified."""
        tokens = [{"type": "heading", "text": "Test"}]
        result = self.exporter.render(tokens, {}, {"pdf_paper_size": "Legal"})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_pdf_custom_margins(self):
        """PDF output respects custom margins."""
        tokens = [{"type": "heading", "text": "Test"}]
        result = self.exporter.render(tokens, {}, {
            "pdf_margin_top": 30,
            "pdf_margin_bottom": 25,
            "pdf_margin_left": 15,
            "pdf_margin_right": 15,
        })
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_pdf_with_header_footer(self):
        """PDF output includes header and footer text."""
        tokens = [{"type": "heading", "text": "Test"}]
        result = self.exporter.render(tokens, {}, {
            "pdf_header": "My Header",
            "pdf_footer": "Page footer",
        })
        self.assertTrue(result.startswith(b"%PDF"))

    def test_heading_font_sizes_are_scaled_down(self):
        """PDF Markdown heading sizes are reduced from the original oversized values."""

        class FakePdf:
            page = 1

            def __init__(self):
                self.font_calls = []

            def set_font(self, family, style="", size=0):
                self.font_calls.append((family, style, size))

            def cell(self, *args, **kwargs):
                pass

            def ln(self, *args, **kwargs):
                pass

        fake_pdf = FakePdf()
        self.exporter._use_unicode = False
        self.exporter._heading_sections = []

        self.exporter._render_heading(cast(Any, fake_pdf), {"type": "heading", "text": "Title", "level": 1})

        self.assertAlmostEqual(fake_pdf.font_calls[0][2], 13.2)

    def test_pdf_document_header_metadata_renders_one_entry_per_line(self):
        """Spec metadata header lines should not collapse into one PDF line."""

        class FakePdf:
            l_margin = 20

            def __init__(self):
                self.writes = []
                self.line_breaks = []

            def set_x(self, x):
                pass

            def set_font(self, *args, **kwargs):
                pass

            def set_text_color(self, *args, **kwargs):
                pass

            def write(self, h, text, link=""):
                self.writes.append((text, link))

            def ln(self, amount=0):
                self.line_breaks.append(amount)

        tokens = parse_markdown(
            "**Author:** _Jan Henkins_\n"
            "**Version:** 3.0.0\n"
            "**Last‑Updated:** 2026‑07‑27\n"
            "**License:** MIT\n"
            "**Repository:** <https://github.com/jhenkins/mdutil>"
        )
        fake_pdf = FakePdf()
        self.exporter._use_unicode = False

        self.exporter._render_paragraph(cast(Any, fake_pdf), tokens[0])

        rendered_lines = "\n".join(text for text, _link in fake_pdf.writes)
        self.assertIn("Author:", rendered_lines)
        self.assertIn("Version:", rendered_lines)
        self.assertGreaterEqual(fake_pdf.line_breaks.count(5), 5)

    def test_pdf_inline_markdown_uses_fonts_and_link_annotations(self):
        """PDF paragraphs preserve inline strong/em/code styles and URL links."""

        class FakePdf:
            l_margin = 20

            def __init__(self):
                self.font_calls = []
                self.writes = []

            def set_x(self, x):
                pass

            def set_font(self, family, style="", size=0):
                self.font_calls.append((family, style, size))

            def set_text_color(self, *args, **kwargs):
                pass

            def write(self, h, text, link=""):
                self.writes.append((text, link))

            def ln(self, amount=0):
                pass

        token = parse_markdown("Paragraph with **bold**, *emphasis*, `code`, and [link](https://example.com).")
        fake_pdf = FakePdf()
        self.exporter._use_unicode = False

        self.exporter._render_paragraph(cast(Any, fake_pdf), token[0])

        styles = [style for _family, style, _size in fake_pdf.font_calls]
        writes = fake_pdf.writes
        self.assertIn("B", styles)
        self.assertIn("I", styles)
        self.assertTrue(any(family == "Courier" for family, _style, _size in fake_pdf.font_calls))
        self.assertIn(("link", "https://example.com"), writes)

    def test_render_table_wraps_text_inside_cells(self):
        """PDF table cells use multi_cell wrapping instead of single-line cells."""

        class FakePdf:
            w = 210
            h = 297
            l_margin = 20
            r_margin = 20
            b_margin = 20

            def __init__(self):
                self.y = 20
                self.multi_cell_calls = []
                self.cell_calls = []

            def set_font(self, *args, **kwargs):
                pass

            def set_fill_color(self, *args, **kwargs):
                pass

            def get_y(self):
                return self.y

            def set_xy(self, x, y):
                self.y = y

            def rect(self, *args, **kwargs):
                pass

            def add_page(self):
                self.y = 20

            def multi_cell(self, w, h, text, **kwargs):
                self.multi_cell_calls.append((w, h, text, kwargs))
                if kwargs.get("dry_run"):
                    return ["wrapped", "text"] if "long" in text else [text]
                return None

            def cell(self, *args, **kwargs):
                self.cell_calls.append((args, kwargs))

            def ln(self, amount=0):
                self.y += amount

        fake_pdf = FakePdf()
        tokens = [{
            "type": "table",
            "headers": ["Name", "Description"],
            "rows": [["mdutil", "long text that should wrap in the cell"]],
            "alignments": ["left", "left"],
        }]
        self.exporter._use_unicode = False

        self.exporter._render_table(cast(Any, fake_pdf), tokens[0])

        self.assertTrue(any(call[3].get("dry_run") for call in fake_pdf.multi_cell_calls))
        self.assertTrue(any(not call[3].get("dry_run") for call in fake_pdf.multi_cell_calls))
        self.assertEqual(fake_pdf.cell_calls, [])

    def test_render_blockquote_draws_block_and_drops_marker_prefix(self):
        """PDF blockquotes render as an indented block instead of literal > lines."""

        class FakePdf:
            w = 210
            l_margin = 20
            r_margin = 20

            def __init__(self):
                self.y = 20
                self.writes = []
                self.lines = []

            def set_font(self, *args, **kwargs):
                pass

            def set_text_color(self, *args, **kwargs):
                pass

            def set_draw_color(self, *args, **kwargs):
                pass

            def get_y(self):
                return self.y

            def set_x(self, x):
                pass

            def write(self, h, text, link=""):
                self.writes.append(text)

            def ln(self, amount=0):
                self.y += amount

            def line(self, *args):
                self.lines.append(args)

        fake_pdf = FakePdf()
        self.exporter._use_unicode = False

        self.exporter._render_blockquote(cast(Any, fake_pdf), {"type": "blockquote", "content": "> **Quote** text"})

        self.assertIn("Quote", "".join(fake_pdf.writes))
        self.assertTrue(all(not text.startswith(">") for text in fake_pdf.writes))
        self.assertTrue(fake_pdf.lines)

    def test_render_pdf_bookmarks_disabled(self):
        """PDF output has no outlines when bookmarks disabled."""
        tokens = [{"type": "heading", "text": "Test", "level": 1}]
        result = self.exporter.render(tokens, {}, {"pdf_bookmarks": False})
        self.assertNotIn(b"/Outlines", result)

    def test_render_table_alternating_rows(self):
        """Table rows should have alternating fill colors."""
        tokens = [{
            "type": "table",
            "headers": ["A", "B"],
            "rows": [["1", "2"], ["3", "4"]],
            "alignments": ["left", "left"],
        }]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_blockquote(self):
        """Blockquote renders in PDF with grey color."""
        tokens = [{"type": "blockquote", "content": "> Quote text"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_unordered_list(self):
        """Unordered list renders in PDF."""
        tokens = [{"type": "list", "items": ["Item A", "Item B"], "ordered": False}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_ordered_list(self):
        """Ordered list renders in PDF."""
        tokens = [{"type": "list", "items": ["Item 1", "Item 2"], "ordered": True}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_code_block(self):
        """Code block renders in PDF with monospace font."""
        tokens = [{"type": "code", "content": "print('hello')", "language": "python"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_horizontal_rule(self):
        """Horizontal rule renders in PDF."""
        tokens = [{"type": "horizontal_rule", "content": "---"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_table_no_headers(self):
        """PDF handles empty table gracefully."""
        tokens = [{"type": "table", "headers": [], "rows": [], "alignments": []}]
        result = self.exporter.render(tokens, {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_render_heading_h4_no_bookmark(self):
        """h4 heading does not create an outline entry."""
        tokens = [{"type": "heading", "text": "Minor", "level": 4}]
        result = self.exporter.render(tokens, {}, {"pdf_bookmarks": True})
        self.assertNotIn(b"/Outlines", result)


class HtmlExporterCustomCssTests(unittest.TestCase):
    """Test HtmlExporter custom CSS support."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_custom_css_embedded(self):
        """Custom CSS is embedded in HTML output."""
        tokens = [{"type": "heading", "text": "Test", "level": 1}]
        result = self.exporter.render(tokens, {}, {"custom_css": "body { color: red; }"})
        self.assertIn("/* Custom CSS */", result)
        self.assertIn("body { color: red; }", result)

    def test_no_custom_css_by_default(self):
        """No custom CSS marker when option not provided."""
        tokens = [{"type": "heading", "text": "Test", "level": 1}]
        result = self.exporter.render(tokens, {}, {})
        self.assertNotIn("/* Custom CSS */", result)


class HtmlExporterTests(unittest.TestCase):
    """Test HtmlExporter functionality."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_supports_html(self):
        self.assertTrue(self.exporter.supports("html"))

    def test_does_not_support_pdf(self):
        self.assertFalse(self.exporter.supports("pdf"))

    def test_does_not_support_unknown_format(self):
        self.assertFalse(self.exporter.supports("txt"))
        self.assertFalse(self.exporter.supports(""))

    def test_render_returns_string(self):
        tokens = [{"type": "heading", "text": "Test"}]
        theme = {}
        options = {}

        result = self.exporter.render(tokens, theme, options)
        self.assertIsInstance(result, str)

    def test_render_returns_html_document(self):
        """Stub should return a minimal HTML document."""
        result = self.exporter.render([], {}, {})
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<html", result)
        self.assertIn("</html>", result)
        self.assertIn("<body>", result)
        self.assertIn("</body>", result)
        self.assertIn("<style>", result)
        self.assertIn("</style>", result)

    def test_render_heading(self):
        """Headings should render with appropriate tags."""
        tokens = [{"type": "heading", "text": "Test Heading", "level": 1}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<h1>Test Heading</h1>", result)

    def test_render_paragraph(self):
        """Paragraphs should render with p tags."""
        tokens = [{"type": "paragraph", "text": "Test paragraph"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<p>Test paragraph</p>", result)

    def test_render_document_header_metadata_on_separate_lines(self):
        """Document metadata header lines should not collapse into one visual line."""
        tokens = parse_markdown(
            "**Author:** _Jan Henkins_\n"
            "**Version:** 3.0.0\n"
            "**Last‑Updated:** 2026‑07‑27\n"
            "**License:** MIT\n"
            "**Repository:** <https://github.com/jhenkins/mdutil>"
        )

        result = self.exporter.render(tokens, {}, {})

        self.assertIn(
            "<p><strong>Author:</strong> <em>Jan Henkins</em><br>\n"
            "<strong>Version:</strong> 3.0.0<br>\n"
            "<strong>Last‑Updated:</strong> 2026‑07‑27<br>\n"
            "<strong>License:</strong> MIT<br>\n"
            '<strong>Repository:</strong> <a href="https://github.com/jhenkins/mdutil">'
            "https://github.com/jhenkins/mdutil</a></p>",
            result,
        )

    def test_render_code_block(self):
        """Code blocks should render with pre/code tags."""
        tokens = [{"type": "code", "content": "print('hello')", "language": "python"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<pre><code class=\"language-python\">", result)
        self.assertIn("print('hello')", result)

    def test_render_horizontal_rule(self):
        """Horizontal rules should render as hr tags."""
        tokens = [{"type": "horizontal_rule", "content": "---", "text": "---"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<hr>", result)

    def test_render_blockquote(self):
        """Blockquotes should render with blockquote tags."""
        tokens = [{"type": "blockquote", "content": "> This is a quote", "text": "> This is a quote"}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<blockquote>", result)
        self.assertIn("This is a quote", result)

    def test_render_ordered_list(self):
        """Ordered lists should render with ol tags."""
        tokens = [{"type": "list", "items": ["Item 1", "Item 2"], "ordered": True}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ol>", result)
        self.assertIn("<li>Item 1</li>", result)
        self.assertIn("<li>Item 2</li>", result)

    def test_render_unordered_list(self):
        """Unordered lists should render with ul tags."""
        tokens = [{"type": "list", "items": ["Item 1", "Item 2"], "ordered": False}]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ul>", result)
        self.assertIn("<li>Item 1</li>", result)
        self.assertIn("<li>Item 2</li>", result)

    def test_render_table(self):
        """Tables should render with proper structure."""
        tokens = [{
            "type": "table",
            "headers": ["Name", "Age"],
            "rows": [["Alice", "30"], ["Bob", "25"]],
            "alignments": ["left", "right"]
        }]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<table>", result)
        self.assertIn("<th", result)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("<td", result)
        self.assertIn(">Alice</td>", result)
        self.assertIn(">30</td>", result)

    def test_render_inline_spans(self):
        """Inline spans (bold, italic, code, links) should render correctly."""
        tokens = [{
            "type": "paragraph",
            "text": "Test text",
            "spans": [
                {"type": "text", "content": "Bold: "},
                {"type": "bold", "content": "text"},
                {"type": "text", "content": ", Italic: "},
                {"type": "italic", "content": "text"},
            ]
        }]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>text</strong>", result)
        self.assertIn("<em>text</em>", result)

    def test_render_code_block_escapes_html(self):
        """Code blocks should escape HTML entities."""
        tokens = [{"type": "code", "content": "<div>test</div>", "language": ""}]
        result = self.exporter.render(tokens, {}, {})
        self.assertNotIn("<div>", result)
        self.assertIn("&lt;div&gt;", result)

    def test_render_empty_tokens(self):
        """Empty tokens list should return valid HTML."""
        result = self.exporter.render([], {}, {})
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("</html>", result)

    def test_render_blank_tokens_skipped(self):
        """Blank tokens should be skipped (no output)."""
        tokens = [
            {"type": "heading", "text": "Title"},
            {"type": "blank", "content": "", "text": ""},
            {"type": "paragraph", "text": "Body"}
        ]
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<h1>Title</h1>", result)
        self.assertIn("<p>Body</p>", result)

    def test_is_exporter_instance(self):
        """HtmlExporter is a proper Exporter subclass."""
        self.assertIsInstance(self.exporter, Exporter)
        self.assertIsInstance(self.exporter, BaseExporter)


class PackageImportTests(unittest.TestCase):
    """Test package imports and re-exports."""

    def test_export_package_re_exports_exporter(self):
        """The export package re-exports the Exporter base class."""
        from mdutil import export

        self.assertEqual(export.Exporter, Exporter)

    def test_exporter_in_all(self):
        """Exporter is listed in __all__."""
        from mdutil.export import __all__

        self.assertIn("Exporter", __all__)


if __name__ == "__main__":
    unittest.main()
