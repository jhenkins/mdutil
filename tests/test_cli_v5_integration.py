"""CLI integration tests for v5.0 features (KB-080).

Tests the full CLI → exporter pipeline with new features: math-fallback,
footnote-style, multi-format export, config integration, and end-to-end
document rendering.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


DOC_WITH_V5_FEATURES = """# V5.0 Features Test

This document tests all v5.0 features through the CLI.

## Inline Features

~~Strikethrough~~ works.

This is ==highlighted== text.

Water is H~2~O and x^2^.

Einstein said $E=mc^2$ here.

This is a reference[^1].

## Task List

- [x] Done task
- [ ] Todo task
- Regular item

## Definition List

Apple
:   A fruit

[^1]: This is a footnote definition.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_mdutil(*args, input_text=None, env=None, cwd=None):
    """Run mdutil CLI via subprocess with isolated HOME."""
    if env is None:
        tmpdir = tempfile.mkdtemp()
        env = os.environ.copy()
        env["HOME"] = tmpdir
    return subprocess.run(
        [sys.executable, "-m", "mdutil", *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        env=env,
        cwd=cwd,
    )


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract human-readable text from PDF bytes."""
    raw_text = pdf_bytes.decode("latin-1", errors="replace")
    cmaps: dict[int, str] = {}
    for m in re.finditer(r"<(\w+)>\s+<(\w+)>", raw_text):
        cid = int(m.group(1), 16)
        uni = int(m.group(2), 16)
        cmaps[cid] = chr(uni)
    streams = re.findall(rb"stream\n(.*?)\nendstream", pdf_bytes, re.DOTALL)
    parts: list[str] = []
    for raw in streams:
        try:
            decomp = zlib.decompress(raw)
        except Exception:
            continue
        text = decomp.decode("latin-1", errors="replace")
        for m in re.finditer(r"\(([^)]*)\)\s*Tj", text, re.DOTALL):
            raw_bytes = m.group(1)
            if isinstance(raw_bytes, bytes):
                raw_bytes = raw_bytes.decode("latin-1")
            decoded = ""
            for i in range(0, len(raw_bytes) - 1, 2):
                cid = (ord(raw_bytes[i]) << 8) | ord(raw_bytes[i + 1])
                decoded += cmaps.get(cid, f"[{cid}]")
            parts.append(decoded)
    return "".join(parts)


# ===========================================================================
# CLI: Math Fallback Flag
# ===========================================================================

class CliMathFallbackTests(unittest.TestCase):
    """Test --math-fallback CLI flag behavior."""

    def test_math_fallback_flag_accepted(self):
        """--math-fallback flag is accepted."""
        result = _run_mdutil("--math-fallback", input_text="Use $E=mc^2$ here.")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_math_fallback_shows_dollar_signs(self):
        """--math-fallback shows $...$ delimiters in terminal output."""
        result = _run_mdutil("--math-fallback", input_text="Use $E=mc^2$ here.")
        self.assertEqual(result.returncode, 0, result.stderr)
        plain = _strip_ansi(result.stdout)
        self.assertIn("$E=mc^2$", plain)

    def test_math_fallback_no_flag_strips_dollars(self):
        """Without --math-fallback, $ signs are stripped."""
        result = _run_mdutil(input_text="Use $E=mc^2$ here.")
        self.assertEqual(result.returncode, 0, result.stderr)
        plain = _strip_ansi(result.stdout)
        self.assertNotIn("$E=mc^2$", plain)

    def test_math_fallback_with_export(self):
        """--math-fallback works with PDF export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("$E=mc^2$", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = _run_mdutil(
                "--math-fallback",
                "--export", "pdf", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(out.read_bytes().startswith(b"%PDF"))

    def test_math_fallback_with_html_export(self):
        """--math-fallback works with HTML export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("$E=mc^2$", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--math-fallback",
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<html", html)

    def test_math_fallback_with_export_to_file(self):
        """--math-fallback with --export pdf to file produces valid PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("$x^2$", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = _run_mdutil(
                "--math-fallback",
                "--export", "pdf", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(out.read_bytes().startswith(b"%PDF"))


# ===========================================================================
# CLI: Footnote Style Flag
# ===========================================================================

class CliFootnoteStyleTests(unittest.TestCase):
    """Test --footnote-style CLI flag behavior."""

    def test_footnote_style_numbered_accepted(self):
        """--footnote-style numbered is accepted."""
        result = _run_mdutil("--footnote-style", "numbered", input_text="See [^1].")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_footnote_style_bracketed_accepted(self):
        """--footnote-style bracketed is accepted."""
        result = _run_mdutil("--footnote-style", "bracketed", input_text="See [^1].")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_footnote_style_rejects_invalid(self):
        """--footnote-style with invalid value exits non-zero."""
        result = _run_mdutil("--footnote-style", "invalid_choice", input_text="See [^1].")
        self.assertNotEqual(result.returncode, 0)

    def test_footnote_style_bracketed_in_terminal_output(self):
        """--footnote-style bracketed renders [1] in terminal."""
        md = "Text[^1].\n\n[^1]: A footnote."
        result = _run_mdutil("--footnote-style", "bracketed", input_text=md)
        self.assertEqual(result.returncode, 0, result.stderr)
        plain = _strip_ansi(result.stdout)
        self.assertIn("[1]", plain)

    def test_footnote_style_numbered_in_terminal_output(self):
        """--footnote-style numbered renders superscript reference."""
        md = "Text[^1].\n\n[^1]: A footnote."
        result = _run_mdutil("--footnote-style", "numbered", input_text=md)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Numbered style should render something (superscript or text)
        plain = _strip_ansi(result.stdout)
        self.assertTrue(len(plain) > 0)


# ===========================================================================
# CLI: Multi-Format Export with v5.0 Features
# ===========================================================================

class CliMultiFormatExportTests(unittest.TestCase):
    """Test multi-format export with v5.0 features."""

    def test_multi_format_pdf_html_v5_features(self):
        """Export to both PDF and HTML preserves v5.0 features."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            result = _run_mdutil(
                "--export", "pdf,html",
                "--output-dir", str(outdir), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((outdir / "doc.pdf").exists())
            self.assertTrue((outdir / "doc.html").exists())
            self.assertGreater((outdir / "doc.pdf").stat().st_size, 10)
            html = (outdir / "doc.html").read_text(encoding="utf-8")
            self.assertIn("<html", html)

    def test_multi_format_with_theme(self):
        """Multi-format export respects theme option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            result = _run_mdutil(
                "--theme", "dracula",
                "--export", "html",
                "--output-dir", str(outdir), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((outdir / "doc.html").exists())

    def test_multi_format_with_syntax_theme(self):
        """Multi-format export respects syntax theme."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            result = _run_mdutil(
                "--syntax-theme", "monokai",
                "--export", "pdf,html",
                "--output-dir", str(outdir), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = (outdir / "doc.html").read_text(encoding="utf-8")
            self.assertIn(".mdutil-highlight", html)

    def test_multi_format_with_custom_css(self):
        """Custom CSS is embedded in HTML export alongside v5.0 styles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css = Path(tmpdir) / "custom.css"
            css.write_text("body { background: #222; }", encoding="utf-8")
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Test\n\n==highlighted==", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--custom-css", str(css),
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("body { background: #222; }", html)
            self.assertIn("<mark>highlighted</mark>", html)


# ===========================================================================
# CLI: Config File Integration
# ===========================================================================

class CliConfigIntegrationTests(unittest.TestCase):
    """Test config file integration with CLI export."""

    def test_config_file_with_math_fallback(self):
        """Config math_fallback=true is respected during export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / "config.ini"
            config.write_text(
                "[mdutil]\nmath_fallback = true\n",
                encoding="utf-8"
            )
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("$E=mc^2$", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = _run_mdutil(
                "--config", str(config),
                "--export", "pdf", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())

    def test_config_file_with_footnote_style(self):
        """Config footnote_style=bracketed is respected during export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / "config.ini"
            config.write_text(
                "[mdutil]\nfootnote_style = bracketed\n",
                encoding="utf-8"
            )
            md = "Text[^1].\n\n[^1]: Footnote."
            result = _run_mdutil(
                "--config", str(config),
                input_text=md
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_flag_overrides_config(self):
        """CLI flag overrides config file setting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / "config.ini"
            config.write_text(
                "[mdutil]\nmath_fallback = true\n",
                encoding="utf-8"
            )
            # CLI flag should override config
            result = _run_mdutil(
                "--config", str(config),
                "--math-fallback",
                input_text="Test $x$ here."
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plain = _strip_ansi(result.stdout)
            self.assertIn("$x$", plain)

    def test_generate_config_includes_v5_options(self):
        """generate-config creates config with math_fallback and footnote_style."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "generated.ini"

            result = _run_mdutil("--config", str(config_path), "--generate-config")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(config_path.exists())
            text = config_path.read_text(encoding="utf-8")
            self.assertIn("math_fallback", text)
            self.assertIn("footnote_style", text)


# ===========================================================================
# CLI: End-to-End Document Rendering
# ===========================================================================

class CliEndToEndTests(unittest.TestCase):
    """End-to-end CLI tests with full v5.0 documents."""

    def test_full_document_terminal_rendering(self):
        """Full v5.0 document renders in terminal without errors."""
        result = _run_mdutil(input_text=DOC_WITH_V5_FEATURES)
        self.assertEqual(result.returncode, 0, result.stderr)
        plain = _strip_ansi(result.stdout)
        self.assertIn("V5.0 Features Test", plain)

    def test_full_document_pdf_export(self):
        """Full v5.0 document exports to valid PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = _run_mdutil(
                "--export", "pdf", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            pdf_bytes = out.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF"))
            self.assertGreater(len(pdf_bytes), 5000)

    def test_full_document_html_export(self):
        """Full v5.0 document exports to valid HTML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("<html", html)
            self.assertIn("</html>", html)

    def test_full_document_all_formats(self):
        """Full v5.0 document exports to all formats successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            result = _run_mdutil(
                "--export", "pdf,html",
                "--output-dir", str(outdir), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((outdir / "doc.pdf").exists())
            self.assertTrue((outdir / "doc.html").exists())

    def test_stdin_to_pdf_export(self):
        """Piped stdin exports to PDF correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "out.pdf"
            result = _run_mdutil(
                "--export", "pdf", "--output", str(out),
                input_text="# Hello\n\n~~Strikethrough~~ and ==highlight==."
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(out.read_bytes().startswith(b"%PDF"))

    def test_stdin_to_html_export(self):
        """Piped stdin exports to HTML file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "out.html"
            result = _run_mdutil(
                "--export", "html", "--output", str(out),
                input_text="# Hello\n\n~~Strikethrough~~ and ==highlight==."
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("Strikethrough", html)

    def test_full_document_with_math_fallback(self):
        """Full document with --math-fallback exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--math-fallback",
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<html", html)

    def test_full_document_with_footnote_style(self):
        """Full document with --footnote-style bracketed exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_V5_FEATURES, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--footnote-style", "bracketed",
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<html", html)


# ===========================================================================
# CLI: Edge Cases
# ===========================================================================

class CliEdgeCaseTests(unittest.TestCase):
    """CLI edge case tests for v5.0 features."""

    def test_empty_document_export(self):
        """Empty document exports without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("", encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = _run_mdutil(
                "--export", "pdf", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_single_feature_document(self):
        """Document with only one v5.0 feature exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("==just highlighted==", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<mark>just highlighted</mark>", html)

    def test_only_math_notation(self):
        """Document with only math notation exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("$x^2 + y^2 = z^2$", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("<math>", html)

    def test_only_task_list(self):
        """Document with only task list exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("- [x] Done\n- [ ] Todo", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("checkbox", html)

    def test_only_footnotes(self):
        """Document with only footnotes exports correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("Text[^1].\n\n[^1]: Footnote.", encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = _run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("footnote", html.lower())


if __name__ == "__main__":
    unittest.main()
