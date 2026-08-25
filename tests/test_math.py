"""Tests for KB-055/056: Math notation detection and rendering ($...$)."""
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


class MathParserTests(unittest.TestCase):
    def test_parse_inline_math_basic(self):
        tokens = parse_markdown("The equation $E=mc^2$ is famous.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<math>E=mc^2</math>", tokens[0]["content"])
        self.assertIn(
            {"type": "math", "text": "E=mc^2"},
            tokens[0]["spans"],
        )

    def test_parse_inline_math_with_text(self):
        tokens = parse_markdown("Let $x$ be a variable.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<math>x</math>", tokens[0]["content"])
        self.assertIn(
            {"type": "math", "text": "x"},
            tokens[0]["spans"],
        )

    def test_parse_multiple_math_expressions(self):
        tokens = parse_markdown("$a$ and $b$ are variables.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<math>a</math>", tokens[0]["content"])
        self.assertIn("<math>b</math>", tokens[0]["content"])
        self.assertEqual(len(tokens[0]["spans"]), 2)

    def test_parse_math_with_inline_code(self):
        tokens = parse_markdown("Use `$code$` literally.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        # Code should shield the $ signs
        self.assertNotIn("<math>", tokens[0]["content"])
        self.assertIn("<code>$code$</code>", tokens[0]["content"])

    def test_parse_escaped_math(self):
        tokens = parse_markdown(r"Literal \$not math\$ text.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertNotIn("<math>", tokens[0]["content"])
        self.assertNotIn(
            {"type": "math"},
            tokens[0]["spans"],
        )

    def test_parse_math_with_mathml(self):
        tokens = parse_markdown("MathML: $<mrow><mi>x</mi><mo>=</mo><mn>2</mn></mrow>$")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<math>", tokens[0]["content"])
        self.assertIn("</math>", tokens[0]["content"])


class MathRendererTests(unittest.TestCase):
    def test_math_renderer_displays_content(self):
        tokens = parse_markdown("$E=mc^2$")
        output = render(tokens, theme="colored")
        # Should not contain <math> tags
        self.assertNotIn("<math>", output)
        # Should contain the math content
        self.assertIn("E=mc^2", output)

    def test_math_with_text_renderer(self):
        tokens = parse_markdown("The equation $E=mc^2$ is famous.")
        output = render(tokens, theme="colored")
        self.assertNotIn("<math>", output)
        self.assertIn("E=mc^2", output)

    def test_math_fallback_raw(self):
        """math_fallback=True renders $...$ delimiters around math content."""
        tokens = parse_markdown("The equation $E=mc^2$ is famous.")
        output = render(tokens, math_fallback=True)
        plain = self._strip_ansi(output)
        self.assertIn("$E=mc^2$", plain)
        self.assertNotIn("<math>", plain)

    def test_math_no_fallback_strips_tags(self):
        """Default (no fallback) strips <math> tags and shows plain content."""
        tokens = parse_markdown("The equation $E=mc^2$ is famous.")
        output = render(tokens, math_fallback=False)
        plain = self._strip_ansi(output)
        self.assertNotIn("$E=mc^2$", plain)
        self.assertIn("E=mc^2", plain)

    @staticmethod
    def _strip_ansi(text: str) -> str:
        import re
        return re.sub(r"\x1b\[[0-9;]*m", "", text)


class MathExporterTests(unittest.TestCase):
    def test_math_html_export(self):
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("$E=mc^2$")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # HTML should preserve <math> tags or render appropriately
        self.assertIn("E=mc^2", html)

    def test_math_pdf_export(self):
        from mdutil.export.pdf import PdfExporter
        tokens = parse_markdown("$E=mc^2$")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        # PDF should be valid (start with %PDF) and non-empty
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)

    def test_math_html_export_uses_math_span(self):
        """HTML export renders math as <span class=\"math\">, not raw <math>."""
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("Eq: $E=mc^2$")
        html = HtmlExporter().render(tokens, {}, {})
        self.assertIn('<span class="math">E=mc^2</span>', html)
        self.assertNotIn("<math>", html)

    def test_math_html_export_escapes_special_chars(self):
        """HTML export escapes < > & inside math content."""
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("Compare $a < b$")
        html = HtmlExporter().render(tokens, {}, {})
        self.assertIn('<span class="math">a &lt; b</span>', html)
        self.assertNotIn("<math>", html)

    def test_math_html_export_no_raw_mathml_tag(self):
        """No raw <math> MathML tag leaks into HTML (browsers drop it empty)."""
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("$x$")
        html = HtmlExporter().render(tokens, {}, {})
        self.assertNotIn("<math>", html)



if __name__ == "__main__":
    unittest.main()
