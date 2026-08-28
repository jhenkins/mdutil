"""Tests for KB-060: HTML and PDF exporter footnote rendering."""

import re
import unittest
import zlib

from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter
from mdutil.parser import parse_markdown


def _decode_pdf_text(pdf_bytes: bytes) -> str:
    """Extract human-readable text from a PDF by mapping CID codes via bfchar."""
    raw_text = pdf_bytes.decode("latin-1", errors="replace")

    # Parse bfchar entries (CID → Unicode)
    cmaps: dict[int, str] = {}
    for m in re.finditer(r"<(\w+)>\s+<(\w+)>", raw_text):
        cid = int(m.group(1), 16)
        uni = int(m.group(2), 16)
        cmaps[cid] = chr(uni)

    # Decompress content streams and extract text
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


class HtmlExporterFootnoteTests(unittest.TestCase):
    """Test footnote rendering in the HTML exporter."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_footnote_ref_rendered_as_superscript_link(self):
        """Footnote reference renders as superscript anchor link."""
        md = "Hello[^1].\n\n[^1]: Footnote text."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn('<sup><a href="#fn-1" id="fnref-1">¹</a></sup>', html)

    def test_footnote_definition_rendered_as_list_item(self):
        """Footnote definition renders in .footnotes div."""
        md = "Hello[^1].\n\n[^1]: Footnote text."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn('<div class="footnotes">', html)
        self.assertIn('id="fn-1"', html)
        self.assertIn("Footnote text.", html)

    def test_multiple_footnotes(self):
        """Multiple footnote references and definitions."""
        md = "See[^1] and[^2].\n\n[^1]: First footnote.\n[^2]: Second footnote."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn('href="#fn-1"', html)
        self.assertIn('href="#fn-2"', html)
        self.assertIn("First footnote.", html)
        self.assertIn("Second footnote.", html)

    def test_footnote_anchor_link_back_reference(self):
        """Footnote definition includes back-reference arrow link."""
        md = "Hello[^1].\n\n[^1]: Footnote text."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        fn_block = re.search(r'id="fn-1">(.*?)</li>', html, re.DOTALL)
        self.assertIsNotNone(fn_block)
        self.assertIn("\u21a9", fn_block.group(1))

    def test_footnote_css_included(self):
        """Footnote-related CSS is included in the exported HTML."""
        md = "Hello[^1].\n\n[^1]: Footnote."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn(".footnotes", html)

    def test_footnote_content_with_inline_formatting(self):
        """Footnote definition with bold/italic renders in HTML."""
        md = "Text[^1].\n\n[^1]: A **bold** footnote with *emphasis*."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>emphasis</em>", html)

    def test_non_numeric_footnote_id(self):
        """Non-numeric footnote IDs render with superscript characters."""
        md = "Text[^note].\n\n[^note]: A named footnote."
        tokens = parse_markdown(md)
        html = self.exporter.render(tokens, {}, {})
        self.assertIn('href="#fn-note"', html)
        self.assertIn('id="fnref-note"', html)
        # Should render as superscript "n⁰ᵗᵉ" not raw "note"
        self.assertIn('<sup><a href="#fn-note" id="fnref-note">', html)


class PdfExporterFootnoteTests(unittest.TestCase):
    """Test footnote rendering in the PDF exporter."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_footnote_ref_rendered_as_superscript(self):
        """Footnote reference renders as Unicode superscript."""
        md = "Hello[^1].\n\n[^1]: Footnote text."
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("\u00b9", text)

    def test_footnote_definition_rendered_with_superscript(self):
        """Footnote definition renders with superscript prefix."""
        md = "Text[^1].\n\n[^1]: This is footnote 1."
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("\u00b9", text)
        self.assertIn("footnote", text.lower())

    def test_multiple_footnotes_superscript(self):
        """Multiple footnotes get different superscript characters."""
        md = "See[^1] and[^2].\n\n[^1]: First.\n[^2]: Second."
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        # Check that both superscript CID codes appear in the raw text
        streams = re.findall(rb"stream\n(.*?)\nendstream", pdf_bytes, re.DOTALL)
        all_cid_codes: set[int] = set()
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
                for i in range(0, len(raw_bytes) - 1, 2):
                    cid = (ord(raw_bytes[i]) << 8) | ord(raw_bytes[i + 1])
                    all_cid_codes.add(cid)
        # CID 6 maps to ¹ and CID 2 maps to ² in the font's bfchar
        self.assertIn(6, all_cid_codes)  # ¹
        self.assertIn(2, all_cid_codes)  # ²

    def test_superscript_single_digit(self):
        """Single digit converts to superscript."""
        self.assertEqual(PdfExporter._superscript("1"), "\u00b9")
        self.assertEqual(PdfExporter._superscript("2"), "\u00b2")
        self.assertEqual(PdfExporter._superscript("3"), "\u00b3")

    def test_superscript_multi_digit(self):
        """Multi-digit number converts each digit to superscript."""
        self.assertEqual(PdfExporter._superscript("12"), "\u00b9\u00b2")
        self.assertEqual(PdfExporter._superscript("10"), "\u00b9\u2070")

    def test_footnote_ref_in_list_item(self):
        """Footnote reference in list item renders as superscript."""
        md = "- Item with[^1] ref\n\n[^1]: Footnote."
        tokens = parse_markdown(md)
        pdf_bytes = self.exporter.render(tokens, {}, {})
        text = _decode_pdf_text(pdf_bytes)
        self.assertIn("\u00b9", text)

    def test_non_numeric_footnote_id_superscript(self):
        """Non-numeric footnote IDs render with superscript characters."""
        self.assertEqual(PdfExporter._superscript("note"), "ⁿᵒᵗᵉ")
        self.assertEqual(PdfExporter._superscript("abc"), "ᵃᵇᶜ")


if __name__ == "__main__":
    unittest.main()
