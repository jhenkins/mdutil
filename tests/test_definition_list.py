"""Tests for KB-065 and KB-066: Definition lists (Term\n:   Definition)."""
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


class DefinitionParserTests(unittest.TestCase):
    """Parser tests for definition lists (KB-065)."""

    def test_parse_single_definition(self):
        """Single term with a single definition."""
        md = "Apple\n:   A fruit from the Malus genus."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(def_tokens[0]["terms"], ["Apple"])
        self.assertEqual(def_tokens[0]["definitions"], ["A fruit from the Malus genus."])
        self.assertEqual(def_tokens[0]["term_text"], "Apple")

    def test_parse_term_with_multiple_definitions(self):
        """Multiple definitions for the same term."""
        md = "Apple\n:   A fruit from the Malus genus.\n:   Also a tech company."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(def_tokens[0]["terms"], ["Apple"])
        self.assertEqual(len(def_tokens[0]["definitions"]), 2)
        self.assertEqual(def_tokens[0]["definitions"][0], "A fruit from the Malus genus.")
        self.assertEqual(def_tokens[0]["definitions"][1], "Also a tech company.")

    def test_parse_multiple_terms_shared_definition(self):
        """Multiple terms sharing a single definition."""
        md = "Apple\nBanana\n:   A fruit."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(def_tokens[0]["terms"], ["Apple", "Banana"])
        self.assertEqual(def_tokens[0]["definitions"], ["A fruit."])
        self.assertEqual(def_tokens[0]["term_text"], "Apple / Banana")

    def test_parse_multiple_definition_groups(self):
        """Multiple separate definition groups."""
        md = "Apple\n:   A fruit.\n\nBanana\n:   A yellow fruit."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 2)
        self.assertEqual(def_tokens[0]["terms"], ["Apple"])
        self.assertEqual(def_tokens[1]["terms"], ["Banana"])

    def test_parse_definition_after_paragraph(self):
        """Definition list appearing after a paragraph."""
        md = "This is a paragraph.\n\nTerm\n:   Definition."
        tokens = parse_markdown(md)
        para_tokens = [t for t in tokens if t["type"] == "paragraph"]
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(para_tokens), 1)
        self.assertEqual(len(def_tokens), 1)

    def test_parse_definition_before_paragraph(self):
        """Definition list appearing before a paragraph."""
        md = "Term\n:   Definition.\n\nThis is a paragraph."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        para_tokens = [t for t in tokens if t["type"] == "paragraph"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(len(para_tokens), 1)

    def test_parse_definition_with_inline_formatting(self):
        """Definition containing inline formatting like **bold**."""
        md = "Term\n:   **Bold** definition."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertIn("<strong>Bold</strong>", def_tokens[0]["content"])

    def test_parse_definition_with_code(self):
        """Definition containing inline code."""
        md = "Term\n:   Use `code` here."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertIn("<code>code</code>", def_tokens[0]["content"])

    def test_parse_definition_with_link(self):
        """Definition containing a link."""
        md = "Term\n:   Visit [example](https://example.com)."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 1)
        self.assertIn("<a", def_tokens[0]["content"])

    def test_parse_no_definition_for_single_line(self):
        """A single line that is not followed by a definition is a paragraph."""
        md = "Just a line."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 0)
        self.assertEqual(tokens[0]["type"], "paragraph")

    def test_parse_no_definition_for_colon_in_paragraph(self):
        """A line ending with colon is not a definition."""
        md = "This is a line that ends with a colon: and then more text."
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        self.assertEqual(len(def_tokens), 0)

    def test_parse_definition_followed_by_heading(self):
        """Definition list followed by a heading does not consume heading."""
        md = "Term\n:   Definition.\n\n# Heading"
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        heading_tokens = [t for t in tokens if t["type"] == "heading"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(len(heading_tokens), 1)

    def test_parse_definition_followed_by_list(self):
        """Definition list followed by a list does not consume list."""
        md = "Term\n:   Definition.\n\n- List item"
        tokens = parse_markdown(md)
        def_tokens = [t for t in tokens if t["type"] == "definition"]
        list_tokens = [t for t in tokens if t["type"] == "list"]
        self.assertEqual(len(def_tokens), 1)
        self.assertEqual(len(list_tokens), 1)


class DefinitionRendererTests(unittest.TestCase):
    """Renderer tests for definition lists (KB-066)."""

    def test_renderer_displays_term_and_definition(self):
        """Terminal renderer displays term and definition text."""
        md = "Apple\n:   A fruit."
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        self.assertIn("Apple", output)
        self.assertIn("A fruit.", output)
        self.assertNotIn("<strong>", output)
        self.assertNotIn("<em>", output)
        self.assertNotIn("<a ", output)

    def test_renderer_strips_inline_tags(self):
        """Terminal renderer strips inline tags."""
        md = "Term\n:   **Bold** definition."
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        self.assertNotIn("<strong>", output)
        self.assertIn("Bold", output)

    def test_renderer_with_multiple_definitions(self):
        """Terminal renderer handles multiple definitions."""
        md = "Apple\n:   A fruit.\n:   A tech company."
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        self.assertIn("A fruit.", output)
        self.assertIn("A tech company.", output)

    def test_renderer_with_multiple_terms(self):
        """Terminal renderer handles multiple terms sharing a definition."""
        md = "Apple\nBanana\n:   A fruit."
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        self.assertIn("Apple", output)
        self.assertIn("Banana", output)
        self.assertIn("A fruit.", output)


class DefinitionExporterTests(unittest.TestCase):
    """Exporter tests for definition lists (KB-066)."""

    def test_html_export_definition(self):
        """HTML exporter renders definition lists."""
        from mdutil.export.html import HtmlExporter

        md = "Apple\n:   A fruit."
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<dl>", html)
        self.assertIn("<dt>", html)
        self.assertIn("<dd>", html)
        self.assertIn("Apple", html)
        self.assertIn("A fruit.", html)
        self.assertIn("</dl>", html)

    def test_html_export_multiple_definitions(self):
        """HTML exporter handles multiple definitions."""
        from mdutil.export.html import HtmlExporter

        md = "Apple\n:   A fruit.\n:   A tech company."
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        # Count <dd> elements
        dd_count = html.count("<dd>")
        self.assertEqual(dd_count, 2)

    def test_html_export_multiple_terms(self):
        """HTML exporter handles multiple terms."""
        from mdutil.export.html import HtmlExporter

        md = "Apple\nBanana\n:   A fruit."
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("Apple", html)
        self.assertIn("Banana", html)
        self.assertIn("</dl>", html)

    def test_html_export_strips_inline_tags(self):
        """HTML exporter preserves inline formatting."""
        from mdutil.export.html import HtmlExporter

        md = "Term\n:   **Bold** definition."
        tokens = parse_markdown(md)
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<strong>Bold</strong>", html)

    def test_pdf_export_definition(self):
        """PDF exporter renders definition lists."""
        from mdutil.export.pdf import PdfExporter

        md = "Apple\n:   A fruit."
        tokens = parse_markdown(md)
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)


if __name__ == "__main__":
    unittest.main()
