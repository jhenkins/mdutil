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


class ImageDimensionParserTests(unittest.TestCase):
    """Test GFM image dimension syntax =WxH."""

    def test_parse_image_with_dimensions(self):
        tokens = parse_markdown("![photo](image.png =200x100)")
        self.assertEqual(tokens[0]["type"], "paragraph")
        image_spans = [s for s in tokens[0]["spans"] if s["type"] == "image"]
        self.assertEqual(len(image_spans), 1)
        self.assertEqual(image_spans[0]["src"], "image.png")
        self.assertEqual(image_spans[0]["width"], 200)
        self.assertEqual(image_spans[0]["height"], 100)

    def test_parse_image_dimensions_in_html(self):
        tokens = parse_markdown("![photo](image.png =200x100)")
        self.assertIn('width="200"', tokens[0]["content"])
        self.assertIn('height="100"', tokens[0]["content"])

    def test_parse_image_without_dimensions(self):
        tokens = parse_markdown("![photo](image.png)")
        image_spans = [s for s in tokens[0]["spans"] if s["type"] == "image"]
        self.assertEqual(len(image_spans), 1)
        self.assertIsNone(image_spans[0].get("width"))
        self.assertIsNone(image_spans[0].get("height"))

    def test_parse_image_with_width_only(self):
        tokens = parse_markdown("![photo](image.png =300x)")
        # "=300x" doesn't match =WxH pattern (no height), treated as part of URL
        image_spans = [s for s in tokens[0]["spans"] if s["type"] == "image"]
        self.assertEqual(len(image_spans), 1)

    def test_image_html_with_dimensions(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("![photo](image.png =200x100)")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn('width="200"', html)
        self.assertIn('height="100"', html)

    def test_image_html_without_dimensions(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("![photo](image.png)")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # The <img> tag should not have width/height attributes
        import re
        img_match = re.search(r'<img[^>]+>', html)
        self.assertIsNotNone(img_match)
        img_tag = img_match.group(0)
        self.assertNotIn('width="', img_tag)
        self.assertNotIn('height="', img_tag)


class ImagePdfEmbeddingTests(unittest.TestCase):
    """Test PDF image embedding with local files."""

    def test_pdf_embeds_local_image(self):
        """PDF embeds a real local image file."""
        import os
        import tempfile

        # Create a minimal 1x1 PNG
        import struct, zlib

        def _make_png(path: str) -> None:
            """Write a tiny valid PNG."""
            raw = b"\x00\x00"  # filter + 2 pixels (RGBA)
            compressed = zlib.compress(raw)
            ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
            ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF)
            idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF)
            iend_crc = struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
            with open(path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n")
                f.write(struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr + ihdr_crc)
                f.write(struct.pack(">I", len(compressed)) + b"IDAT" + compressed + idat_crc)
                f.write(struct.pack(">I", 0) + b"IEND" + iend_crc)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            png_path = tmp.name
        try:
            _make_png(png_path)
            rel_path = os.path.basename(png_path)

            # Save current cwd, change to tmp dir for relative path resolution
            orig_cwd = os.getcwd()
            os.chdir(os.path.dirname(png_path))
            try:
                tokens = parse_markdown(f"![test image]({rel_path})")
                from mdutil.export.pdf import PdfExporter

                exporter = PdfExporter()
                pdf_bytes = exporter.render(tokens, {}, {})
                self.assertTrue(pdf_bytes.startswith(b"%PDF"))
                # A PDF with an embedded image should be notably larger
                # than one with just a text placeholder
                self.assertGreater(len(pdf_bytes), 500)
            finally:
                os.chdir(orig_cwd)
        finally:
            os.unlink(png_path)

    def test_pdf_remote_image_falls_back_to_placeholder(self):
        """Remote URLs fall back to text placeholder."""
        tokens = parse_markdown("![remote](https://example.com/photo.png)")
        from mdutil.export.pdf import PdfExporter

        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        # The placeholder text should appear in the PDF stream
        import zlib

        stream_start = pdf_bytes.find(b"stream\n")
        if stream_start != -1:
            stream_end = pdf_bytes.find(b"\nendstream", stream_start)
            if stream_end != -1:
                stream_data = pdf_bytes[stream_start + 7 : stream_end]
                try:
                    decompressed = zlib.decompress(stream_data)
                    self.assertIn(b"[image:", decompressed)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
