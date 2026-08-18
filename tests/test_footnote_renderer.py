"""Tests for KB-059: Renderer footnotes display."""
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render, _superscript


class FootnoteRendererTests(unittest.TestCase):
    def test_footnote_reference_rendered_as_superscript(self):
        """Footnote reference [^1] is rendered as superscript ¹."""
        tokens = parse_markdown("Text[^1].")
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertNotIn("<fnref", output)

    def test_footnote_reference_multiple(self):
        """Multiple footnote references rendered as superscripts."""
        tokens = parse_markdown("First[^1] and second[^2].")
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertIn("²", output)

    def test_footnote_reference_with_text(self):
        """Footnote reference in paragraph with surrounding text."""
        tokens = parse_markdown("See here[^1] for details.")
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertIn("See here", output)
        self.assertIn("for details", output)

    def test_footnote_definition_rendered_indented(self):
        """Footnote definition is rendered with indentation."""
        md = "Text.\n\n[^1]: This is a footnote."
        tokens = parse_markdown(md)
        output = render(tokens)
        # Should have indentation (4 spaces)
        self.assertIn("    ¹", output)
        self.assertIn("This is a footnote", output)

    def test_footnote_definition_multiple(self):
        """Multiple footnote definitions rendered."""
        md = "Text.\n\n[^1]: First footnote.\n\n[^2]: Second footnote."
        tokens = parse_markdown(md)
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertIn("²", output)
        self.assertIn("First footnote", output)
        self.assertIn("Second footnote", output)

    def test_footnote_definition_with_inline_formatting(self):
        """Footnote definition with inline formatting rendered as plain text."""
        md = "Text.\n\n[^1]: A **bold** footnote with *emphasis*."
        tokens = parse_markdown(md)
        output = render(tokens)
        # Inline tags should be stripped
        self.assertNotIn("<strong>", output)
        self.assertNotIn("<em>", output)
        self.assertIn("bold", output)
        self.assertIn("emphasis", output)

    def test_superscript_function_basic(self):
        """_superscript converts single digit to superscript."""
        self.assertEqual(_superscript("1"), "¹")
        self.assertEqual(_superscript("2"), "²")
        self.assertEqual(_superscript("3"), "³")

    def test_superscript_function_multiple_digits(self):
        """_superscript converts multi-digit numbers."""
        self.assertEqual(_superscript("10"), "¹⁰")
        self.assertEqual(_superscript("123"), "¹²³")

    def test_superscript_function_zero(self):
        """_superscript handles zero."""
        self.assertEqual(_superscript("0"), "⁰")

    def test_footnote_reference_in_list(self):
        """Footnote reference in list item rendered as superscript."""
        md = "- Item with ref[^1]\n\n[^1]: Footnote."
        tokens = parse_markdown(md)
        output = render(tokens)
        self.assertIn("¹", output)


class FootnoteRendererEdgeCases(unittest.TestCase):
    def test_footnote_reference_no_definition(self):
        """Footnote reference without definition still renders superscript."""
        tokens = parse_markdown("Text[^1].")
        output = render(tokens)
        self.assertIn("¹", output)
        # No footnote definition token should be present
        self.assertNotIn("    ¹", output)

    def test_footnote_definition_no_reference(self):
        """Footnote definition without reference still rendered."""
        md = "Text.\n\n[^1]: Orphan footnote."
        tokens = parse_markdown(md)
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertIn("Orphan footnote", output)

    def test_footnote_reference_with_bold(self):
        """Footnote reference with surrounding bold text."""
        tokens = parse_markdown("**Bold** text[^1].")
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertNotIn("<strong>", output)
        self.assertIn("Bold", output)

    def test_footnote_reference_with_link(self):
        """Footnote reference with link in same paragraph."""
        tokens = parse_markdown("[Link](url) text[^1].")
        output = render(tokens)
        self.assertIn("¹", output)
        self.assertIn("Link", output)


if __name__ == "__main__":
    unittest.main()
