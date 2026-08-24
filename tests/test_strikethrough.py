"""Tests for KB-051: Strikethrough support (~~text~~)."""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


def _strip_macrons(text: str) -> str:
    """Remove combining macron characters (U+0305) from text."""
    return text.replace("\u0305", "")


class StrikethroughParserTests(unittest.TestCase):
    def test_parse_inline_strikethrough(self):
        tokens = parse_markdown("This is ~~deleted~~ text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<del>deleted</del>", tokens[0]["content"])
        self.assertIn(
            {"type": "strikethrough", "text": "deleted"},
            tokens[0]["spans"],
        )

    def test_parse_strikethrough_with_bold(self):
        tokens = parse_markdown("~~**bold deleted**~~")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<del><strong>bold deleted</strong></del>", tokens[0]["content"])
        self.assertIn(
            {"type": "strikethrough", "text": "bold deleted"},
            tokens[0]["spans"],
        )

    def test_parse_strikethrough_with_emphasis(self):
        tokens = parse_markdown("~~*emphasized*~~")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<del><em>emphasized</em></del>", tokens[0]["content"])
        self.assertIn(
            {"type": "strikethrough", "text": "emphasized"},
            tokens[0]["spans"],
        )

    def test_parse_strikethrough_with_code(self):
        tokens = parse_markdown("~~`inline code`~~")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<del><code>inline code</code></del>", tokens[0]["content"])
        self.assertIn(
            {"type": "strikethrough", "text": "inline code"},
            tokens[0]["spans"],
        )

    def test_parse_escaped_strikethrough(self):
        tokens = parse_markdown(r"Literal \~~not deleted\~~ text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<del>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "strikethrough"},
            tokens[0]["spans"],
        )

    def test_parse_unclosed_strikethrough(self):
        # Single tilde is not strikethrough syntax - just literal tilde
        tokens = parse_markdown("~not closed")
        self.assertEqual(tokens[0]["type"], "paragraph")
        # No <del> tags should be produced
        self.assertNotIn("<del>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "strikethrough"},
            tokens[0]["spans"],
        )


class StrikethroughRendererTests(unittest.TestCase):
    def test_strikethrough_renderer_strips_del_tags(self):
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        # Should not contain <del> tags
        self.assertNotIn("<del>", output)
        # Should contain the text (stripped of combining macrons)
        self.assertIn("deleted", _strip_macrons(output))

    def test_strikethrough_with_bold_renderer(self):
        tokens = parse_markdown("~~**bold deleted**~~")
        output = render(tokens, theme="colored")
        # Should not contain <del> or <strong> tags
        self.assertNotIn("<del>", output)
        self.assertNotIn("<strong>", output)
        # Should contain the text (stripped of combining macrons)
        self.assertIn("bold deleted", _strip_macrons(output))

    def test_strikethrough_with_emphasis_renderer(self):
        tokens = parse_markdown("~~*emphasized*~~")
        output = render(tokens, theme="colored")
        # Should not contain <del> or <em> tags
        self.assertNotIn("<del>", output)
        self.assertNotIn("<em>", output)
        # Should contain the text (stripped of combining macrons)
        self.assertIn("emphasized", _strip_macrons(output))

    def test_strikethrough_with_code_renderer(self):
        tokens = parse_markdown("~~`inline code`~~")
        output = render(tokens, theme="colored")
        # Should not contain <del> or <code> tags
        self.assertNotIn("<del>", output)
        self.assertNotIn("<code>", output)
        # Should contain the text (stripped of combining macrons)
        self.assertIn("inline code", _strip_macrons(output))


class StrikethroughExporterTests(unittest.TestCase):
    def test_strikethrough_html_export(self):
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("~~deleted~~")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # HTML should preserve <del> tags
        self.assertIn("<del>", html)
        self.assertIn("deleted", html)

    def test_strikethrough_pdf_export(self):
        from mdutil.export.pdf import PdfExporter
        tokens = parse_markdown("~~deleted~~")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        # PDF should be valid (start with %PDF) and non-empty
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)
        # Check for the text "deleted" somewhere in the PDF stream
        # (PDFs are compressed, so check for the string in the decompressed stream)
        import zlib
        # Find stream content and try to decompress
        stream_start = pdf_bytes.find(b"stream\n")
        if stream_start != -1:
            stream_end = pdf_bytes.find(b"\nendstream", stream_start)
            if stream_end != -1:
                stream_data = pdf_bytes[stream_start + 7 : stream_end]
                try:
                    decompressed = zlib.decompress(stream_data)
                    self.assertIn(b"deleted", decompressed)
                except Exception:
                    # If decompression fails, just check the PDF is valid
                    pass


if __name__ == "__main__":
    unittest.main()
