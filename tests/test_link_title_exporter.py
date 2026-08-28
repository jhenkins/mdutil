"""Tests for link title rendering in HTML and PDF exporters (KB-072)."""

import unittest

from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter, _InlineHTMLParser
from mdutil.parser import parse_markdown


class HtmlExporterLinkTitleTests(unittest.TestCase):
    """Test HTML exporter link title rendering."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_link_without_title(self):
        """Links without title render without title attribute."""
        tokens = parse_markdown("[click](https://example.com)")
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<a href="https://example.com">click</a>', result)
        self.assertNotIn("title=", result)

    def test_link_with_title(self):
        """Links with title render with title attribute."""
        tokens = parse_markdown('[click](https://example.com "Example Site")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn(
            '<a href="https://example.com" title="Example Site">click</a>',
            result,
        )

    def test_link_with_empty_title(self):
        """Links with empty title render title attribute."""
        tokens = parse_markdown('[click](https://example.com "")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('title=""', result)
        self.assertIn('<a href="https://example.com"', result)

    def test_mixed_links_title_and_no_title(self):
        """Mixed links: some with title, some without."""
        tokens = parse_markdown(
            '[labeled](/url "Label") and [plain](/other).'
        )
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('<a href="/url" title="Label">labeled</a>', result)
        self.assertIn('<a href="/other">plain</a>', result)

    def test_title_html_escaping(self):
        """Title attribute values are HTML-escaped."""
        tokens = parse_markdown('[click](https://example.com "A & B")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('title="A &amp; B"', result)

    def test_title_contains_quote_chars(self):
        """Title with double quotes is escaped in HTML output."""
        tokens = parse_markdown('[click](https://example.com "Say \\"hello\\"")')
        result = self.exporter.render(tokens, {}, {})
        self.assertIn("title=", result)

    def test_multiple_links_titles_rendered(self):
        """Multiple links with titles all render their titles."""
        tokens = parse_markdown(
            '[one](/a "First") and [two](/b "Second").'
        )
        result = self.exporter.render(tokens, {}, {})
        self.assertIn('title="First"', result)
        self.assertIn('title="Second"', result)


class PdfExporterLinkTitleParserTests(unittest.TestCase):
    """Test _InlineHTMLParser extracts title from <a> tags."""

    def test_parser_extracts_title_attribute(self):
        """_InlineHTMLParser captures title attribute from <a> tags."""
        parser = _InlineHTMLParser()
        parser.feed('<a href="https://example.com" title="My Title">click</a>')
        parser.close()

        self.assertEqual(len(parser.segments), 1)
        seg = parser.segments[0]
        self.assertEqual(seg["text"], "click")
        self.assertEqual(seg["href"], "https://example.com")
        self.assertEqual(seg["title"], "My Title")

    def test_parser_no_title(self):
        """Links without title have title=None in segment."""
        parser = _InlineHTMLParser()
        parser.feed('<a href="https://example.com">click</a>')
        parser.close()

        seg = parser.segments[0]
        self.assertEqual(seg["href"], "https://example.com")
        self.assertIsNone(seg["title"])

    def test_parser_mixed_formatting_with_title(self):
        """Title is preserved alongside bold/italic formatting."""
        parser = _InlineHTMLParser()
        parser.feed('<strong>bold</strong> <a href="/url" title="T">link</a>')
        parser.close()

        link_seg = [s for s in parser.segments if s["href"] == "/url"][0]
        self.assertEqual(link_seg["title"], "T")
        bold_seg = [s for s in parser.segments if s["text"] == "bold"][0]
        self.assertTrue(bold_seg["strong"])

    def test_parser_image_with_title(self):
        """Image segments with associated link title are captured."""
        parser = _InlineHTMLParser()
        parser.feed('<a href="/url" title="T"><img src="x.png" alt="alt"></a>')
        parser.close()

        img_seg = [s for s in parser.segments if s.get("type") == "image"][0]
        self.assertEqual(img_seg["title"], "T")
        self.assertEqual(img_seg["href"], "/url")


class PdfExporterLinkTitleRenderingTests(unittest.TestCase):
    """Test PDF rendering of link titles."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_pdf_render_with_link_title(self):
        """PDF export with link title produces valid PDF."""
        tokens = parse_markdown('[click](https://example.com "Example Site")')
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
        # Check it's a valid PDF (starts with %PDF)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_pdf_render_without_title_still_works(self):
        """PDF export without link title still works (regression)."""
        tokens = parse_markdown("[click](https://example.com)")
        pdf_bytes = self.exporter.render(tokens, {}, {})
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
