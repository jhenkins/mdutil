import re
import subprocess
import sys
import unittest
from pathlib import Path

from mdutil.parser import parse_markdown
from mdutil.reader import read_input
from mdutil.renderer import render

FIXTURE_DIR = Path(__file__).parent / "fixtures"
GOLDEN_CASES = [
    "representative",
    "inline-quality",
    "unicode-table",
]
NO_COLOR_THEME = FIXTURE_DIR / "no-color-theme.json"


def visible_text(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text).rstrip("\n")


def fixture_text(name: str, suffix: str) -> str:
    return (FIXTURE_DIR / f"{name}.{suffix}").read_text(encoding="utf-8").rstrip("\n")


class GoldenOutputTests(unittest.TestCase):
    def test_markdown_fixtures_render_to_golden_output(self):
        for name in GOLDEN_CASES:
            with self.subTest(name=name):
                content = read_input(FIXTURE_DIR / f"{name}.md")
                output = render(parse_markdown(content), theme_file=str(NO_COLOR_THEME))

                self.assertEqual(visible_text(output), fixture_text(name, "golden"))

    def test_cli_markdown_fixtures_match_golden_output(self):
        for name in GOLDEN_CASES:
            with self.subTest(name=name):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "mdutil",
                        "--theme-file",
                        str(NO_COLOR_THEME),
                        str(FIXTURE_DIR / f"{name}.md"),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(visible_text(result.stdout), fixture_text(name, "golden"))
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
