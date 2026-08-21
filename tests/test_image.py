"""Tests for KB-067/068: Image syntax parsing and terminal rendering."""
import unittest

from mdutil.parser import parse_markdown


class ImageParserTests(unittest.TestCase):
    def test_parse_basic_image(self):
        tokens = parse_markdown("![alt text](https://example.com/image.png)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="https://example.com/image.png" alt="alt text">', tokens[0]["content"])
        self.assertIn(
            {"type": "image", "text": "alt text", "src": "https://example.com/image.png"},
            tokens[0]["spans"],
        )

    def test_parse_image_with_local_url(self):
        tokens = parse_markdown("![logo](./logo.svg)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="./logo.svg" alt="logo">', tokens[0]["content"])
        self.assertIn(
            {"type": "image", "text": "logo", "src": "./logo.svg"},
            tokens[0]["spans"],
        )

    def test_parse_image_with_empty_alt(self):
        tokens = parse_markdown("![](https://example.com/empty.png)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="https://example.com/empty.png" alt="">', tokens[0]["content"])
        self.assertIn(
            {"type": "image", "text": "", "src": "https://example.com/empty.png"},
            tokens[0]["spans"],
        )

    def test_parse_image_with_bold_alt(self):
        tokens = parse_markdown("![**bold alt**](https://example.com/bold.png)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="https://example.com/bold.png" alt="<strong>bold alt</strong>">', tokens[0]["content"])

    def test_parse_image_with_inline_formatting_in_alt(self):
        tokens = parse_markdown("![alt **bold** and *em*](https://example.com/nested.png)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="https://example.com/nested.png"', tokens[0]["content"])

    def test_parse_image_in_paragraph_with_text(self):
        tokens = parse_markdown("Before ![alt](url) after")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("Before ", tokens[0]["content"])
        self.assertIn('<img src="url" alt="alt">', tokens[0]["content"])
        self.assertIn(" after", tokens[0]["content"])

    def test_parse_multiple_images_in_paragraph(self):
        tokens = parse_markdown("![a](url1) and ![b](url2)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="url1" alt="a">', tokens[0]["content"])
        self.assertIn('<img src="url2" alt="b">', tokens[0]["content"])
        image_spans = [s for s in tokens[0]["spans"] if s["type"] == "image"]
        self.assertEqual(len(image_spans), 2)

    def test_parse_image_not_confused_with_link(self):
        tokens = parse_markdown("![](https://example.com/img.png) and [link text](https://example.com)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        # Should contain both image and link
        self.assertIn("<img", tokens[0]["content"])
        self.assertIn('<a href="https://example.com">', tokens[0]["content"])

    def test_parse_escaped_image(self):
        tokens = parse_markdown(r"Literal \![](not-an-image.png)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<img", tokens[0]["content"])

    def test_parse_image_without_closing_paren(self):
        tokens = parse_markdown("![alt](https://example.com/broken")
        self.assertEqual(tokens[0]["type"], "paragraph")
        # Should not parse as image (no closing paren)
        self.assertNotIn("<img", tokens[0]["content"])

    def test_parse_image_with_spaces_in_url(self):
        tokens = parse_markdown('![alt](https://example.com/path "title")')
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<img src="https://example.com/path', tokens[0]["content"])


class ImageRendererTests(unittest.TestCase):
    def test_render_image_strips_img_tag(self):
        from mdutil.renderer import render

        tokens = parse_markdown("![alt text](https://example.com/image.png)")
        output = render(tokens, theme="colored")
        # Should not contain raw HTML tags
        self.assertNotIn("<img", output)
        # Should contain image placeholder
        self.assertIn("[image: alt text]", output)

    def test_render_image_with_empty_alt(self):
        from mdutil.renderer import render

        tokens = parse_markdown("![](https://example.com/empty.png)")
        output = render(tokens, theme="colored")
        self.assertNotIn("<img", output)
        # Empty alt falls back to showing URL
        self.assertIn("[image:", output)

    def test_render_image_with_local_path(self):
        from mdutil.renderer import render

        tokens = parse_markdown("![logo](./logo.svg)")
        output = render(tokens, theme="colored")
        self.assertIn("[image: logo]", output)

    def test_render_image_in_paragraph(self):
        from mdutil.renderer import render

        tokens = parse_markdown("Before ![alt](url) after")
        output = render(tokens, theme="colored")
        self.assertNotIn("<img", output)
        self.assertIn("[image: alt]", output)

    def test_render_image_not_confused_with_link(self):
        from mdutil.renderer import render

        tokens = parse_markdown("![alt](url) and [link](href)")
        output = render(tokens, theme="colored")
        self.assertNotIn("<img", output)
        self.assertNotIn("<a", output)
        # Both should be rendered as placeholders
        self.assertIn("[image: alt]", output)
        self.assertIn("link (href)", output)

    def test_render_multiple_images(self):
        from mdutil.renderer import render

        tokens = parse_markdown("![a](url1) and ![b](url2)")
        output = render(tokens, theme="colored")
        self.assertNotIn("<img", output)
        self.assertIn("[image: a]", output)
        self.assertIn("[image: b]", output)


class ImageExporterTests(unittest.TestCase):
    def test_image_html_export(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("![alt text](https://example.com/image.png)")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # HTML should contain <img> tag
        self.assertIn('<img src="https://example.com/image.png"', html)
        self.assertIn('alt="alt text"', html)

    def test_image_html_export_empty_alt(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("![](https://example.com/empty.png)")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn('<img src="https://example.com/empty.png"', html)

    def test_image_pdf_export(self):
        from mdutil.export.pdf import PdfExporter

        tokens = parse_markdown("![alt text](https://example.com/image.png)")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        # PDF should be valid (start with %PDF) and non-empty
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)


if __name__ == "__main__":
    unittest.main()
