import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mdutil.cli import main


class CliTests(unittest.TestCase):
    def run_mdutil(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, "-m", "mdutil", *args],
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_reads_file_argument(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("# From file\n", encoding="utf-8")

            result = self.run_mdutil(str(path))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# From file", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_file_argument_launches_interactive_viewer_when_stdout_is_terminal(self):
        class TtyStdout(io.StringIO):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("# Interactive\n", encoding="utf-8")

            stdout = TtyStdout()
            with (
                patch("sys.stdout", stdout),
                patch("mdutil.cli.run_interactive_viewer", return_value=None) as viewer,
            ):
                exit_code = main([str(path)])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        viewer.assert_called_once()
        rendered_lines = viewer.call_args.args[0]
        self.assertTrue(any("# Interactive" in line for line in rendered_lines))

    def test_piped_stdin_keeps_non_interactive_output_even_when_stdout_is_terminal(self):
        class TtyStdout(io.StringIO):
            def isatty(self):
                return True

        class PipeStdin(io.StringIO):
            def isatty(self):
                return False

        stdout = TtyStdout()
        with (
            patch("sys.stdin", PipeStdin("# Piped\n")),
            patch("sys.stdout", stdout),
            patch("mdutil.cli.run_interactive_viewer", return_value=None) as viewer,
        ):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("# Piped", stdout.getvalue())
        viewer.assert_not_called()

    def test_reads_stdin_when_file_is_dash(self):
        result = self.run_mdutil("-", input_text="# From dash\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# From dash", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_reads_piped_stdin_when_no_file_argument(self):
        result = self.run_mdutil(input_text="# From pipe\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# From pipe", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_supports_theme_and_theme_file_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            theme_file = Path(tmpdir) / "theme.json"
            theme_file.write_text('{"name": "custom", "markdown": {"h1": "#ffffff"}}', encoding="utf-8")
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Themed\n", encoding="utf-8")

            result = self.run_mdutil("--theme", "dracula", "--theme-file", str(theme_file), str(doc))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Themed", result.stdout)
        self.assertIn("\033[38;2;255;255;255m", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_invalid_theme_name_is_rejected(self):
        result = self.run_mdutil("--theme", "missing", "-", input_text="# Bad\n")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)

    def test_supports_line_numbers(self):
        result = self.run_mdutil("--line-numbers", "-", input_text="# Numbered\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("   1 | ", result.stdout)
        self.assertIn("# Numbered", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_no_file_and_interactive_stdin_shows_usage_error(self):
        class InteractiveStdin(io.StringIO):
            def isatty(self):
                return True

        stderr = io.StringIO()
        with patch("sys.stdin", InteractiveStdin()), patch("sys.stderr", stderr):
            exit_code = main([])

        self.assertEqual(exit_code, 2)
        self.assertIn("usage: mdutil", stderr.getvalue())
        self.assertIn("provide a file path or pipe Markdown on stdin", stderr.getvalue())

    def test_missing_file_error_is_reported_by_cli(self):
        result = self.run_mdutil("/definitely/missing/file.md")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Error: File not found: /definitely/missing/file.md", result.stderr)

    def test_supports_version(self):
        result = self.run_mdutil("--version")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"^mdutil \d+\.\d+\.\d+\n$")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
