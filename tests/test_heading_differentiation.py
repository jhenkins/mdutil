"""Tests for KB-090: Terminal heading differentiation (colour + bold + underline).

Visual hierarchy:
  h1: colour + bold + underline with ═ (double horizontal)
  h2: colour + bold + underline with ─ (single horizontal)
  h3-h6: colour + bold (no underline)
"""
import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.themes import (
    BUILT_IN_THEMES,
    COLORED,
    DEFAULT_THEME,
    DRACULA,
    HIGH_CONTRAST,
    MARKDOWN_COLORS,
    ONE_DARK,
    load_theme,
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def has_ansi(text: str) -> bool:
    """Check if a string contains ANSI escape codes."""
    return bool(re.search(r"\033\[[0-9;]*m", text))


def has_bold(text: str) -> bool:
    """Check if a string contains ANSI bold."""
    return "\033[1m" in text


def get_colour_codes(text: str) -> list[str]:
    """Extract 24-bit colour codes from text."""
    return re.findall(r"\033\[38;2;\d+;\d+;\d+m", text)


class HeadingParserTests(unittest.TestCase):
    """Parser produces heading tokens with correct level."""

    def test_parse_h1(self):
        tokens = parse_markdown("# Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 1)
        self.assertEqual(tokens[0]["text"], "Title")

    def test_parse_h2(self):
        tokens = parse_markdown("## Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 2)
        self.assertEqual(tokens[0]["text"], "Title")

    def test_parse_h3(self):
        tokens = parse_markdown("### Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 3)

    def test_parse_h4(self):
        tokens = parse_markdown("#### Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 4)

    def test_parse_h5(self):
        tokens = parse_markdown("##### Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 5)

    def test_parse_h6(self):
        tokens = parse_markdown("###### Title")
        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[0]["level"], 6)

    def test_parse_all_levels(self):
        """All six heading levels parse correctly."""
        md = "\n".join(f"{'#' * i} Heading {i}" for i in range(1, 7))
        tokens = parse_markdown(md)
        self.assertEqual(len(tokens), 6)
        for i, token in enumerate(tokens):
            self.assertEqual(token["type"], "heading")
            self.assertEqual(token["level"], i + 1)
            self.assertEqual(token["text"], f"Heading {i + 1}")


class HeadingRendererTests(unittest.TestCase):
    """Heading rendering produces styled output with level-appropriate decoration."""

    def test_h1_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("# Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h1 should have ANSI codes")
        self.assertTrue(has_bold(output), "h1 should be bold")

    def test_h2_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("## Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h2 should have ANSI codes")
        self.assertTrue(has_bold(output), "h2 should be bold")

    def test_h3_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("### Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h3 should have ANSI codes")
        self.assertTrue(has_bold(output), "h3 should be bold")

    def test_h4_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("#### Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h4 should have ANSI codes")
        self.assertTrue(has_bold(output), "h4 should be bold")

    def test_h5_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("##### Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h5 should have ANSI codes")
        self.assertTrue(has_bold(output), "h5 should be bold")

    def test_h6_has_bold_styling(self):
        from mdutil.renderer import render

        tokens = parse_markdown("###### Title")
        output = render(tokens, theme="colored")
        self.assertTrue(has_ansi(output), "h6 should have ANSI codes")
        self.assertTrue(has_bold(output), "h6 should be bold")

    def test_h1_has_double_horizontal_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("# Title")
        plain = strip_ansi(output := render(tokens, theme="colored"))
        lines = plain.splitlines()
        # h1: "Title" + "═════"
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Title")
        self.assertIn("═", lines[1])

    def test_h2_has_single_horizontal_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("## Title")
        plain = strip_ansi(output := render(tokens, theme="colored"))
        lines = plain.splitlines()
        # h2: "Title" + "────"
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Title")
        self.assertIn("─", lines[1])
        self.assertNotIn("═", lines[1])

    def test_h3_no_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("### Title")
        plain = strip_ansi(output := render(tokens, theme="colored"))
        lines = plain.splitlines()
        # h3: only "Title"
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "Title")

    def test_h4_no_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("#### Title")
        plain = strip_ansi(render(tokens, theme="colored"))
        lines = plain.splitlines()
        self.assertEqual(len(lines), 1)

    def test_h5_no_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("##### Title")
        plain = strip_ansi(render(tokens, theme="colored"))
        lines = plain.splitlines()
        self.assertEqual(len(lines), 1)

    def test_h6_no_underline(self):
        from mdutil.renderer import render

        tokens = parse_markdown("###### Title")
        plain = strip_ansi(render(tokens, theme="colored"))
        lines = plain.splitlines()
        self.assertEqual(len(lines), 1)

    def test_h1_underline_matches_text_width(self):
        from mdutil.renderer import render

        text = "Hello World"
        tokens = parse_markdown(f"# {text}")
        plain = strip_ansi(render(tokens, theme="colored"))
        lines = plain.splitlines()
        underline = lines[1].strip("\033[0m")
        # Count only ═ chars
        double_hors = underline.count("═")
        self.assertEqual(double_hors, len(text))

    def test_h2_underline_matches_text_width(self):
        from mdutil.renderer import render

        text = "Hello"
        tokens = parse_markdown(f"## {text}")
        plain = strip_ansi(render(tokens, theme="colored"))
        lines = plain.splitlines()
        single_hors = lines[1].count("─")
        self.assertEqual(single_hors, len(text))


class HeadingDifferentiationTests(unittest.TestCase):
    """Heading levels are visually differentiated across all themes."""

    def test_colored_theme_all_levels_different_colours(self):
        """Each heading level gets a distinct colour in the colored theme."""
        from mdutil.renderer import render

        raw_outputs = []
        for i in range(1, 7):
            md = f"{'#' * i} Level{i}"
            tokens = parse_markdown(md)
            raw_outputs.append(render(tokens, theme="colored"))

        # Collect unique first-colour RGB tuples across heading levels
        colours_used = set()
        for raw in raw_outputs:
            codes = get_colour_codes(raw)
            for code in codes:
                m = re.match(r"\033\[38;2;(\d+);(\d+);(\d+)m", code)
                if m:
                    colours_used.add((int(m.group(1)), int(m.group(2)), int(m.group(3))))
                    break  # only first colour per level

        self.assertGreater(len(colours_used), 1, "Multiple heading levels should have different colours")

    def test_dracula_theme_all_levels_different_colours(self):
        """Each heading level gets a distinct colour in the dracula theme."""
        h1_colour = DRACULA["markdown"]["h1"]
        h2_colour = DRACULA["markdown"]["h2"]
        h3_colour = DRACULA["markdown"]["h3"]
        h4_colour = DRACULA["markdown"]["h4"]
        h5_colour = DRACULA["markdown"]["h5"]
        h6_colour = DRACULA["markdown"]["h6"]

        # All six should be different
        colours = [h1_colour, h2_colour, h3_colour, h4_colour, h5_colour, h6_colour]
        self.assertEqual(len(set(colours)), 6, "All 6 heading levels should have distinct colours in dracula")

    def test_high_contrast_theme_all_levels_different_colours(self):
        """Each heading level gets a distinct colour in the high-contrast theme."""
        h1 = HIGH_CONTRAST["markdown"]["h1"]
        h2 = HIGH_CONTRAST["markdown"]["h2"]
        h3 = HIGH_CONTRAST["markdown"]["h3"]
        h4 = HIGH_CONTRAST["markdown"]["h4"]
        h5 = HIGH_CONTRAST["markdown"]["h5"]
        h6 = HIGH_CONTRAST["markdown"]["h6"]

        colours = [h1, h2, h3, h4, h5, h6]
        self.assertEqual(len(set(colours)), 6, "All 6 heading levels should have distinct colours in high-contrast")

    def test_one_dark_theme_all_levels_different_colours(self):
        """Each heading level gets a distinct colour in the one-dark theme."""
        h1 = ONE_DARK["markdown"]["h1"]
        h2 = ONE_DARK["markdown"]["h2"]
        h3 = ONE_DARK["markdown"]["h3"]
        h4 = ONE_DARK["markdown"]["h4"]
        h5 = ONE_DARK["markdown"]["h5"]
        h6 = ONE_DARK["markdown"]["h6"]

        colours = [h1, h2, h3, h4, h5, h6]
        self.assertEqual(len(set(colours)), 6, "All 6 heading levels should have distinct colours in one-dark")

    def test_dracula_heading_colours_are_vivid(self):
        """Dracula heading colours use vivid syntax-highlight palette."""
        # These should be vivid, recognisable dracula colours
        expected_colours = {"#ff79c6", "#bd93f9", "#50fa7b", "#8be9fd", "#f1fa8c", "#6272a4"}
        actual = {
            DRACULA["markdown"]["h1"],
            DRACULA["markdown"]["h2"],
            DRACULA["markdown"]["h3"],
            DRACULA["markdown"]["h4"],
            DRACULA["markdown"]["h5"],
            DRACULA["markdown"]["h6"],
        }
        self.assertEqual(actual, expected_colours)

    def test_colored_theme_heading_colours_distinct(self):
        """Colored theme headings use distinct colours."""
        colours = [
            MARKDOWN_COLORS["h1"],
            MARKDOWN_COLORS["h2"],
            MARKDOWN_COLORS["h3"],
            MARKDOWN_COLORS["h4"],
            MARKDOWN_COLORS["h5"],
            MARKDOWN_COLORS["h6"],
        ]
        self.assertEqual(len(set(colours)), 6, "All 6 heading levels should have distinct colours")


class HeadingRerenderingTests(unittest.TestCase):
    """Multi-line rendering integrates correctly with other features."""

    def test_heading_followed_by_paragraph(self):
        from mdutil.renderer import render

        md = "# Title\n\nBody text."
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        lines = plain.splitlines()
        # h1: 2 lines (text + underline), blank: 1 line, paragraph: 1 line
        self.assertIn("Title", lines[0])
        self.assertIn("═", lines[1])
        self.assertEqual(lines[2], "")
        self.assertIn("Body text", lines[3])

    def test_heading_followed_by_heading(self):
        from mdutil.renderer import render

        md = "# H1\n\n## H2"
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored")
        plain = strip_ansi(output)
        lines = plain.splitlines()
        # h1: 2 lines, blank: 1 line, h2: 2 lines
        self.assertEqual(len(lines), 5)
        self.assertIn("═", lines[1])
        self.assertIn("─", lines[4])

    def test_heading_with_line_numbers(self):
        from mdutil.renderer import render

        md = "# Title\n\nBody"
        tokens = parse_markdown(md)
        output = render(tokens, theme="colored", line_numbers=True)
        lines = strip_ansi(output).splitlines()
        # h1 text gets line 1, underline gets line 2, blank gets line 3, body gets line 4
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith("   1 | Title"))
        self.assertTrue(lines[1].startswith("   2 | ═"))
        self.assertTrue(lines[2].startswith("   3 | "))
        self.assertTrue(lines[3].startswith("   4 | Body"))

    def test_heading_uses_markdown_key_for_colour(self):
        from mdutil.renderer import render

        # Each heading level should use its own h{N} colour key
        tokens = parse_markdown("# H1\n\n## H2")
        output = render(tokens, theme="colored")
        # Both should have ANSI codes
        self.assertTrue(has_ansi(output))
        self.assertTrue(has_bold(output))


class HeadingThemeKeyTests(unittest.TestCase):
    """Theme keys are properly configured for all heading levels."""

    def test_markdown_colors_has_all_heading_keys(self):
        for i in range(1, 7):
            self.assertIn(f"h{i}", MARKDOWN_COLORS, f"h{i} missing from MARKDOWN_COLORS")

    def test_all_built_in_themes_have_all_heading_keys(self):
        for name, theme in BUILT_IN_THEMES.items():
            md = theme.get("markdown", {})
            for i in range(1, 7):
                key = f"h{i}"
                self.assertIn(
                    key, md,
                    f"Theme '{name}' missing h{i} key",
                )

    def test_heading_colours_are_valid_hex(self):
        for name, theme in BUILT_IN_THEMES.items():
            md = theme.get("markdown", {})
            for i in range(1, 7):
                key = f"h{i}"
                colour = md.get(key, "")
                self.assertRegex(
                    colour,
                    r"^#[0-9a-fA-F]{6}$",
                    f"Theme '{name}' h{i} colour '{colour}' is not valid hex",
                )


if __name__ == "__main__":
    unittest.main()
