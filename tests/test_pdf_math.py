"""Tests for KB-099: PDF math notation rendered in a monospace font.

The parser emits ``<math>content</math>`` for ``$...$`` math. The PDF
exporter must render that content in a monospace font (per the spec:
"PDF: mono font") rather than leaving it in the default text font.
"""
import unittest
from typing import Any, cast

from mdutil.export.pdf import PdfExporter, _InlineHTMLParser
from mdutil.parser import parse_markdown


class _FakePdf:
    """Minimal PDF stand-in that records set_font/write calls."""

    l_margin = 20

    def __init__(self) -> None:
        self.font_calls: list[tuple[str, str, float]] = []
        self.writes: list[tuple[str, str]] = []

    def set_x(self, x: float) -> None:
        pass

    def set_font(self, family: str, style: str = "", size: float = 0) -> None:
        self.font_calls.append((family, style, size))

    def set_text_color(self, *args: Any, **kwargs: Any) -> None:
        pass

    def write(self, h: float, text: str, link: str = "") -> None:
        self.writes.append((text, link))

    def ln(self, amount: float = 0) -> None:
        pass


class MathInlineParserTests(unittest.TestCase):
    def test_math_tag_sets_math_flag(self):
        """_InlineHTMLParser flags <math> segments for mono rendering."""
        parser = _InlineHTMLParser()
        parser.feed("<math>E=mc^2</math>")
        segs = [s for s in parser.segments if s.get("text")]
        self.assertEqual(len(segs), 1)
        self.assertTrue(segs[0]["math"])

    def test_non_math_segment_not_flagged(self):
        parser = _InlineHTMLParser()
        parser.feed("plain text")
        segs = [s for s in parser.segments if s.get("text")]
        self.assertFalse(segs[0]["math"])


class MathPdfRenderTests(unittest.TestCase):
    def test_math_renders_in_mono_font(self):
        """PDF export renders math content in a monospace font."""
        exporter = PdfExporter()
        exporter._use_unicode = False
        fake = _FakePdf()
        tokens = parse_markdown("Eq: $E=mc^2$")
        exporter._render_paragraph(cast(Any, fake), tokens[0])
        self.assertTrue(
            any(family == "Courier" for family, _style, _size in fake.font_calls)
        )
        self.assertTrue(any(text == "E=mc²" for text, _link in fake.writes))

    def test_plain_text_uses_regular_font(self):
        """Non-math text still renders in the regular (non-mono) font."""
        exporter = PdfExporter()
        exporter._use_unicode = False
        fake = _FakePdf()
        tokens = parse_markdown("Just text.")
        exporter._render_paragraph(cast(Any, fake), tokens[0])
        self.assertTrue(
            any(family != "Courier" for family, _style, _size in fake.font_calls)
        )


if __name__ == "__main__":
    unittest.main()
