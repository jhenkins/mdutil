"""Comprehensive renderer tests for KB-078: All new features.

Tests terminal rendering, theme color application, fallback behavior,
and cross-feature rendering for: strikethrough, task lists, math, footnotes,
sub/superscript, highlight, definition lists, images, link titles, and nested lists.
"""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _strip_macrons(text: str) -> str:
    """Remove combining macron characters (U+0305) from text."""
    return text.replace("\u0305", "")


def has_ansi(text: str) -> bool:
    """Check if text contains ANSI escape sequences."""
    return bool(re.search(r"\x1b\[[0-9;]*m", text))


# ===========================================================================
# Theme color verification for each feature
# ===========================================================================

class ThemeColorTests(unittest.TestCase):
    """Verify that theme colors are applied to each new feature."""

    def test_strikethrough_uses_theme_color(self):
        """Strikethrough should be styled with strikethrough theme color."""
        tokens = parse_markdown("This is ~~deleted~~ text.")
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("deleted", _strip_macrons(plain))
        # Should have ANSI coloring
        self.assertTrue(has_ansi(output))

    def test_highlight_uses_background_color(self):
        """Highlight should apply background color from theme."""
        tokens = parse_markdown("This is ==highlighted== text.")
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("highlighted", plain)
        # Should have ANSI background color (48;2;...)
        self.assertTrue(has_ansi(output))
        self.assertIn("48;2;", output)

    def test_definition_term_uses_theme_color(self):
        """Definition term should use definition_term theme color."""
        md = "Term\n:   Definition."
        tokens = parse_markdown(md)
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("Term", plain)
        self.assertIn("Definition", plain)
        self.assertTrue(has_ansi(output))

    def test_subscript_uses_theme_color(self):
        """Subscript should use subscript theme color."""
        tokens = parse_markdown("H~2~O")
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("H", plain)
        self.assertIn("O", plain)
        self.assertTrue(has_ansi(output))

    def test_superscript_uses_theme_color(self):
        """Superscript should use superscript theme color."""
        tokens = parse_markdown("e^2^")
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("e", plain)
        self.assertIn("²", plain)
        self.assertTrue(has_ansi(output))

    def test_task_checkbox_uses_theme_color(self):
        """Task checkboxes should use theme colors."""
        md = "- [x] Done\n- [ ] Todo"
        tokens = parse_markdown(md)
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("☑", plain)
        self.assertIn("☐", plain)
        self.assertTrue(has_ansi(output))

    def test_footnote_reference_rendered_as_superscript(self):
        """Footnote references render as superscript characters."""
        md = "Text[^1].\n\n[^1]: Footnote."
        tokens = parse_markdown(md)
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("¹", plain)


# ===========================================================================
# Math fallback behavior
# ===========================================================================

class MathFallbackTests(unittest.TestCase):

    def test_math_fallback_shows_raw_latex(self):
        """math_fallback=True preserves $...$ delimiters."""
        tokens = parse_markdown("Equation: $E=mc^2$")
        output = render(tokens, math_fallback=True)
        plain = strip_ansi(output)
        self.assertIn("$E=mc^2$", plain)

    def test_math_no_fallback_strips_tags(self):
        """math_fallback=False (default) strips <math> tags."""
        tokens = parse_markdown("Equation: $E=mc^2$")
        output = render(tokens, math_fallback=False)
        plain = strip_ansi(output)
        self.assertNotIn("$E=mc^2$", plain)
        self.assertIn("E=mc²", plain)

    def test_math_default_is_no_fallback(self):
        """Default behavior (no math_fallback param) strips tags."""
        tokens = parse_markdown("$x$")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("$x$", plain)
        self.assertIn("x", plain)


# ===========================================================================
# Footnote style behavior
# ===========================================================================

class FootnoteStyleTests(unittest.TestCase):

    def test_footnote_bracketed_style(self):
        """footnote_style=bracketed renders [N] instead of superscript."""
        md = "Text[^1] and [^2]."
        tokens = parse_markdown(md)
        output = render(tokens, footnote_style="bracketed")
        plain = strip_ansi(output)
        self.assertIn("[1]", plain)
        self.assertIn("[2]", plain)
        self.assertNotIn("¹", plain)
        self.assertNotIn("²", plain)

    def test_footnote_numbered_style(self):
        """footnote_style=numbered renders superscript (default)."""
        md = "Text[^1]."
        tokens = parse_markdown(md)
        output = render(tokens, footnote_style="numbered")
        plain = strip_ansi(output)
        self.assertIn("¹", plain)
        self.assertNotIn("[1]", plain)

    def test_footnote_default_is_numbered(self):
        """Default footnote_style is numbered."""
        md = "Text[^1]."
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("¹", plain)
        self.assertNotIn("[1]", plain)


# ===========================================================================
# Cross-feature rendering
# ===========================================================================

class CrossFeatureRendererTests(unittest.TestCase):
    """Test rendering of documents with multiple features."""

    def test_full_document_rendering(self):
        """Render a document with all features and verify no tags remain."""
        md = (
            "# Title\n\n"
            "Paragraph with ~~strike~~, **bold**, *em*, `code`, "
            '[link](url "title"), ![alt](img.png), $E=mc^2$, '
            "[^1], H~2~O, e^2^, ==highlight==.\n\n"
            "- [x] Task 1\n"
            "- [ ] Task 2\n\n"
            "Term\n:   Definition\n\n"
            "[^1]: Footnote."
        )
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)

        # No HTML-like tags should remain
        self.assertNotIn("<del>", plain)
        self.assertNotIn("<strong>", plain)
        self.assertNotIn("<em>", plain)
        self.assertNotIn("<code>", plain)
        self.assertNotIn("<a ", plain)
        self.assertNotIn("<img", plain)
        self.assertNotIn("<math>", plain)
        self.assertNotIn("<fnref", plain)
        self.assertNotIn("<sub>", plain)
        self.assertNotIn("<sup>", plain)
        self.assertNotIn("<mark>", plain)

        # Content should be present
        self.assertIn("strike", _strip_macrons(plain))
        self.assertIn("bold", plain)
        self.assertIn("em", plain)
        self.assertIn("code", plain)
        self.assertIn("url", plain)
        self.assertIn("E=mc²", plain)
        self.assertIn("H", plain)
        self.assertIn("O", plain)
        self.assertIn("highlight", plain)
        self.assertIn("Term", plain)
        self.assertIn("Definition", plain)
        self.assertIn("Footnote", plain)

    def test_strikethrough_in_list(self):
        """Strikethrough inside list items renders correctly."""
        md = "- ~~deleted~~ item"
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<del>", plain)
        self.assertIn("deleted", plain)

    def test_task_list_with_formatting(self):
        """Task list with inline formatting renders correctly."""
        md = "- [x] **Done** with *em* and `code`"
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<strong>", plain)
        self.assertNotIn("<em>", plain)
        self.assertNotIn("<code>", plain)
        self.assertIn("Done", plain)
        self.assertIn("em", plain)
        self.assertIn("code", plain)

    def test_math_with_formatting(self):
        """Math with surrounding formatting renders correctly."""
        tokens = parse_markdown("The **equation** $E=mc^2$ is **famous**.")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<strong>", plain)
        self.assertNotIn("<math>", plain)
        self.assertIn("equation", plain)
        self.assertIn("E=mc²", plain)
        self.assertIn("famous", plain)

    def test_footnote_with_link(self):
        """Footnote with link in definition renders correctly."""
        md = "Text[^1].\n\n[^1]: See [link](url) for details."
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<a", plain)
        self.assertNotIn("href", plain)
        self.assertIn("link", plain)
        self.assertIn("url", plain)

    def test_nested_list_with_tasks(self):
        """Nested task lists render with proper indentation."""
        md = "- [x] Top task\n  - [ ] Sub task"
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("☑", plain)
        self.assertIn("☐", plain)
        # Sub-item should be indented
        lines = plain.split("\n")
        top_line = [l for l in lines if "Top task" in l][0]
        sub_line = [l for l in lines if "Sub task" in l][0]
        self.assertTrue(sub_line.startswith("  "))


# ===========================================================================
# Image rendering
# ===========================================================================

class ImageRendererTests(unittest.TestCase):

    def test_image_rendered_as_placeholder(self):
        """Images render as [image: alt text] placeholders."""
        tokens = parse_markdown("![alt text](url)")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<img", plain)
        self.assertIn("[image: alt text]", plain)

    def test_image_empty_alt_uses_url(self):
        """Empty alt text falls back to URL."""
        tokens = parse_markdown("![](url)")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("[image: url]", plain)

    def test_image_in_paragraph(self):
        """Image in paragraph with surrounding text."""
        tokens = parse_markdown("Before ![alt](url) after")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("Before", plain)
        self.assertIn("[image: alt]", plain)
        self.assertIn("after", plain)


# ===========================================================================
# Definition list rendering
# ===========================================================================

class DefinitionListRendererTests(unittest.TestCase):

    def test_definition_term_and_definition(self):
        """Definition list renders term with definition."""
        md = "Term\n:   Definition."
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("Term", plain)
        self.assertIn("Definition", plain)
        self.assertIn("—", plain)

    def test_definition_strips_inline_tags(self):
        """Definition list strips inline formatting tags."""
        md = "Term\n:   **Bold** and *em* definition."
        tokens = parse_markdown(md)
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<strong>", plain)
        self.assertNotIn("<em>", plain)
        self.assertIn("Bold", plain)
        self.assertIn("em", plain)


# ===========================================================================
# Complex document rendering
# ===========================================================================

class ComplexDocumentRendererTests(unittest.TestCase):

    def test_heading_with_inline_formatting(self):
        """Headings with inline formatting render correctly."""
        tokens = parse_markdown("# **Bold** *Italic* `Code`")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertNotIn("<strong>", plain)
        self.assertNotIn("<em>", plain)
        self.assertNotIn("<code>", plain)
        self.assertIn("Bold", plain)
        self.assertIn("Italic", plain)
        self.assertIn("Code", plain)

    def test_code_block_preserves_content(self):
        """Code blocks preserve original content."""
        tokens = parse_markdown("```python\nprint('hello')\n```")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("print('hello')", plain)

    def test_table_rendering(self):
        """Tables render with proper alignment."""
        tokens = parse_markdown("A | B\n:--- | ---:\n1 | 2")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("A", plain)
        self.assertIn("B", plain)
        self.assertIn("1", plain)
        self.assertIn("2", plain)

    def test_blockquote_rendering(self):
        """Blockquotes render with pipe character."""
        tokens = parse_markdown("> Quote text")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("│", plain)
        self.assertIn("Quote text", plain)

    def test_horizontal_rule_rendering(self):
        """Horizontal rules render with theme color."""
        tokens = parse_markdown("---")
        output = render(tokens, theme="dracula")
        plain = strip_ansi(output)
        self.assertIn("---", plain)
        self.assertTrue(has_ansi(output))

    def test_line_numbers(self):
        """Line numbers are added when requested."""
        tokens = parse_markdown("# Title\n\nText")
        output = render(tokens, line_numbers=True)
        lines = strip_ansi(output).split("\n")
        self.assertTrue(lines[0].startswith("   1 | "))
        self.assertTrue(lines[1].startswith("   2 | "))
        self.assertTrue(lines[2].startswith("   3 | "))


# ===========================================================================
# Fallback behaviors
# ===========================================================================

class FallbackBehaviorTests(unittest.TestCase):

    def test_quiet_mode(self):
        """quiet=True returns empty string."""
        tokens = parse_markdown("# Title")
        output = render(tokens, quiet=True)
        self.assertEqual(output, "")

    def test_unknown_theme_raises_value_error(self):
        """Unknown theme raises ValueError (no fallback)."""
        tokens = parse_markdown("# Title")
        with self.assertRaises(ValueError):
            render(tokens, theme="nonexistent")

    def test_empty_document(self):
        """Empty document renders nothing."""
        output = render([])
        self.assertEqual(output, "")

    def test_blank_lines_preserved(self):
        """Blank lines are preserved in output."""
        tokens = parse_markdown("# Title\n\nText")
        output = render(tokens)
        self.assertIn("\n\nText", output)


# ===========================================================================
# Unicode and special characters
# ===========================================================================

class UnicodeRendererTests(unittest.TestCase):

    def test_emoji_in_text(self):
        """Emoji characters render correctly."""
        tokens = parse_markdown("Hello 🌍 World")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("🌍", plain)

    def test_cjk_characters(self):
        """CJK characters render with proper width."""
        tokens = parse_markdown("你好世界")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("你好世界", plain)

    def test_mixed_ascii_and_unicode(self):
        """Mixed ASCII and Unicode characters."""
        tokens = parse_markdown("Hello 世界!")
        output = render(tokens)
        plain = strip_ansi(output)
        self.assertIn("Hello", plain)
        self.assertIn("世界", plain)
        self.assertIn("!", plain)


if __name__ == "__main__":
    unittest.main()
