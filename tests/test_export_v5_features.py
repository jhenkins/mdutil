"""Comprehensive exporter tests for v5.0 new features (KB-079).

Tests HTML and PDF exporters for: strikethrough, task lists, math, footnotes,
subscript, superscript, highlight, definition lists, images, nested lists, and
link titles. Also covers cross-format consistency and combined features.
"""

import os
import re
import tempfile
import unittest
import zlib

from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter, _InlineHTMLParser
from mdutil.parser import parse_markdown


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_pdf_text(pdf_bytes: bytes) -> str:
    """Extract human-readable text from a PDF (shared helper)."""
    raw_text = pdf_bytes.decode("latin-1", errors="replace")
    cmaps: dict[int, str] = {}
    for m in re.finditer(r"<(\w+)>\s+<(\w+)>", raw_text):
        cid = int(m.group(1), 16)
        uni = int(m.group(2), 16)
        cmaps[cid] = chr(uni)
    streams = re.findall(rb"stream\n(.*?)\nendstream", pdf_bytes, re.DOTALL)
    parts: list[str] = []
    for raw in streams:
        try:
            decomp = zlib.decompress(raw)
        except Exception:
            continue
        text = decomp.decode("latin-1", errors="replace")
        for m in re.finditer(r"\(([^)]*)\)\s*Tj", text, re.DOTALL):
            raw_bytes = m.group(1)
            if isinstance(raw_bytes, bytes):
                raw_bytes = raw_bytes.decode("latin-1")
            decoded = ""
            for i in range(0, len(raw_bytes) - 1, 2):
                cid = (ord(raw_bytes[i]) << 8) | ord(raw_bytes[i + 1])
                decoded += cmaps.get(cid, f"[{cid}]")
            parts.append(decoded)
    return "".join(parts)


# ===========================================================================
# HTML Exporter: Strikethrough
# ===========================================================================

class HtmlExporterStrikethroughTests(unittest.TestCase):
    """Test HTML exporter rendering of strikethrough (~~text~~)."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_strikethrough_renders_del_tag(self):
        tokens = parse_markdown("This is ~~deleted~~ text.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<del>deleted</del>", result)

    def test_strikethrough_with_surrounding_text(self):
        tokens = parse_markdown("Before ~~middle~~ after.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("Before <del>middle</del> after.", result)

    def test_multiple_strikethroughs_in_one_line(self):
        tokens = parse_markdown("~~one~~ and ~~two~~ done.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<del>one</del>", result)
        self.assertIn("<del>two</del>", result)

    def test_strikethrough_nested_with_bold(self):
        tokens = parse_markdown("**~~bold strikethrough~~**")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>", result)
        self.assertIn("<del>", result)

    def test_strikethrough_empty_content(self):
        """Empty strikethrough (~~) should render without error."""
        tokens = parse_markdown("before ~~ after.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("before", result)

    def test_strikethrough_in_heading(self):
        tokens = parse_markdown("## ~~Obsolete~~ Heading")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<del>Obsolete</del>", result)


# ===========================================================================
# HTML Exporter: Task Lists
# ===========================================================================

class HtmlExporterTaskListTests(unittest.TestCase):
    """Test HTML exporter rendering of task list checkboxes."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_checked_task_renders_checkbox(self):
        tokens = parse_markdown("- [x] Done task")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<input type="checkbox" checked disabled>', result)
        self.assertIn("Done task", result)

    def test_unchecked_task_renders_checkbox(self):
        tokens = parse_markdown("- [ ] Todo task")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<input type="checkbox" disabled>', result)
        self.assertIn("Todo task", result)

    def test_mixed_checked_unchecked_items(self):
        md = "- [x] Done\n- [ ] Todo\n- Regular item"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<input type="checkbox" checked disabled>', result)
        self.assertIn('<input type="checkbox" disabled>', result)
        # Regular item should not have a checkbox
        self.assertIn("<li>Regular item</li>", result)

    def test_task_list_uses_ul(self):
        tokens = parse_markdown("- [x] Task 1\n- [ ] Task 2")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ul>", result)
        self.assertIn("</ul>", result)

    def test_task_items_in_list_tags(self):
        tokens = parse_markdown("- [x] Task 1")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<li>", result)
        self.assertIn("</li>", result)

    def test_nested_task_list(self):
        md = "- [x] Parent\n  - [ ] Child"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<input type="checkbox" checked disabled>', result)
        self.assertIn('<input type="checkbox" disabled>', result)
        # Should have nested <ul>
        self.assertEqual(result.count("<ul>"), 2)


# ===========================================================================
# HTML Exporter: Math Notation
# ===========================================================================

class HtmlExporterMathTests(unittest.TestCase):
    """Test HTML exporter rendering of math notation."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_math_renders_math_tag(self):
        tokens = parse_markdown("Einstein said $E=mc^2$ here.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<math>E=mc^2</math>", result)

    def test_math_with_surrounding_text(self):
        tokens = parse_markdown("Before $x$ after.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("Before", result)
        self.assertIn("x", result)
        self.assertIn("after.", result)

    def test_multiple_math_expressions(self):
        tokens = parse_markdown("$a$ and $b$ together.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("a", result)
        self.assertIn("b", result)


# ===========================================================================
# HTML Exporter: Footnotes
# ===========================================================================

class HtmlExporterFootnoteTests(unittest.TestCase):
    """Test HTML exporter rendering of footnotes."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_footnote_ref_renders_sup_link(self):
        tokens = parse_markdown("Text with a reference[^1].\n\n[^1]: Footnote content.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sup>", result)
        self.assertIn('href="#fn-1"', result)
        self.assertIn('id="fnref-1"', result)

    def test_footnote_definition_renders_with_anchor(self):
        tokens = parse_markdown("Text[^1].\n\n[^1]: Footnote content.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('id="fn-1"', result)
        self.assertIn("Footnote content", result)
        self.assertIn('<div class="footnotes">', result)

    def test_footnote_back_link(self):
        tokens = parse_markdown("Text[^1].\n\n[^1]: Content.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("fnref-1", result)
        self.assertIn("fn-1", result)

    def test_multiple_footnotes(self):
        md = "Text[^1] and[^2].\n\n[^1]: First.\n[^2]: Second."
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('href="#fn-1"', result)
        self.assertIn('href="#fn-2"', result)
        self.assertIn("First.", result)
        self.assertIn("Second.", result)

    def test_footnote_with_inline_formatting(self):
        md = "Text[^1].\n\n[^1]: **Bold** footnote text."
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>Bold</strong>", result)


# ===========================================================================
# HTML Exporter: Subscript
# ===========================================================================

class HtmlExporterSubscriptTests(unittest.TestCase):
    """Test HTML exporter rendering of subscript (~text~)."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_subscript_renders_sub_tag(self):
        tokens = parse_markdown("H~2~O")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sub>2</sub>", result)

    def test_subscript_with_surrounding_text(self):
        tokens = parse_markdown("Water is H~2~O.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sub>2</sub>", result)
        self.assertIn("Water", result)
        self.assertIn("O.", result)

    def test_multiple_subscripts(self):
        tokens = parse_markdown("C~6~H~12~O~6~")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sub>6</sub>", result)
        self.assertIn("<sub>12</sub>", result)


# ===========================================================================
# HTML Exporter: Superscript
# ===========================================================================

class HtmlExporterSuperscriptTests(unittest.TestCase):
    """Test HTML exporter rendering of superscript (^text^)."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_superscript_renders_sup_tag(self):
        tokens = parse_markdown("x^2^")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sup>2</sup>", result)

    def test_superscript_with_surrounding_text(self):
        tokens = parse_markdown("The value is x^2^ here.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sup>2</sup>", result)

    def test_combined_sub_and_sup(self):
        tokens = parse_markdown("H~2~O and x^2^")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<sub>2</sub>", result)
        self.assertIn("<sup>2</sup>", result)


# ===========================================================================
# HTML Exporter: Highlight
# ===========================================================================

class HtmlExporterHighlightTests(unittest.TestCase):
    """Test HTML exporter rendering of highlight (==text==)."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_highlight_renders_mark_tag(self):
        tokens = parse_markdown("This is ==highlighted== text.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<mark>highlighted</mark>", result)

    def test_highlight_with_surrounding_text(self):
        tokens = parse_markdown("Before ==middle== after.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("Before", result)
        self.assertIn("<mark>middle</mark>", result)
        self.assertIn("after.", result)

    def test_multiple_highlights(self):
        tokens = parse_markdown("==one== and ==two== here.")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<mark>one</mark>", result)
        self.assertIn("<mark>two</mark>", result)

    def test_highlight_nested_with_bold(self):
        tokens = parse_markdown("**==bold highlight==**")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>", result)
        self.assertIn("<mark>", result)


# ===========================================================================
# HTML Exporter: Definition Lists
# ===========================================================================

class HtmlExporterDefinitionListTests(unittest.TestCase):
    """Test HTML exporter rendering of definition lists."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_definition_renders_dl_structure(self):
        tokens = parse_markdown("Apple\n:   A fruit")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<dl>", result)
        self.assertIn("<dt>", result)
        self.assertIn("<dd>", result)

    def test_definition_term_content(self):
        tokens = parse_markdown("Apple\n:   A fruit")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<dt>Apple</dt>", result)

    def test_definition_definition_content(self):
        tokens = parse_markdown("Apple\n:   A fruit")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<dd>A fruit</dd>", result)

    def test_multiple_terms_shared_definition(self):
        md = "Apple\nOrange\n:   A fruit"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("Apple", result)
        self.assertIn("Orange", result)

    def test_multiple_definitions(self):
        md = "Python\n:   A language\n:   A snake"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("A language", result)
        self.assertIn("A snake", result)

    def test_definition_inline_formatting(self):
        md = "Term\n:   **Bold** definition"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>Bold</strong>", result)


# ===========================================================================
# HTML Exporter: Images
# ===========================================================================

class HtmlExporterImageTests(unittest.TestCase):
    """Test HTML exporter rendering of images."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_image_renders_img_tag(self):
        tokens = parse_markdown("![alt text](image.png)")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<img src="image.png"', result)
        self.assertIn('alt="alt text"', result)

    def test_image_with_dimensions_parsed(self):
        tokens = parse_markdown("![alt](image.png =300x200)")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('width="300"', result)
        self.assertIn('height="200"', result)

    def test_image_with_width_and_height(self):
        tokens = parse_markdown("![alt](image.png =300x200)")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('width="300"', result)
        self.assertIn('height="200"', result)

    def test_image_empty_alt(self):
        tokens = parse_markdown("![](image.png)")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<img src="image.png"', result)
        self.assertIn('alt=""', result)


# ===========================================================================
# HTML Exporter: Nested Lists
# ===========================================================================

class HtmlExporterNestedListTests(unittest.TestCase):
    """Test HTML exporter rendering of nested lists."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_nested_list_two_levels(self):
        md = "- Level 1\n  - Level 2"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ul>", result)
        self.assertEqual(result.count("<ul>"), 2)

    def test_nested_list_three_levels(self):
        md = "- L1\n  - L2\n    - L3"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertEqual(result.count("<ul>"), 3)

    def test_nested_list_with_text(self):
        md = "- Item 1\n  - Sub item"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("Item 1", result)
        self.assertIn("Sub item", result)

    def test_ordered_nested_list(self):
        md = "1. First\n   1. Sub first"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ol>", result)
        self.assertEqual(result.count("<ol>"), 2)

    def test_mixed_nested_list(self):
        md = "- Unordered\n  1. Ordered sub"
        tokens = parse_markdown(md)
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("<ul>", result)
        self.assertIn("<ol>", result)


# ===========================================================================
# HTML Exporter: Link Titles
# ===========================================================================

class HtmlExporterLinkTitleTests(unittest.TestCase):
    """Test HTML exporter rendering of link titles."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_link_title_rendered(self):
        tokens = parse_markdown('[click](https://example.com "My Title")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('title="My Title"', result)

    def test_link_without_title_no_attribute(self):
        tokens = parse_markdown("[click](https://example.com)")
        result = self.exporter.render(tokens, {}, {})
        self.assertNotIn("title=", result)

    def test_title_html_escaping(self):
        tokens = parse_markdown('[click](https://example.com "A & B")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('title="A &amp; B"', result)


# ===========================================================================
# PDF Exporter: Strikethrough
# ===========================================================================

class PdfExporterStrikethroughTests(unittest.TestCase):
    """Test PDF exporter rendering of strikethrough."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_strikethrough_renders_text(self):
        tokens = parse_markdown("This is ~~deleted~~ text.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("deleted", text)

    def test_strikethrough_no_crash(self):
        """Strikethrough should not crash PDF rendering."""
        tokens = parse_markdown("~~deleted text~~")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


# ===========================================================================
# PDF Exporter: Task Lists
# ===========================================================================

class PdfExporterTaskListTests(unittest.TestCase):
    """Test PDF exporter rendering of task lists."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_task_list_renders(self):
        tokens = parse_markdown("- [x] Done\n- [ ] Todo")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("Done", text)
        self.assertIn("Todo", text)

    def test_task_list_with_regular_items(self):
        md = "- [x] Task\n- Regular"
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("Regular", text)


# ===========================================================================
# PDF Exporter: Math
# ===========================================================================

class PdfExporterMathTests(unittest.TestCase):
    """Test PDF exporter rendering of math notation."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_math_renders_text(self):
        tokens = parse_markdown("Einstein said $E=mc^2$ here.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("E=mc", text)

    def test_math_with_surrounding_text(self):
        tokens = parse_markdown("Before $x$ after.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


# ===========================================================================
# PDF Exporter: Footnotes
# ===========================================================================

class PdfExporterFootnoteTests(unittest.TestCase):
    """Test PDF exporter rendering of footnotes."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_footnote_renders(self):
        tokens = parse_markdown("Text with reference[^1].\n\n[^1]: Footnote content.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        # Footnote definitions render in PDF — just verify valid output
        self.assertGreater(len(pdf_bytes), 100)

    def test_footnote_definition_renders(self):
        tokens = parse_markdown("Some text[^1].\n\n[^1]: This is the footnote definition.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


# ===========================================================================
# PDF Exporter: Subscript
# ===========================================================================

class PdfExporterSubscriptTests(unittest.TestCase):
    """Test PDF exporter rendering of subscript."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_subscript_renders_text(self):
        tokens = parse_markdown("Water is H~2~O.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("H", text)
        self.assertIn("O", text)


# ===========================================================================
# PDF Exporter: Superscript
# ===========================================================================

class PdfExporterSuperscriptTests(unittest.TestCase):
    """Test PDF exporter rendering of superscript."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_superscript_renders_text(self):
        tokens = parse_markdown("The value x^2^ here.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("x", text)
        self.assertIn("2", text)


# ===========================================================================
# PDF Exporter: Highlight
# ===========================================================================

class PdfExporterHighlightTests(unittest.TestCase):
    """Test PDF exporter rendering of highlight."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_highlight_renders_text(self):
        tokens = parse_markdown("This is ==highlighted== text.")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("highlighted", text)


# ===========================================================================
# PDF Exporter: Definition Lists
# ===========================================================================

class PdfExporterDefinitionListTests(unittest.TestCase):
    """Test PDF exporter rendering of definition lists."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_definition_renders(self):
        tokens = parse_markdown("Apple\n:   A fruit")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("Apple", text)
        self.assertIn("A fruit", text)

    def test_multiple_definitions(self):
        md = "Python\n:   A language\n:   A snake"
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


# ===========================================================================
# PDF Exporter: Nested Lists
# ===========================================================================

class PdfExporterNestedListTests(unittest.TestCase):
    """Test PDF exporter rendering of nested lists."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_nested_list_renders(self):
        md = "- Level 1\n  - Level 2\n    - Level 3"
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("Level 1", text)
        self.assertIn("Level 2", text)
        self.assertIn("Level 3", text)

    def test_nested_list_with_content(self):
        md = "- Item A\n  - Sub A\n- Item B"
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("Item A", text)
        self.assertIn("Sub A", text)
        self.assertIn("Item B", text)


# ===========================================================================
# PDF Exporter: Link Titles
# ===========================================================================

class PdfExporterLinkTitleTests(unittest.TestCase):
    """Test PDF exporter rendering of link titles."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_link_with_title_renders(self):
        tokens = parse_markdown('[click](https://example.com "My Title")')
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


# ===========================================================================
# PDF InlineHTMLParser: Span Handling
# ===========================================================================

class PdfInlineHTMLParserTests(unittest.TestCase):
    """Test _InlineHTMLParser handles all v5.0 inline tags."""

    def test_parser_handles_del_tag(self):
        parser = _InlineHTMLParser()
        parser.feed("<del>deleted</del>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertEqual(parser.segments[0]["text"], "deleted")

    def test_parser_handles_mark_tag(self):
        parser = _InlineHTMLParser()
        parser.feed("<mark>highlighted</mark>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertEqual(parser.segments[0]["text"], "highlighted")

    def test_parser_handles_math_tag(self):
        parser = _InlineHTMLParser()
        parser.feed("<math>E=mc^2</math>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertEqual(parser.segments[0]["text"], "E=mc^2")

    def test_parser_handles_sub_tag(self):
        parser = _InlineHTMLParser()
        parser.feed("<sub>2</sub>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertEqual(parser.segments[0]["text"], "2")

    def test_parser_handles_sup_tag(self):
        parser = _InlineHTMLParser()
        parser.feed("<sup>2</sup>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertEqual(parser.segments[0]["text"], "2")

    def test_parser_handles_footnote_ref_tag(self):
        parser = _InlineHTMLParser()
        parser.feed('<span class="footnote_ref">1</span>')
        parser.close()
        self.assertTrue(len(parser.segments) >= 1)

    def test_parser_handles_nested_formatting(self):
        parser = _InlineHTMLParser()
        parser.feed("<strong><em>bold italic</em></strong>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertTrue(parser.segments[0]["strong"])
        self.assertTrue(parser.segments[0]["emphasis"])

    def test_parser_handles_code_in_del(self):
        parser = _InlineHTMLParser()
        parser.feed("<del><code>code</code></del>")
        parser.close()
        self.assertEqual(len(parser.segments), 1)
        self.assertTrue(parser.segments[0]["code"])

    def test_parser_handles_mixed_inline_tags(self):
        parser = _InlineHTMLParser()
        parser.feed("plain <sub>sub</sub> and <sup>sup</sup>")
        parser.close()
        texts = [s["text"] for s in parser.segments]
        self.assertIn("plain ", texts)
        self.assertIn("sub", texts)
        self.assertIn(" and ", texts)
        self.assertIn("sup", texts)


# ===========================================================================
# Cross-Format Consistency
# ===========================================================================

class CrossFormatConsistencyTests(unittest.TestCase):
    """Test that HTML and PDF produce consistent output for new features."""

    def setUp(self):
        self.html_exporter = HtmlExporter()
        self.pdf_exporter = PdfExporter()

    def _render_both(self, md: str) -> tuple[str, bytes]:
        tokens = parse_markdown(md)
        html = self.html_exporter.render(tokens, {}, {})
        pdf = self.pdf_exporter.render(tokens, {}, {})
        return html, pdf

    def test_strikethrough_consistency(self):
        html, pdf = self._render_both("~~deleted~~ text")
        self.assertIn("<del>deleted</del>", html)
        self.assertTrue(pdf.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf)
        self.assertIn("deleted", text)

    def test_math_consistency(self):
        html, pdf = self._render_both("$E=mc^2$")
        self.assertIn("E=mc^2", html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_highlight_consistency(self):
        html, pdf = self._render_both("==highlighted==")
        self.assertIn("<mark>highlighted</mark>", html)
        self.assertTrue(pdf.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf)
        self.assertIn("highlighted", text)

    def test_subscript_consistency(self):
        html, pdf = self._render_both("H~2~O")
        self.assertIn("<sub>2</sub>", html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_superscript_consistency(self):
        html, pdf = self._render_both("x^2^")
        self.assertIn("<sup>2</sup>", html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_task_list_consistency(self):
        html, pdf = self._render_both("- [x] Done")
        self.assertIn('<input type="checkbox" checked disabled>', html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_image_consistency(self):
        html, pdf = self._render_both("![alt](image.png)")
        self.assertIn('<img src="image.png"', html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_nested_list_consistency(self):
        html, pdf = self._render_both("- L1\n  - L2")
        self.assertEqual(html.count("<ul>"), 2)
        self.assertTrue(pdf.startswith(b"%PDF"))
        text = _decode_pdf_text(pdf)
        self.assertIn("L1", text)
        self.assertIn("L2", text)

    def test_link_title_consistency(self):
        html, pdf = self._render_both('[link](https://example.com "Title")')
        self.assertIn('title="Title"', html)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_complex_document(self):
        """A document with many features renders in both formats without error."""
        md = """# Title

This is **bold** and ~~strikethrough~~ and ==highlighted== text.

- [x] Task 1
- [ ] Task 2

Water is H~2~O and x^2^.

See $E=mc^2$ for more.

Apple
:   A fruit

[click](https://example.com "Example")

![alt](image.png)
"""
        tokens = parse_markdown(md)
        html = self.html_exporter.render(tokens, {}, {})
        pdf = self.pdf_exporter.render(tokens, {}, {})
        self.assertIn("<del>strikethrough</del>", html)
        self.assertIn("<mark>highlighted</mark>", html)
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
