"""Tests for KB-093: Terminal inline code visual styling (mono font, background)."""
import unittest

from mdutil.parser import parse_markdown


class InlineCodeParserTests(unittest.TestCase):
    def test_parse_basic_inline_code(self):
        tokens = parse_markdown("Use `mdutil` now.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<code>mdutil</code>", tokens[0]["content"])

    def test_parse_inline_code_span_type(self):
        tokens = parse_markdown("Use `mdutil` now.")
        spans = tokens[0].get("spans", [])
        self.assertIn(
            {"type": "inline_code", "text": "mdutil"},
            spans,
        )

    def test_parse_multiple_inline_code(self):
        tokens = parse_markdown("Use `foo` and `bar` here.")
        self.assertIn("<code>foo</code>", tokens[0]["content"])
        self.assertIn("<code>bar</code>", tokens[0]["content"])

    def test_parse_inline_code_with_bold_inside(self):
        tokens = parse_markdown("Use `**literal**` here.")
        # Backtick content is literal — ** not parsed as bold
        self.assertIn("<code>**literal**</code>", tokens[0]["content"])

    def test_parse_inline_code_with_link_inside(self):
        tokens = parse_markdown("Use `[link](http://x.com)` here.")
        # Link syntax inside backticks is literal text
        self.assertIn("<code>[link](http://x.com)</code>", tokens[0]["content"])

    def test_parse_inline_code_in_heading(self):
        tokens = parse_markdown("## Heading with `code`")
        self.assertEqual(tokens[0]["type"], "heading")
        # Headings preserve raw backtick markers (inline not parsed in headings)
        self.assertIn("`code`", tokens[0]["content"])

    def test_parse_empty_inline_code(self):
        tokens = parse_markdown("Empty: ``.")
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<code></code>", tokens[0]["content"])


class InlineCodeRendererTests(unittest.TestCase):
    def test_inline_code_has_background_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("Use `mdutil` now.")
        output = render(tokens, theme="colored")
        # Should have ANSI background code (48;2;R;G;Bm)
        self.assertIn("\033[48;2;", output)
        # Stripped of tags
        self.assertNotIn("<code>", output)
        self.assertNotIn("</code>", output)
        # Text content preserved
        self.assertIn("mdutil", output)

    def test_inline_code_no_styling_when_theme_missing_key(self):
        from mdutil.renderer import render

        # Pass a theme without inline_code key — should degrade gracefully
        tokens = parse_markdown("Use `code` here.")
        output = render(tokens, theme="colored")
        # With default theme, inline_code is set, so it should have background
        self.assertIn("code", output)
        self.assertNotIn("<code>", output)

    def test_inline_code_all_themes(self):
        from mdutil.renderer import render

        tokens = parse_markdown("Use `code` here.")
        for theme_name in ("colored", "dracula", "high-contrast", "one-dark"):
            output = render(tokens, theme=theme_name)
            self.assertIn("code", output)
            self.assertNotIn("<code>", output)
            # All themes should apply background
            self.assertIn("\033[48;2;", output, f"{theme_name} should have background")

    def test_inline_code_multiple_spans_styled(self):
        from mdutil.renderer import render

        tokens = parse_markdown("Use `foo` and `bar` here.")
        output = render(tokens, theme="colored")
        # Both spans should have background styling
        count = output.count("\033[48;2;")
        self.assertEqual(count, 2)

    def test_inline_code_with_other_inline_styles(self):
        from mdutil.renderer import render

        tokens = parse_markdown("`code` and **bold** and *italic*.")
        output = render(tokens, theme="colored")
        # Inline code: background
        self.assertIn("\033[48;2;", output)
        # Bold: bold weight
        self.assertIn("\033[1m", output)
        # Italic: italic weight
        self.assertIn("\033[3m", output)

    def test_inline_code_preserves_text_content(self):
        from mdutil.renderer import render

        tokens = parse_markdown("See `the quick brown fox` jump.")
        output = render(tokens, theme="colored")
        self.assertIn("the quick brown fox", output)

    def test_inline_code_in_heading_styled(self):
        from mdutil.renderer import render

        tokens = parse_markdown("## Heading with `code`")
        output = render(tokens, theme="colored")
        # Headings preserve raw backtick markers — no inline parsing
        self.assertIn("`code`", output)


class InlineCodeThemeTests(unittest.TestCase):
    def test_colored_theme_inline_code_color(self):
        from mdutil.themes import COLORED

        self.assertIn("inline_code", COLORED["markdown"])
        self.assertEqual(COLORED["markdown"]["inline_code"], "#e8e8e8")

    def test_dracula_theme_inline_code_color(self):
        from mdutil.themes import DRACULA

        self.assertIn("inline_code", DRACULA["markdown"])
        self.assertEqual(DRACULA["markdown"]["inline_code"], "#44475a")

    def test_high_contrast_theme_inline_code_color(self):
        from mdutil.themes import HIGH_CONTRAST

        self.assertIn("inline_code", HIGH_CONTRAST["markdown"])
        self.assertEqual(HIGH_CONTRAST["markdown"]["inline_code"], "#cccccc")

    def test_one_dark_theme_inline_code_color(self):
        from mdutil.themes import ONE_DARK

        self.assertIn("inline_code", ONE_DARK["markdown"])
        self.assertEqual(ONE_DARK["markdown"]["inline_code"], "#3c4048")

    def test_markdown_colors_includes_inline_code(self):
        from mdutil.themes import MARKDOWN_COLORS

        self.assertIn("inline_code", MARKDOWN_COLORS)
        self.assertEqual(MARKDOWN_COLORS["inline_code"], "#e8e8e8")


if __name__ == "__main__":
    unittest.main()
