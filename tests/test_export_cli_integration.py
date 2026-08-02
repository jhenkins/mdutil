"""CLI integration tests for syntax-highlighted export (Phase 4).

Exercises the full CLI → exporter pipeline with syntax-highlighted code blocks.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


DOC_WITH_CODE = """# Title

Here is some Python:

```python
def greet(name: str) -> str:
    \"\"\"Greet someone.\"\"\"
    return f\"Hello, {name}!\"

# Call it
print(greet(\"World\"))
```

And some JavaScript:

```javascript
function add(a, b) {
    return a + b;
}
const sum = add(3, 5);
console.log(sum);
```
"""


class CliSyntaxHighlightExportTests(unittest.TestCase):
    """CLI integration tests for syntax-highlighted PDF/HTML exports."""

    @staticmethod
    def run_mdutil(*args, input_text=None, env=None):
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

    def test_export_html_includes_pygments_highlighting(self):
        """HTML export with syntax theme produces span classes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil(
                "--syntax-theme", "dracula",
                "--export", "html", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn("<style>", html)
            self.assertIn(".mdutil-highlight", html)
            self.assertIn("def", html)
            self.assertIn("<span", html)

    def test_export_html_custom_syntax_theme(self):
        """Different syntax themes produce different CSS in HTML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            out1 = Path(tmpdir) / "out1.html"
            out2 = Path(tmpdir) / "out2.html"

            self.run_mdutil(
                "--syntax-theme", "dracula",
                "--export", "html", "--output", str(out1), str(doc)
            )
            self.run_mdutil(
                "--syntax-theme", "monokai",
                "--export", "html", "--output", str(out2), str(doc)
            )

            html1 = out1.read_text(encoding="utf-8")
            html2 = out2.read_text(encoding="utf-8")

            # Both should have syntax CSS
            self.assertIn(".mdutil-highlight", html1)
            self.assertIn(".mdutil-highlight", html2)
            # They should differ in color values
            self.assertNotEqual(html1, html2)

    def test_export_html_unknown_language_fallback(self):
        """Unknown language codes fall back to plain text without error."""
        md = """# Test

```xyzunknown
some gibberish code
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(md, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            # No span tags for unknown language
            self.assertNotIn("<span", html)
            # But the code text should still be present
            self.assertIn("some gibberish code", html)

    def test_export_pdf_includes_highlighting(self):
        """PDF export with syntax theme produces valid PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = self.run_mdutil(
                "--syntax-theme", "dracula",
                "--export", "pdf", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 10)
            # Basic PDF validation
            pdf_bytes = out.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_export_pdf_unknown_language_fallback(self):
        """Unknown language in PDF export falls back to plain text."""
        md = """# Test

```xyzunknown
some gibberish code
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(md, encoding="utf-8")
            out = Path(tmpdir) / "out.pdf"

            result = self.run_mdutil(
                "--export", "pdf", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            pdf_bytes = out.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_export_no_syntax_theme_still_works(self):
        """Exports work with default syntax theme."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil(
                "--export", "html", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn('<pre class="mdutil-highlight">', html)
            self.assertIn("def", html)

    def test_export_multi_format_both_highlighted(self):
        """Multi-format export produces both PDF and HTML with highlighting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            outdir = Path(tmpdir) / "exports"

            result = subprocess.run(
                [sys.executable, "-m", "mdutil",
                 "--syntax-theme", "dracula",
                 "--export", "pdf,html",
                 "--output-dir", str(outdir), str(doc)],
                capture_output=True,
                check=False,
                env={**os.environ, "HOME": tempfile.mkdtemp()},
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            pdf_path = outdir / "doc.pdf"
            html_path = outdir / "doc.html"
            self.assertTrue(pdf_path.exists())
            self.assertTrue(html_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 10)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn(".mdutil-highlight", html)

    def test_export_with_custom_css_and_syntax_theme(self):
        """Custom CSS and syntax theme both present in HTML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css = Path(tmpdir) / "custom.css"
            css.write_text("body { background: #111; }", encoding="utf-8")
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(DOC_WITH_CODE, encoding="utf-8")
            out = Path(tmpdir) / "out.html"

            result = self.run_mdutil(
                "--syntax-theme", "dracula",
                "--custom-css", str(css),
                "--export", "html", "--output", str(out), str(doc)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn(".mdutil-highlight", html)
            self.assertIn("/* Custom CSS */", html)
            self.assertIn("body { background: #111; }", html)
            # Custom CSS should appear after syntax CSS
            syntax_pos = html.find(".mdutil-highlight")
            custom_pos = html.find("/* Custom CSS */")
            self.assertGreater(custom_pos, syntax_pos)


if __name__ == "__main__":
    unittest.main()
