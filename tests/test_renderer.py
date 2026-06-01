import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


class RendererTests(unittest.TestCase):
    def test_render_preserves_blank_lines_from_blank_tokens(self):
        output = render(parse_markdown("# Title\n\nText"))

        self.assertIn("\n\nText", output)

    def test_render_strips_inline_code_tags_to_visible_text(self):
        output = render(parse_markdown("Use `mdutil` now"))

        self.assertEqual(output, "Use mdutil now")

    def test_render_horizontal_rule_as_rule_text(self):
        output = render(parse_markdown("Before\n---\nAfter"))

        self.assertEqual(strip_ansi(output), "Before\n---\nAfter")

    def test_heading_uses_token_content_not_reconstructed_text(self):
        output = render(
            [
                {
                    "type": "heading",
                    "level": 6,
                    "content": "# Canonical heading",
                    "text": "Wrong text must not render",
                }
            ]
        )

        self.assertIn("# Canonical heading", output)
        self.assertNotIn("Wrong text must not render", output)
        self.assertNotIn("######", output)

    def test_render_blocks_from_structured_token_content(self):
        tokens = [
            {"type": "paragraph", "content": "Paragraph <strong>text</strong>"},
            {"type": "blank", "content": ""},
            {"type": "list", "ordered": False, "items": ["one", "two"]},
            {"type": "blank", "content": ""},
            {"type": "list", "ordered": True, "items": ["first", "second"]},
            {"type": "blank", "content": ""},
            {"type": "blockquote", "content": "> quote\n> more"},
            {"type": "blank", "content": ""},
            {"type": "code", "content": "print(1)\nprint(2)", "language": "python"},
            {"type": "blank", "content": ""},
            {
                "type": "table",
                "headers": ["A", "B"],
                "alignments": ["left", "right"],
                "rows": [["1", "22"], ["333", "4"]],
            },
        ]

        output = strip_ansi(render(tokens, theme="colored"))

        self.assertIn("Paragraph text", output)
        self.assertIn("- one\n- two", output)
        self.assertIn("1. first\n2. second", output)
        self.assertIn("│ quote\n│ more", output)
        self.assertIn("print(1)\nprint(2)", output)
        self.assertIn("A   |  B", output)
        self.assertIn("--- | --", output)
        self.assertIn("1   | 22", output)
        self.assertIn("333 |  4", output)

    def test_ansi_styling_comes_from_selected_theme(self):
        output = render(
            [{"type": "heading", "level": 1, "content": "# Themed", "text": "Themed"}],
            theme="dracula",
        )

        self.assertIn("\033[38;2;255;121;198m", output)
        self.assertIn("\033[1m", output)
        self.assertTrue(output.endswith("\033[0m"))

    def test_horizontal_rule_uses_theme_color(self):
        output = render([{"type": "horizontal_rule", "content": "---", "text": "---"}], theme="dracula")

        self.assertEqual(output, "\033[38;2;98;114;164m---\033[0m")

    def test_custom_json_theme_file_overrides_rendered_colors(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "theme.json"
            path.write_text('{"markdown": {"h1": "#010203", "hr": "#040506"}}', encoding="utf-8")

            output = render(
                [
                    {"type": "heading", "level": 1, "content": "# Custom", "text": "Custom"},
                    {"type": "horizontal_rule", "content": "---", "text": "---"},
                ],
                theme_file=str(path),
            )

        self.assertIn("\033[38;2;1;2;3m", output)
        self.assertIn("\033[38;2;4;5;6m", output)

    def test_line_numbers_are_applied_to_every_rendered_line(self):
        output = render(parse_markdown("# Title\n\n```python\nprint(1)\nprint(2)\n```\nAfter"), line_numbers=True)

        lines = strip_ansi(output).splitlines()
        self.assertEqual(len(lines), 5)
        self.assertTrue(lines[0].startswith("   1 | "))
        self.assertTrue(lines[1].startswith("   2 | "))
        self.assertEqual(lines[1], "   2 | ")
        self.assertTrue(lines[2].startswith("   3 | print(1)"))
        self.assertTrue(lines[3].startswith("   4 | print(2)"))
        self.assertTrue(lines[4].startswith("   5 | After"))

    def test_code_blocks_are_syntax_highlighted_for_known_languages(self):
        output = render(parse_markdown("```python\ndef greet():\n    return 'hi'\n```"), theme="dracula")

        self.assertIn("\033[", output)
        self.assertEqual(strip_ansi(output), "def greet():\n    return 'hi'")

    def test_code_blocks_fall_back_to_plain_text_for_unknown_languages(self):
        output = render(parse_markdown("```unknown-language\nraw <code>\n```"), theme="dracula")

        self.assertEqual(output, "raw <code>")


if __name__ == "__main__":
    unittest.main()
