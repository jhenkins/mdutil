"""Tests for KB-103: Terminal strikethrough uses combining macron, not just colour.

Strikethrough `~~text~~` now renders with combining macron (U+0305) after each
character, producing `t̶e̶x̶t̶`-style output instead of just grey-coloured text.
"""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


MACRON = "\u0305"  # Combining macron


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def strip_macrons(text: str) -> str:
    """Remove combining macron characters."""
    return text.replace(MACRON, "")


class StrikethroughMacronTests(unittest.TestCase):
    """Strikethrough renders with combining macron overlay."""

    def test_strikethrough_contains_macron(self):
        """~~text~~ renders with combining macron after each character."""
        tokens = parse_markdown("~~text~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        # Should contain combining macron characters
        self.assertIn(MACRON, plain, "Strikethrough should contain combining macron")

    def test_strikethrough_macron_after_each_char(self):
        """Each character in strikethrough has a macron after it."""
        tokens = parse_markdown("~~abc~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        # "abc" with macrons: "a̅b̅c̅"
        self.assertIn("a" + MACRON, plain)
        self.assertIn("b" + MACRON, plain)
        self.assertIn("c" + MACRON, plain)

    def test_strikethrough_no_raw_del_tags(self):
        """Strikethrough output should not contain <del> tags."""
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertNotIn("<del>", plain)
        self.assertNotIn("</del>", plain)

    def test_strikethrough_with_spaces(self):
        """Spaces in strikethrough also get macrons."""
        tokens = parse_markdown("~~hello world~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        # "hello world" with macrons: "h̅e̅l̅l̅o̅  ̅w̅o̅r̅l̅d̅"
        self.assertIn("h" + MACRON, plain)
        self.assertIn(" " + MACRON, plain)
        self.assertIn("w" + MACRON, plain)

    def test_strikethrough_all_themes(self):
        """All themes apply macron overlay to strikethrough."""
        for theme in ("colored", "dracula", "high-contrast", "one-dark"):
            tokens = parse_markdown("~~text~~")
            output = render(tokens, theme=theme)
            plain = strip_ansi(output)
            self.assertIn(
                MACRON, plain, f"{theme} should apply combining macron"
            )

    def test_strikethrough_with_bold(self):
        """~~**bold**~~ renders with macron overlay on bold text."""
        tokens = parse_markdown("~~**bold**~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        # Bold "bold" with macrons
        self.assertIn("b" + MACRON, plain)
        self.assertIn("o" + MACRON, plain)
        self.assertIn("l" + MACRON, plain)
        self.assertIn("d" + MACRON, plain)

    def test_strikethrough_with_emphasis(self):
        """~~*em*~~ renders with macron overlay on em text."""
        tokens = parse_markdown("~~*em*~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("e" + MACRON, plain)
        self.assertIn("m" + MACRON, plain)

    def test_strikethrough_with_code(self):
        """~~`code`~~ renders with macron overlay on code text."""
        tokens = parse_markdown("~~`code`~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("c" + MACRON, plain)
        self.assertIn("o" + MACRON, plain)
        self.assertIn("d" + MACRON, plain)
        self.assertIn("e" + MACRON, plain)

    def test_strikethrough_preserves_text_content(self):
        """Strikethrough preserves the original text when macrons stripped."""
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        stripped = strip_macrons(plain)
        self.assertIn("deleted", stripped)

    def test_non_strikethrough_no_macron(self):
        """Regular text does not get combining macrons."""
        tokens = parse_markdown("This is normal text.")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertNotIn(MACRON, plain)


class StrikethroughHelperTests(unittest.TestCase):
    """Test the _strikethrough helper function."""

    def test_strikethrough_helper_empty(self):
        from mdutil.renderer import _strikethrough

        self.assertEqual(_strikethrough(""), "")

    def test_strikethrough_helper_single_char(self):
        from mdutil.renderer import _strikethrough

        result = _strikethrough("a")
        self.assertEqual(result, "a" + MACRON)

    def test_strikethrough_helper_multiple_chars(self):
        from mdutil.renderer import _strikethrough

        result = _strikethrough("abc")
        self.assertEqual(result, "a" + MACRON + "b" + MACRON + "c" + MACRON)

    def test_strikethrough_helper_with_spaces(self):
        from mdutil.renderer import _strikethrough

        result = _strikethrough("hi")
        self.assertEqual(result, "h" + MACRON + "i" + MACRON)


if __name__ == "__main__":
    unittest.main()
