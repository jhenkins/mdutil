"""Tests for KB-102: Parser ***bold-italic*** leaves trailing asterisk.

The parser was checking ** before ***, so ***text*** matched ** + *text* + **,
leaving a trailing *. Now *** is checked first.
"""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


class BoldItalicParserTests(unittest.TestCase):
    """Parser correctly handles ***bold-italic*** syntax."""

    def test_parse_bold_italic_asterisk(self):
        tokens = parse_markdown("***bold italic***")
        self.assertEqual(tokens[0]["type"], "paragraph")
        content = tokens[0]["content"]
        # Should contain both <strong> and <em> tags
        self.assertIn("<strong>", content)
        self.assertIn("<em>", content)
        # Text should be wrapped in both
        self.assertIn("<strong><em>bold italic</em></strong>", content)

    def test_parse_bold_italic_underscore(self):
        tokens = parse_markdown("___bold italic___")
        self.assertEqual(tokens[0]["type"], "paragraph")
        content = tokens[0]["content"]
        self.assertIn("<strong><em>bold italic</em></strong>", content)

    def test_parse_bold_italic_mixed(self):
        """***bold italic*** produces strong+emphasis spans."""
        tokens = parse_markdown("***bold italic***")
        spans = tokens[0].get("spans", [])
        types = [s["type"] for s in spans]
        self.assertIn("strong", types)
        self.assertIn("emphasis", types)

    def test_bold_italic_no_trailing_asterisk(self):
        """***text*** should not leave trailing * in parsed content."""
        tokens = parse_markdown("***text***")
        content = tokens[0]["content"]
        # The trailing asterisk should not appear in the raw content
        self.assertNotIn("***text***", content)
        # Should be fully wrapped
        self.assertTrue(content.startswith("<strong><em>"))
        self.assertTrue(content.endswith("</em></strong>"))

    def test_bold_italic_underscore_no_trailing(self):
        """___text___ should not leave trailing _ in parsed content."""
        tokens = parse_markdown("___text___")
        content = tokens[0]["content"]
        self.assertNotIn("___text___", content)

    def test_bold_italic_with_inner_formatting(self):
        """***bold *inner* italic*** works correctly."""
        tokens = parse_markdown("***bold *inner* italic***")
        content = tokens[0]["content"]
        self.assertIn("<strong><em>", content)
        self.assertIn("</em></strong>", content)

    def test_bold_italic_preserves_content(self):
        """Bold italic preserves the inner text."""
        tokens = parse_markdown("***hello world***")
        self.assertIn("hello world", tokens[0]["content"])

    def test_single_asterisk_not_bold_italic(self):
        """*text* is emphasis, not bold italic."""
        tokens = parse_markdown("*text*")
        content = tokens[0]["content"]
        self.assertIn("<em>text</em>", content)
        self.assertNotIn("<strong>", content)

    def test_double_asterisk_not_bold_italic(self):
        """**text** is bold, not bold italic."""
        tokens = parse_markdown("**text**")
        content = tokens[0]["content"]
        self.assertIn("<strong>text</strong>", content)
        self.assertNotIn("<em>", content)

    def test_triple_asterisk_bold_italic(self):
        """***text*** is bold italic, not bold+emphasis separately."""
        tokens = parse_markdown("***text***")
        content = tokens[0]["content"]
        # Should be a single wrapped element, not two separate ones
        self.assertIn("<strong><em>text</em></strong>", content)


class BoldItalicRendererTests(unittest.TestCase):
    """Renderer correctly renders bold italic without trailing characters."""

    def test_bold_italic_renders_without_trailing_asterisk(self):
        from mdutil.renderer import render

        tokens = parse_markdown("***bold italic***")
        output = render(tokens, theme="colored")
        # Should not contain literal asterisks from the syntax
        plain = re.sub(r"\033\[[0-9;]*m", "", output)
        self.assertNotIn("***", plain)
        self.assertNotIn("*bold italic*", plain)
        # Should contain the text
        self.assertIn("bold italic", plain)
        # Should have ANSI codes (bold)
        self.assertIn("\033[", output)

    def test_bold_italic_underscore_renders_cleanly(self):
        from mdutil.renderer import render

        tokens = parse_markdown("___bold italic___")
        output = render(tokens, theme="colored")
        plain = re.sub(r"\033\[[0-9;]*m", "", output)
        self.assertNotIn("___", plain)
        self.assertIn("bold italic", plain)

    def test_bold_italic_all_themes(self):
        from mdutil.renderer import render

        for theme in ("colored", "dracula", "high-contrast", "one-dark"):
            tokens = parse_markdown("***text***")
            output = render(tokens, theme=theme)
            plain = re.sub(r"\033\[[0-9;]*m", "", output)
            self.assertNotIn("*", plain, f"{theme}: should not have trailing asterisks")
            self.assertIn("text", plain, f"{theme}: should contain text")

    def test_bold_italic_in_sentence(self):
        from mdutil.renderer import render

        tokens = parse_markdown("This is ***bold italic*** text.")
        output = render(tokens, theme="colored")
        plain = re.sub(r"\033\[[0-9;]*m", "", output)
        self.assertNotIn("***", plain)
        self.assertIn("bold italic", plain)


if __name__ == "__main__":
    unittest.main()
