"""Tests for KB-063: Highlight syntax (==text==)."""
import unittest

from mdutil.parser import parse_markdown


class HighlightParserTests(unittest.TestCase):
    def test_parse_basic_highlight(self):
        tokens = parse_markdown("This is ==highlighted== text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark>highlighted</mark>", tokens[0]["content"])
        self.assertIn(
            {"type": "highlight", "text": "highlighted"},
            tokens[0]["spans"],
        )

    def test_parse_highlight_with_bold(self):
        tokens = parse_markdown("==**bold highlight**==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark><strong>bold highlight</strong></mark>", tokens[0]["content"])
        self.assertIn(
            {"type": "highlight", "text": "bold highlight"},
            tokens[0]["spans"],
        )

    def test_parse_highlight_with_emphasis(self):
        tokens = parse_markdown("==*emphasized*==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark><em>emphasized</em></mark>", tokens[0]["content"])
        self.assertIn(
            {"type": "highlight", "text": "emphasized"},
            tokens[0]["spans"],
        )

    def test_parse_highlight_with_code(self):
        tokens = parse_markdown("==`inline code`==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark><code>inline code</code></mark>", tokens[0]["content"])
        self.assertIn(
            {"type": "highlight", "text": "inline code"},
            tokens[0]["spans"],
        )

    def test_parse_highlight_with_subscript(self):
        tokens = parse_markdown("==~sub~ text==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark><sub>sub</sub> text</mark>", tokens[0]["content"])

    def test_parse_highlight_with_superscript(self):
        tokens = parse_markdown("==^super^ text==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark><sup>super</sup> text</mark>", tokens[0]["content"])

    def test_parse_multiple_highlights(self):
        tokens = parse_markdown("==first== and ==second==")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<mark>first</mark>", tokens[0]["content"])
        self.assertIn("<mark>second</mark>", tokens[0]["content"])
        highlight_spans = [s for s in tokens[0]["spans"] if s["type"] == "highlight"]
        self.assertEqual(len(highlight_spans), 2)

    def test_parse_escaped_highlight(self):
        tokens = parse_markdown(r"Literal \==not highlighted\== text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<mark>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "highlight"},
            tokens[0]["spans"],
        )

    def test_parse_unclosed_highlight(self):
        tokens = parse_markdown("==not closed")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<mark>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "highlight"},
            tokens[0]["spans"],
        )

    def test_parse_highlight_in_heading(self):
        tokens = parse_markdown("## ==highlighted== heading")
        self.assertEqual(tokens[0]["type"], "heading")
        # Headings pass through raw; inline not parsed in parser
        self.assertIn("==highlighted==", tokens[0]["content"])

    def test_parse_highlight_with_link(self):
        tokens = parse_markdown("==**bold and ==link==**==")
        # Inner == should close outer == — verify parser handles nested
        self.assertEqual(tokens[0]["type"], "paragraph")


class HighlightRendererTests(unittest.TestCase):
    def test_highlight_renderer_strips_mark_tags(self):
        from mdutil.renderer import render

        tokens = parse_markdown("==highlighted==")
        output = render(tokens, theme="colored")
        # Should not contain <mark> tags
        self.assertNotIn("<mark>", output)
        # Should contain the text
        self.assertIn("highlighted", output)

    def test_highlight_with_bold_renderer(self):
        from mdutil.renderer import render

        tokens = parse_markdown("==**bold highlight**==")
        output = render(tokens, theme="colored")
        # Should not contain <mark> or <strong> tags
        self.assertNotIn("<mark>", output)
        self.assertNotIn("<strong>", output)
        # Should contain the text
        self.assertIn("bold highlight", output)

    def test_highlight_with_emphasis_renderer(self):
        from mdutil.renderer import render

        tokens = parse_markdown("==*emphasized*==")
        output = render(tokens, theme="colored")
        # Should not contain <mark> or <em> tags
        self.assertNotIn("<mark>", output)
        self.assertNotIn("<em>", output)
        # Should contain the text
        self.assertIn("emphasized", output)


class HighlightExporterTests(unittest.TestCase):
    def test_highlight_html_export(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("==highlighted==")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # HTML should contain <mark> tags
        self.assertIn("<mark>", html)
        self.assertIn("highlighted", html)
        self.assertIn("</mark>", html)

    def test_highlight_pdf_export(self):
        from mdutil.export.pdf import PdfExporter

        tokens = parse_markdown("==highlighted==")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        # PDF should be valid (start with %PDF) and non-empty
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)


if __name__ == "__main__":
    unittest.main()
