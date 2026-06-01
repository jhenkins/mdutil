import re
import subprocess
import sys
import unittest
from pathlib import Path

from mdutil.parser import parse_markdown
from mdutil.reader import read_input
from mdutil.renderer import render

FIXTURE_DIR = Path(__file__).parent / "fixtures"
REPRESENTATIVE_MD = FIXTURE_DIR / "representative.md"
REPRESENTATIVE_GOLDEN = FIXTURE_DIR / "representative.golden"
NO_COLOR_THEME = FIXTURE_DIR / "no-color-theme.json"


def visible_text(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text).rstrip("\n")


def golden_text() -> str:
    return REPRESENTATIVE_GOLDEN.read_text(encoding="utf-8").rstrip("\n")


class GoldenOutputTests(unittest.TestCase):
    def test_representative_markdown_renders_to_golden_output(self):
        content = read_input(REPRESENTATIVE_MD)
        output = render(parse_markdown(content), theme_file=str(NO_COLOR_THEME))

        self.assertEqual(visible_text(output), golden_text())

    def test_cli_representative_markdown_matches_golden_output(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mdutil",
                "--theme-file",
                str(NO_COLOR_THEME),
                str(REPRESENTATIVE_MD),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(visible_text(result.stdout), golden_text())
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
