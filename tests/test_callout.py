"""Tests for GFM callout (admonition) blockquote handling.

Covers parser detection/stripping (KB-091) and terminal renderer
differentiation between callout blockquotes and ordinary blockquotes.
"""

import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


class CalloutParserTests(unittest.TestCase):
    def test_regular_blockquote_is_not_a_callout(self):
        tokens = parse_markdown("> just a quote\n> second line")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0]["type"], "blockquote")
        self.assertNotIn("callout_type", tokens[0])

    def test_note_callout_is_detected_and_typed(self):
        tokens = parse_markdown("> [!NOTE] title\n> body")
        self.assertEqual(tokens[0]["type"], "blockquote")
        self.assertEqual(tokens[0]["callout_type"], "NOTE")

    def test_callout_marker_is_stripped_from_content(self):
        tokens = parse_markdown("> [!NOTE] title\n> body")
        content = tokens[0]["content"]
        self.assertNotIn("[!NOTE]", content)
        self.assertIn("title", content)
        self.assertIn("body", content)

    def test_callout_title_following_marker_is_preserved(self):
        tokens = parse_markdown("> [!WARNING] Be careful with that")
        content = tokens[0]["content"].strip()
        self.assertEqual(content, "Be careful with that")

    def test_callout_type_is_uppercased_and_case_insensitive(self):
        for raw, expected in [("note", "NOTE"), ("Warning", "WARNING"), ("iMpOrTaNt", "IMPORTANT")]:
            tokens = parse_markdown(f"> [!{raw}] x")
            self.assertEqual(tokens[0]["callout_type"], expected, msg=raw)

    def test_callout_without_leading_space_after_gt(self):
        tokens = parse_markdown(">[!NOTE] tight")
        self.assertEqual(tokens[0]["callout_type"], "NOTE")
        self.assertEqual(tokens[0]["content"].strip(), "tight")

    def test_all_supported_callout_types(self):
        for t in ["NOTE", "TIP", "SUCCESS", "INFO", "QUESTION", "CAUTION", "WARNING", "IMPORTANT", "DANGER"]:
            tokens = parse_markdown(f"> [!{t}] body")
            self.assertEqual(tokens[0]["callout_type"], t)

    def test_blockquote_only_a_callout_when_first_line_is_marker(self):
        tokens = parse_markdown("> plain line\n> [!NOTE] inside")
        # The blockquote starts with a non-marker line, so it is not a callout.
        self.assertNotIn("callout_type", tokens[0])
        self.assertIn("[!NOTE]", tokens[0]["content"])


class CalloutRendererTests(unittest.TestCase):
    def test_regular_blockquote_uses_plain_border(self):
        out = strip_ansi(render(parse_markdown("> quote line")))
        self.assertIn("│ quote line", out)

    def test_callout_header_differs_from_regular_quote(self):
        plain = strip_ansi(render(parse_markdown("> quote line")))
        callout = strip_ansi(render(parse_markdown("> [!NOTE] title\n> body")))
        self.assertNotEqual(plain, callout)
        self.assertIn("[!NOTE]", callout)
        self.assertNotIn("[!NOTE]", plain)

    def test_callout_header_shows_marker_and_title(self):
        out = strip_ansi(render(parse_markdown("> [!NOTE] My title")))
        self.assertIn("▌ [!NOTE]  My title", out)

    def test_callout_body_lines_carry_border(self):
        out = strip_ansi(render(parse_markdown("> [!NOTE] t\n> body one\n> body two")))
        self.assertIn("body one", out)
        self.assertIn("body two", out)

    def test_callout_applies_type_colour(self):
        # DANGER -> red (255;0;0) should appear in the raw output.
        raw = render(parse_markdown("> [!DANGER] x"))
        self.assertIn("255;0;0", raw)

    def test_callout_header_is_bold(self):
        raw = render(parse_markdown("> [!NOTE] x"))
        # Bold escape precedes the header marker.
        self.assertIn("\033[1m", raw)

    def test_empty_callout_still_renders_header(self):
        out = strip_ansi(render(parse_markdown("> [!NOTE]")))
        self.assertIn("▌ [!NOTE]", out)

    def test_callout_colour_can_be_overridden_by_theme(self):
        theme = {
            "markdown": {
                "blockquote": "#888888",
                "blockquote_border": "#444444",
                "callouts": {"NOTE": "#ff00ff"},
            }
        }
        from mdutil.renderer import _callout_color
        self.assertEqual(_callout_color("NOTE", theme), "\033[38;2;255;0;255m")


if __name__ == "__main__":
    unittest.main()
