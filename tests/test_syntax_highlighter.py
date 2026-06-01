import re
import unittest

from mdutil.syntax_highlighter import highlight_code
from mdutil.themes import BUILT_IN_THEMES


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


class SyntaxHighlighterTests(unittest.TestCase):
    def test_python_code_is_highlighted_with_ansi_but_keeps_text(self):
        code = 'def greet(name):\n    return "hi " + name\n'

        highlighted = highlight_code(code, "python", BUILT_IN_THEMES["dracula"])

        self.assertIn("\033[", highlighted)
        self.assertEqual(strip_ansi(highlighted), code.rstrip("\n"))

    def test_javascript_alias_is_highlighted(self):
        highlighted = highlight_code("const value = 1;", "js", BUILT_IN_THEMES["colored"])

        self.assertIn("\033[", highlighted)
        self.assertEqual(strip_ansi(highlighted), "const value = 1;")

    def test_unknown_language_falls_back_to_plain_text(self):
        code = "some unknown language text\nwith two lines"

        highlighted = highlight_code(code, "definitely-not-a-language", BUILT_IN_THEMES["colored"])

        self.assertEqual(highlighted, code)

    def test_missing_language_falls_back_to_plain_text(self):
        code = "plain text only"

        highlighted = highlight_code(code, "", BUILT_IN_THEMES["colored"])

        self.assertEqual(highlighted, code)


if __name__ == "__main__":
    unittest.main()
