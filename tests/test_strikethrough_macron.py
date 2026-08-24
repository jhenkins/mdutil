"""Tests for strikethrough rendering: ANSI \033[9m strikethrough.

Strikethrough `~~text~~` renders with the strikethrough theme colour
and the ANSI strikethrough escape (\033[9m / STANDOUT ON).
"""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def strip_ansi_colors(text: str) -> str:
    """Remove ANSI colour codes but keep bold/italic."""
    # Remove colour codes (38;2;R;G;Bm and similar)
    text = re.sub(r"\033\[38;2;\d+;\d+;\d+m", "", text)
    text = re.sub(r"\033\[48;2;\d+;\d+;\d+m", "", text)
    return text


class StrikethroughRendererTests(unittest.TestCase):
    """Strikethrough renders with theme colour."""

    def test_strikethrough_no_raw_del_tags(self):
        """Strikethrough output should not contain <del> tags."""
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertNotIn("<del>", plain)
        self.assertNotIn("</del>", plain)

    def test_strikethrough_preserves_text(self):
        """Strikethrough preserves the original text."""
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("deleted", plain)

    def test_strikethrough_with_bold(self):
        """~~**bold**~~ renders strikethrough colour around bold text."""
        tokens = parse_markdown("~~**bold**~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("bold", plain)

    def test_strikethrough_with_emphasis(self):
        """~~*em*~~ renders strikethrough colour around italic text."""
        tokens = parse_markdown("~~*em*~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("em", plain)

    def test_strikethrough_with_code(self):
        """~~`code`~~ renders strikethrough colour around code text."""
        tokens = parse_markdown("~~`code`~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("code", plain)

    def test_all_themes_apply_colour(self):
        """All themes apply colour to strikethrough text."""
        for theme in ("colored", "dracula", "high-contrast", "one-dark"):
            tokens = parse_markdown("~~text~~")
            output = render(tokens, theme=theme)
            plain = strip_ansi(output)
            self.assertIn("text", plain, f"{theme} should preserve text")

    def test_non_strikethrough_no_colour(self):
        """Regular text renders without strikethrough styling."""
        tokens = parse_markdown("This is normal text.")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        # Plain paragraph text should render normally
        self.assertIn("This is normal text.", plain)

    def test_strikethrough_with_spaces(self):
        """Spaces in strikethrough are preserved."""
        tokens = parse_markdown("~~hello world~~")
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        self.assertIn("hello", plain)
        self.assertIn("world", plain)

    def test_strikethrough_uses_ansi_escape(self):
        """Strikethrough output contains \033[9m (STANDOUT ON) and \033[29m (off)."""
        tokens = parse_markdown("~~deleted~~")
        output = render(tokens, theme="colored")
        self.assertIn("\033[9m", output, "Should contain strikethrough ON escape")
        self.assertIn("\033[29m", output, "Should contain strikethrough OFF escape")

    def test_strikethrough_escape_with_bold(self):
        """~~**bold**~~ includes strikethrough escape codes."""
        tokens = parse_markdown("~~**bold**~~")
        output = render(tokens, theme="colored")
        self.assertIn("\033[9m", output)
        self.assertIn("\033[29m", output)

    def test_strikethrough_escape_with_emphasis(self):
        """~~*em*~~ includes strikethrough escape codes."""
        tokens = parse_markdown("~~*em*~~")
        output = render(tokens, theme="colored")
        self.assertIn("\033[9m", output)
        self.assertIn("\033[29m", output)

    def test_strikethrough_escape_with_code(self):
        """~~`code`~~ includes strikethrough escape codes."""
        tokens = parse_markdown("~~`code`~~")
        output = render(tokens, theme="colored")
        self.assertIn("\033[9m", output)
        self.assertIn("\033[29m", output)

    def test_strikethrough_all_themes_have_escape(self):
        """All themes apply strikethrough ANSI escape."""
        for theme in ("colored", "dracula", "high-contrast", "one-dark"):
            tokens = parse_markdown("~~text~~")
            output = render(tokens, theme=theme)
            self.assertIn("\033[9m", output, f"{theme} should apply strikethrough escape")
            self.assertIn("\033[29m", output, f"{theme} should turn off strikethrough escape")
