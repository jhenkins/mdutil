"""Tests for KB-061/062: Subscript and superscript syntax."""
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render, _subscript, _superscript


class SubscriptParserTests(unittest.TestCase):
    def test_parse_basic_subscript(self):
        tokens = parse_markdown("Water is H~2~O")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sub>2</sub>", tokens[0]["content"])
        self.assertIn(
            {"type": "subscript", "text": "2"},
            tokens[0]["spans"],
        )

    def test_parse_subscript_with_text(self):
        tokens = parse_markdown("The ~sub~ text")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sub>sub</sub>", tokens[0]["content"])
        self.assertIn(
            {"type": "subscript", "text": "sub"},
            tokens[0]["spans"],
        )

    def test_parse_multiple_subscripts(self):
        tokens = parse_markdown("H~2~O and CO~2~")
        self.assertIn("<sub>2</sub>", tokens[0]["content"])
        sub_spans = [s for s in tokens[0]["spans"] if s["type"] == "subscript"]
        self.assertEqual(len(sub_spans), 2)

    def test_parse_escaped_subscript(self):
        tokens = parse_markdown(r"Literal \~not sub\~ text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<sub>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "subscript"},
            tokens[0]["spans"],
        )

    def test_parse_unclosed_subscript(self):
        tokens = parse_markdown("~not closed")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<sub>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "subscript"},
            tokens[0]["spans"],
        )

    def test_parse_subscript_with_bold(self):
        tokens = parse_markdown("~**bold sub**~")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sub><strong>bold sub</strong></sub>", tokens[0]["content"])

    def test_parse_subscript_with_emphasis(self):
        tokens = parse_markdown("~*em sub*~")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sub><em>em sub</em></sub>", tokens[0]["content"])


class SuperscriptParserTests(unittest.TestCase):
    def test_parse_basic_superscript(self):
        tokens = parse_markdown("x^2^ squared")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sup>2</sup>", tokens[0]["content"])
        self.assertIn(
            {"type": "superscript", "text": "2"},
            tokens[0]["spans"],
        )

    def test_parse_superscript_with_text(self):
        tokens = parse_markdown("e^x^ function")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sup>x</sup>", tokens[0]["content"])
        self.assertIn(
            {"type": "superscript", "text": "x"},
            tokens[0]["spans"],
        )

    def test_parse_multiple_superscripts(self):
        tokens = parse_markdown("x^2^ and y^3^")
        sup_spans = [s for s in tokens[0]["spans"] if s["type"] == "superscript"]
        self.assertEqual(len(sup_spans), 2)

    def test_parse_escaped_superscript(self):
        tokens = parse_markdown(r"Literal \^not super\^ here.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<sup>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "superscript"},
            tokens[0]["spans"],
        )

    def test_parse_unclosed_superscript(self):
        tokens = parse_markdown("^not closed")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<sup>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "superscript"},
            tokens[0]["spans"],
        )

    def test_parse_superscript_with_bold(self):
        tokens = parse_markdown("^**bold super**^")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sup><strong>bold super</strong></sup>", tokens[0]["content"])

    def test_parse_superscript_with_emphasis(self):
        tokens = parse_markdown("^*em super*^")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<sup><em>em super</em></sup>", tokens[0]["content"])


class SubscriptRendererTests(unittest.TestCase):
    def test_subscript_renderer_displays_unicode(self):
        tokens = parse_markdown("H~2~O")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sub>", output)
        self.assertIn("₂", output)

    def test_subscript_strips_tags(self):
        tokens = parse_markdown("~sub~")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sub>", output)
        self.assertNotIn("</sub>", output)
        self.assertIn("ₛᵤb", output)

    def test_subscript_with_bold_renderer(self):
        tokens = parse_markdown("~**bold sub**~")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sub>", output)
        self.assertNotIn("<strong>", output)
        # Text appears in subscript Unicode
        self.assertIn("ₛᵤb", output)

    def test_subscript_with_emphasis_renderer(self):
        tokens = parse_markdown("~*em sub*~")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sub>", output)
        self.assertNotIn("<em>", output)
        # Text appears in subscript Unicode
        self.assertIn("ₑₘ ₛᵤb", output)


class SuperscriptRendererTests(unittest.TestCase):
    def test_superscript_renderer_displays_unicode(self):
        tokens = parse_markdown("x^2^ squared")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sup>", output)
        self.assertIn("²", output)

    def test_superscript_strips_tags(self):
        tokens = parse_markdown("^sup^")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sup>", output)
        self.assertNotIn("</sup>", output)
        self.assertIn("ˢᵘᵖ", output)

    def test_superscript_with_bold_renderer(self):
        tokens = parse_markdown("^**bold super**^")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sup>", output)
        self.assertNotIn("<strong>", output)
        # Text appears in superscript Unicode
        self.assertIn("ˢᵘᵖᵉʳ", output)

    def test_superscript_with_emphasis_renderer(self):
        tokens = parse_markdown("^*em super*^")
        output = render(tokens, theme="colored")
        self.assertNotIn("<sup>", output)
        self.assertNotIn("<em>", output)
        # Text appears in superscript Unicode
        self.assertIn("ᵉᵐ", output)


class SubscriptUnicodeTests(unittest.TestCase):
    def test_subscript_digits(self):
        self.assertEqual(_subscript("123"), "₁₂₃")
        self.assertEqual(_subscript("0"), "₀")
        self.assertEqual(_subscript("9"), "₉")

    def test_subscript_letters(self):
        self.assertEqual(_subscript("ae"), "ₐₑ")
        self.assertEqual(_subscript("hij"), "ₕᵢⱼ")
        self.assertEqual(_subscript("xyz"), "ₓyz")

    def test_subscript_special(self):
        self.assertEqual(_subscript("-+"), "₋₊")
        self.assertEqual(_subscript("()"), "₍₎")

    def test_subscript_unmapped_chars(self):
        self.assertEqual(_subscript("J"), "J")
        self.assertEqual(_subscript(" "), " ")


class SuperscriptUnicodeTests(unittest.TestCase):
    def test_superscript_digits(self):
        self.assertEqual(_superscript("123"), "¹²³")
        self.assertEqual(_superscript("0"), "⁰")
        self.assertEqual(_superscript("9"), "⁹")

    def test_superscript_letters(self):
        self.assertEqual(_superscript("abc"), "ᵃᵇᶜ")
        self.assertEqual(_superscript("xyz"), "ˣʸᶻ")
        self.assertEqual(_superscript("AEIOU"), "ᴬᴱᴵᴼᵁ")

    def test_superscript_special(self):
        self.assertEqual(_superscript("-+"), "⁻⁺")
        self.assertEqual(_superscript("()"), "⁽⁾")

    def test_superscript_unmapped_chars(self):
        self.assertEqual(_superscript("12"), "¹²")
        self.assertEqual(_superscript(""), "")


class SubscriptExporterTests(unittest.TestCase):
    def test_subscript_html_export(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("H~2~O")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<sub>", html)
        self.assertIn("2", html)
        self.assertIn("</sub>", html)

    def test_subscript_pdf_export(self):
        from mdutil.export.pdf import PdfExporter

        tokens = parse_markdown("H~2~O")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)

    def test_superscript_html_export(self):
        from mdutil.export.html import HtmlExporter

        tokens = parse_markdown("x^2^")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<sup>", html)
        self.assertIn("2", html)
        self.assertIn("</sup>", html)

    def test_superscript_pdf_export(self):
        from mdutil.export.pdf import PdfExporter

        tokens = parse_markdown("x^2^")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)


if __name__ == "__main__":
    unittest.main()
