import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mdutil.cli import main


class CliTests(unittest.TestCase):
    def run_mdutil(self, *args, input_text=None, env=None):
        if env is not None:
            return subprocess.run(
                [sys.executable, "-m", "mdutil", *args],
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            isolated_env = os.environ.copy()
            isolated_env["HOME"] = tmpdir
            return subprocess.run(
                [sys.executable, "-m", "mdutil", *args],
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
                env=isolated_env,
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
            path.write_text("# Interactive\n\nbody\n", encoding="utf-8")

            stdout = TtyStdout()
            with (
                patch("sys.stdout", stdout),
                patch("mdutil.cli.run_interactive_viewer", return_value=None) as viewer,
            ):
                exit_code = main([str(path)])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        viewer.assert_called_once()
        source_lines = viewer.call_args.args[0]
        self.assertEqual(source_lines, ["# Interactive", "", "body"])
        self.assertEqual(viewer.call_args.kwargs["document_name"], "doc.md")
        self.assertEqual(viewer.call_args.kwargs["save_path"], str(path))

    def test_file_argument_passes_line_number_preference_to_interactive_viewer(self):
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
                exit_code = main(["--line-numbers", str(path)])

        self.assertEqual(exit_code, 0)
        viewer.assert_called_once()
        rendered_lines = viewer.call_args.args[0]
        self.assertTrue(any("# Interactive" in line for line in rendered_lines))
        self.assertFalse(any("   1 |" in line for line in rendered_lines))
        self.assertTrue(viewer.call_args.kwargs["line_numbers"])
        self.assertEqual(viewer.call_args.kwargs["document_name"], "doc.md")
        self.assertEqual(viewer.call_args.kwargs["save_path"], str(path))

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

    def test_creates_default_config_in_home_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["HOME"] = tmpdir

            result = self.run_mdutil("-", input_text="# Config created\n", env=env)

            config_path = Path(tmpdir) / ".mdutilcfg"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(config_path.exists())
            config_text = config_path.read_text(encoding="utf-8")
            self.assertIn("# mdutil configuration file", config_text)
            self.assertIn("theme = colored", config_text)
            self.assertIn("# Available built-in themes:", config_text)

    def test_generate_config_creates_config_without_requiring_markdown_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "generated.ini"

            result = self.run_mdutil("--config", str(config_path), "--generate-config")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Configuration file ready: {config_path}", result.stdout)
            self.assertTrue(config_path.exists())
            self.assertIn("theme = colored", config_path.read_text(encoding="utf-8"))

    def test_loads_runtime_defaults_from_config_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom.ini"
            config_path.write_text("[mdutil]\nline_numbers = true\ntheme = dracula\n", encoding="utf-8")

            result = self.run_mdutil("--config", str(config_path), "-", input_text="# Configured\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("   1 | ", result.stdout)
        self.assertIn("# Configured", result.stdout)
        self.assertIn("\033[38;2;255;121;198m", result.stdout)

    def test_cli_options_override_config_file_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            theme_file = Path(tmpdir) / "theme.json"
            theme_file.write_text('{"name": "custom", "markdown": {"h1": "#ffffff"}}', encoding="utf-8")
            config_path = Path(tmpdir) / "custom.ini"
            config_path.write_text("[mdutil]\nline_numbers = true\ntheme = dracula\n", encoding="utf-8")

            result = self.run_mdutil(
                "--config",
                str(config_path),
                "--theme",
                "colored",
                "--theme-file",
                str(theme_file),
                "-",
                input_text="# Overridden\n",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("   1 | ", result.stdout)
        self.assertIn("\033[38;2;255;255;255m", result.stdout)

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

    def test_export_pdf_writes_valid_file(self):
        """--export pdf with --output writes a valid PDF file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Test Title\n\nParagraph.\n", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = self.run_mdutil("--export", "pdf", "--output", str(out), str(doc))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertIn(out.name, result.stderr)
            self.assertGreater(out.stat().st_size, 10)

    def test_export_pdf_stdout_returns_pdf_bytes(self):
        """--export pdf without --output/--output-dir writes to cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "mdutil", "--export", "pdf", str(doc)],
                capture_output=True,
                check=False,
                env={**os.environ, "HOME": tmpdir},
                cwd=tmpdir,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            out = Path(tmpdir) / "doc.pdf"
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 10)

    def test_export_html_writes_valid_file(self):
        """--export html with --output writes a valid HTML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil("--export", "html", "--output", str(out), str(doc))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertIn(out.name, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("<h1>Title</h1>", html)

    def test_export_html_stdout_returns_valid_html(self):
        """--export html without --output/--output-dir writes to cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "mdutil", "--export", "html", str(doc)],
                capture_output=True,
                check=False,
                env={**os.environ, "HOME": tmpdir},
                cwd=tmpdir,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            out = Path(tmpdir) / "doc.html"
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("<h1>Title</h1>", html)

    def test_export_multi_format_via_output_dir(self):
        """--export pdf,html with --output-dir generates both files auto-named."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            # Use subprocess directly with binary mode for multi-format (mixes text+binary output)
            result = subprocess.run(
                [sys.executable, "-m", "mdutil", "--export", "pdf,html", "--output-dir", str(outdir), str(doc)],
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertTrue((outdir / "doc.pdf").exists())
            self.assertTrue((outdir / "doc.html").exists())
            self.assertIn(b"doc.pdf", result.stderr)
            self.assertIn(b"doc.html", result.stderr)

    def test_export_multi_format_stdin_auto_names(self):
        """--export pdf,html with --output-dir on stdin uses output as stem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            outdir = Path(tmpdir) / "exports"

            result = subprocess.run(
                [sys.executable, "-m", "mdutil", "--export", "pdf,html", "--output-dir", str(outdir)],
                input=b"# Title\n\nBody.\n",
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertTrue((outdir / "output.pdf").exists())
            self.assertTrue((outdir / "output.html").exists())

    def test_export_bad_format_rejected(self):
        """--export with unsupported format returns error."""
        result = self.run_mdutil("--export", "docx", input_text="# Title\n\nBody.\n")

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Unsupported export format", result.stderr)

    def test_export_partial_failure_continues(self):
        """When one format in a multi-export fails, others continue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            # Make output_dir a path to an existing file to trigger write error
            outdir = Path(tmpdir) / "exports"
            outdir.mkdir()
            result = self.run_mdutil("--export", "pdf,html", "--output-dir", str(outdir), str(doc))

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_export_with_theme_passthrough(self):
        """--export respects --theme choice (colored theme)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil("--theme", "dracula", "--export", "html", "--output", str(out), str(doc))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("<h1>Title</h1>", html)

    def test_export_with_custom_css(self):
        """--custom-css embeds CSS in HTML output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css_file = Path(tmpdir) / "custom.css"
            css_file.write_text("body { color: red; }", encoding="utf-8")
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil("--custom-css", str(css_file), "--export", "html", "--output", str(out), str(doc))

            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("/* Custom CSS */", html)
            self.assertIn("body { color: red; }", html)

    def test_export_with_custom_css_missing_file(self):
        """--custom-css with a nonexistent file reports an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.run_mdutil("--custom-css", "/nonexistent/file.css", "--export", "html", input_text="# Title\n\nBody.\n")

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Error reading custom CSS file", result.stderr)

    def test_export_pdf_uses_config_defaults(self):
        """PDF export respects config defaults for paper size and margins."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = self.run_mdutil("--export", "pdf", "--output", str(out), str(doc))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 10)

    def test_export_permission_error_handled(self):
        """Export to a read-only directory reports PermissionError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Title\n\nBody.\n", encoding="utf-8")
            readonly = Path(tmpdir) / "readonly"
            readonly.mkdir(mode=0o444)

            result = self.run_mdutil("--export", "pdf", "--output-dir", str(readonly), str(doc))

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Permission denied", result.stderr)


if __name__ == "__main__":
    unittest.main()
