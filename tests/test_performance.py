"""Performance tests for mdutil (KB-087).

Validates no regressions in parsing, rendering, and exporting for various
document sizes and feature density. Uses time.perf_counter() for measurements
and cProfile for deeper analysis when needed.
"""

import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from mdutil.parser import parse_markdown
from mdutil.renderer import render as render_terminal
from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter


FIXTURES_DIR = Path(__file__).parent / "lorem_ipsum_*.md"


# ---------------------------------------------------------------------------
# v5.0 feature-heavy document used for targeted benchmarks
# ---------------------------------------------------------------------------
V5_FEATURE_DOC = """\
# Performance Benchmark — v5.0 Features

This document exercises every v5.0 feature simultaneously.

## Strikethrough

This is ~~obsolete~~ outdated text with ~~multiple~~ ~~strikes~~ in one line.

## Task Lists

- [x] Parser strikethrough support
- [x] Parser task list detection
- [x] Renderer task list display
- [x] Exporter task list rendering
- [ ] Performance testing
- [ ] Version bump to 5.0.0

## Math Notation

Inline math: $E = mc^2$ and $\\sum_{i=1}^{n} x_i$.

Escaped: \\$ this is not math.

Code with math: `not $math$ here`.

## Footnotes

Here is a footnote reference[^1], another[^2], and a third[^3].

[^1]: First footnote definition with ~~strikethrough~~ and **bold**.
[^2]: Second footnote with *italic* and `code`.
[^3]: Third footnote with ==highlight== and $math$.

## Subscript / Superscript

Chemistry: H~2~O and C~6~H~12~O~6~.
Math: E=mc^2^ is famous.
Unicode: x₀, y₁, z₂ for subscripts.
Superscripts: x⁰, y¹, z².

## Highlight

This is ==highlighted== text with ==multiple== highlights ==in one line==.
Nested: ==text with **bold** inside==.

## Definition Lists

Term 1
:   Definition 1 with **bold** and *italic*.

Term 2
:   Definition 2 with `code` and ~~strike~~.
:   Additional definition for Term 2.

## Images

Inline image: ![alt text](https://example.com/image.png "Tooltip Title")
Another: ![logo](logo.png =300x200)

## Nested Lists

- Level 1 item 1
    - Level 2 item 1
        - Level 3 item 1
        - Level 3 item 2
    - Level 2 item 2
- Level 1 item 2
    - Level 2 item 3

## Link Titles

[Example](https://example.com "Example Site")
[GitHub](https://github.com "GitHub - Where the world builds software")
[With `code`](https://example.com "Title with **bold**")

## Code Block

```python
def fibonacci(n):
    \"\"\"Return the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# ~~Recursive is slow~~ — use iterative approach
result = fibonacci(10)
print("F(" + str(result) + ") = " + str(result))
```

## Blockquote with Features

> This is a **bold** blockquote with ~~strikethrough~~ text.
> It contains a task list item: - [x] verified.

## Table with Features

| Feature | Status | Notes |
|---------|--------|-------|
| Strikethrough | ✅ Done | ~~Not done~~ |
| Task Lists | ✅ Done | - [x] complete |
| Math | ✅ Done | $E=mc^2$ |
| Footnotes | ✅ Done | See above[^1] |
| Highlight | ✅ Done | ==Visible== |
| Definition Lists | ✅ Done | See above |
"""


def _load_fixture(name: str) -> str:
    """Load a lorem ipsum fixture by size name (e.g. '5k', '100k')."""
    path = Path(__file__).parent / f"lorem_ipsum_{name}.md"
    return path.read_text()


def _warmup(fn, *args, n: int = 3, **kwargs):
    """Run fn a few times to warm caches before timing."""
    for _ in range(n):
        fn(*args, **kwargs)


def _benchmark(fn, *args, n_runs: int = 5, **kwargs):
    """Run fn n_runs times and return (mean_ms, min_ms, max_ms, results_ms)."""
    # warmup
    _warmup(fn, *args, n=2, **kwargs)
    times_ms: list[float] = []
    for _ in range(n_runs):
        start = time.perf_counter()
        fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times_ms.append(elapsed_ms)
    return {
        "mean_ms": round(statistics.mean(times_ms), 3),
        "min_ms": round(min(times_ms), 3),
        "max_ms": round(max(times_ms), 3),
        "runs_ms": [round(t, 3) for t in times_ms],
    }


class TestParsePerformance(unittest.TestCase):
    """Benchmark parser against progressively larger documents."""

    @classmethod
    def setUpClass(cls):
        cls._sizes = ["5k", "10k", "20k", "50k", "75k", "100k", "250k"]
        cls._results: dict[str, dict] = {}
        for size in cls._sizes:
            doc = _load_fixture(size)
            cls._results[size] = _benchmark(parse_markdown, doc, n_runs=5)

    def test_parse_small_document(self):
        """5K doc should parse in well under 50ms."""
        r = self._results["5k"]
        self.assertLess(r["max_ms"], 50, f"5K parse took {r['max_ms']}ms")

    def test_parse_medium_document(self):
        """20K doc should parse in well under 200ms."""
        r = self._results["20k"]
        self.assertLess(r["max_ms"], 200, f"20K parse took {r['max_ms']}ms")

    def test_parse_large_document(self):
        """100K doc should parse in well under 1 second."""
        r = self._results["100k"]
        self.assertLess(r["max_ms"], 1000, f"100K parse took {r['max_ms']}ms")

    def test_parse_huge_document(self):
        """250K doc should parse in well under 2.5 seconds."""
        r = self._results["250k"]
        self.assertLess(r["max_ms"], 2500, f"250K parse took {r['max_ms']}ms")

    def test_parse_is_linear(self):
        """Parse time should scale roughly linearly with input size.

        Doubling input size should roughly double parse time (within 3x factor).
        """
        r_5k = self._results["5k"]["mean_ms"]
        r_100k = self._results["100k"]["mean_ms"]
        ratio = r_100k / r_5k if r_5k > 0 else float("inf")
        size_ratio = 100 / 5
        self.assertLess(
            ratio, size_ratio * 3,
            f"Parse scaled super-linearly: {size_ratio}x size → {ratio:.1f}x time"
        )

    def test_parse_v5_feature_document(self):
        """Parse the v5.0 feature test document."""
        doc = V5_FEATURE_DOC
        r = _benchmark(parse_markdown, doc, n_runs=5)
        self.assertLess(r["max_ms"], 20, f"V5 doc parse took {r['max_ms']}ms")

    def _print_results(self):
        print("\n=== Parse Performance ===")
        print(f"{'Size':>6s}  {'Mean ms':>10s}  {'Min ms':>10s}  {'Max ms':>10s}")
        for size in self._sizes:
            r = self._results[size]
            print(f"{size:>6s}  {r['mean_ms']:>10.3f}  {r['min_ms']:>10.3f}  {r['max_ms']:>10.3f}")


class TestRenderPerformance(unittest.TestCase):
    """Benchmark terminal renderer against progressively larger documents."""

    @classmethod
    def setUpClass(cls):
        cls._sizes = ["5k", "10k", "20k", "50k", "75k", "100k", "250k"]
        cls._results: dict[str, dict] = {}
        for size in cls._sizes:
            doc = _load_fixture(size)
            tokens = parse_markdown(doc)
            cls._results[size] = _benchmark(render_terminal, tokens, n_runs=5)

    def test_render_small_document(self):
        r = self._results["5k"]
        self.assertLess(r["max_ms"], 50, f"5K render took {r['max_ms']}ms")

    def test_render_medium_document(self):
        r = self._results["20k"]
        self.assertLess(r["max_ms"], 300, f"20K render took {r['max_ms']}ms")

    def test_render_large_document(self):
        r = self._results["100k"]
        self.assertLess(r["max_ms"], 2000, f"100K render took {r['max_ms']}ms")

    def test_render_huge_document(self):
        r = self._results["250k"]
        self.assertLess(r["max_ms"], 5000, f"250K render took {r['max_ms']}ms")

    def test_render_v5_feature_document(self):
        doc = V5_FEATURE_DOC
        tokens = parse_markdown(doc)
        r = _benchmark(render_terminal, tokens, n_runs=5)
        self.assertLess(r["max_ms"], 30, f"V5 doc render took {r['max_ms']}ms")

    def _print_results(self):
        print("\n=== Terminal Render Performance ===")
        print(f"{'Size':>6s}  {'Mean ms':>10s}  {'Min ms':>10s}  {'Max ms':>10s}")
        for size in self._sizes:
            r = self._results[size]
            print(f"{size:>6s}  {r['mean_ms']:>10.3f}  {r['min_ms']:>10.3f}  {r['max_ms']:>10.3f}")


class TestHTMLExportPerformance(unittest.TestCase):
    """Benchmark HTML exporter against progressively larger documents."""

    @classmethod
    def setUpClass(cls):
        cls._sizes = ["5k", "10k", "20k", "50k", "75k", "100k", "250k"]
        cls._results: dict[str, dict] = {}
        for size in cls._sizes:
            doc = _load_fixture(size)
            tokens = parse_markdown(doc)
            exporter = HtmlExporter()
            theme = {"text": "#000000", "heading": "#000000", "link": "#0366d6"}
            options = {"custom_css": "", "syntax_theme": "default"}
            cls._results[size] = _benchmark(
                exporter.render, tokens, theme, options, n_runs=5
            )

    def test_html_small_document(self):
        r = self._results["5k"]
        self.assertLess(r["max_ms"], 80, f"5K HTML took {r['max_ms']}ms")

    def test_html_medium_document(self):
        r = self._results["20k"]
        self.assertLess(r["max_ms"], 500, f"20K HTML took {r['max_ms']}ms")

    def test_html_large_document(self):
        r = self._results["100k"]
        self.assertLess(r["max_ms"], 4000, f"100K HTML took {r['max_ms']}ms")

    def test_html_huge_document(self):
        r = self._results["250k"]
        self.assertLess(r["max_ms"], 10000, f"250K HTML took {r['max_ms']}ms")

    def test_html_v5_feature_document(self):
        doc = V5_FEATURE_DOC
        tokens = parse_markdown(doc)
        exporter = HtmlExporter()
        theme = {"text": "#000000", "heading": "#000000", "link": "#0366d6"}
        options = {"custom_css": "", "syntax_theme": "default"}
        r = _benchmark(exporter.render, tokens, theme, options, n_runs=5)
        self.assertLess(r["max_ms"], 50, f"V5 doc HTML took {r['max_ms']}ms")

    def _print_results(self):
        print("\n=== HTML Export Performance ===")
        print(f"{'Size':>6s}  {'Mean ms':>10s}  {'Min ms':>10s}  {'Max ms':>10s}")
        for size in self._sizes:
            r = self._results[size]
            print(f"{size:>6s}  {r['mean_ms']:>10.3f}  {r['min_ms']:>10.3f}  {r['max_ms']:>10.3f}")


class TestPDFExportPerformance(unittest.TestCase):
    """Benchmark PDF exporter against progressively larger documents."""

    @classmethod
    def setUpClass(cls):
        cls._sizes = ["5k", "10k", "20k", "50k"]
        cls._results: dict[str, dict] = {}
        for size in cls._sizes:
            doc = _load_fixture(size)
            tokens = parse_markdown(doc)
            exporter = PdfExporter()
            theme = {}
            options = {"custom_css": "", "syntax_theme": "default"}
            cls._results[size] = _benchmark(
                exporter.render, tokens, theme, options, n_runs=3
            )

    def test_pdf_small_document(self):
        r = self._results["5k"]
        self.assertLess(r["max_ms"], 500, f"5K PDF took {r['max_ms']}ms")

    def test_pdf_medium_document(self):
        r = self._results["20k"]
        self.assertLess(r["max_ms"], 3000, f"20K PDF took {r['max_ms']}ms")

    def test_pdf_large_document(self):
        r = self._results["50k"]
        self.assertLess(r["max_ms"], 8000, f"50K PDF took {r['max_ms']}ms")

    def test_pdf_v5_feature_document(self):
        doc = V5_FEATURE_DOC
        tokens = parse_markdown(doc)
        exporter = PdfExporter()
        theme = {}
        options = {"custom_css": "", "syntax_theme": "default"}
        r = _benchmark(exporter.render, tokens, theme, options, n_runs=3)
        self.assertLess(r["max_ms"], 500, f"V5 doc PDF took {r['max_ms']}ms")

    def _print_results(self):
        print("\n=== PDF Export Performance ===")
        print(f"{'Size':>6s}  {'Mean ms':>10s}  {'Min ms':>10s}  {'Max ms':>10s}")
        for size in self._sizes:
            r = self._results[size]
            print(f"{size:>6s}  {r['mean_ms']:>10.3f}  {r['min_ms']:>10.3f}  {r['max_ms']:>10.3f}")


class TestV5FeaturePerformance(unittest.TestCase):
    """Performance tests specifically targeting v5.0 feature parsing/rendering."""

    def test_many_footnotes(self):
        """Document with many footnote references should parse and render fast."""
        refs = "\n".join(
            f"This is text with a reference[^{i}]. " for i in range(1, 51)
        )
        defs = "\n".join(f"[^{i}]: Footnote definition number {i}." for i in range(1, 51))
        doc = f"# Many Footnotes\n{refs}\n\n{defs}\n"
        tokens = parse_markdown(doc)
        r_parse = _benchmark(parse_markdown, doc, n_runs=5)
        r_render = _benchmark(render_terminal, tokens, n_runs=5)
        self.assertLess(r_parse["max_ms"], 100, f"Many-footnote parse took {r_parse['max_ms']}ms")
        self.assertLess(r_render["max_ms"], 100, f"Many-footnote render took {r_render['max_ms']}ms")

    def test_many_task_items(self):
        """Document with many task list items."""
        items = "\n".join(f"- [ ] Item {i}" for i in range(1, 101))
        doc = f"# Tasks\n{items}\n"
        tokens = parse_markdown(doc)
        r_parse = _benchmark(parse_markdown, doc, n_runs=5)
        r_render = _benchmark(render_terminal, tokens, n_runs=5)
        self.assertLess(r_parse["max_ms"], 100, f"Many-task parse took {r_parse['max_ms']}ms")
        self.assertLess(r_render["max_ms"], 100, f"Many-task render took {r_render['max_ms']}ms")

    def test_inline_formatting_density(self):
        """Document with inline formatting on every line."""
        lines = []
        for i in range(200):
            lines.append(
                f"**bold** *italic* `code` ~~strike~~ ==highlight~ "
                f"[link](url) [^1] E=mc^2^ H~2~O **text** on line {i}"
            )
        doc = "\n".join(lines)
        tokens = parse_markdown(doc)
        r_parse = _benchmark(parse_markdown, doc, n_runs=5)
        r_render = _benchmark(render_terminal, tokens, n_runs=5)
        self.assertLess(r_parse["max_ms"], 200, f"Dense-inline parse took {r_parse['max_ms']}ms")
        self.assertLess(r_render["max_ms"], 200, f"Dense-inline render took {r_render['max_ms']}ms")

    def test_nested_list_depth(self):
        """Deeply nested lists should not cause quadratic behavior."""
        # Build a list nested 10 levels deep
        parts = ["- Level 1"]
        for i in range(2, 11):
            parts.append(f"    - Level {i}")
        doc = "\n".join(parts) + "\n"
        tokens = parse_markdown(doc)
        r_parse = _benchmark(parse_markdown, doc, n_runs=5)
        r_render = _benchmark(render_terminal, tokens, n_runs=5)
        self.assertLess(r_parse["max_ms"], 50, f"Deep-nested parse took {r_parse['max_ms']}ms")
        self.assertLess(r_render["max_ms"], 50, f"Deep-nested render took {r_render['max_ms']}ms")


class TestProfileLargeDocument(unittest.TestCase):
    """Use cProfile to analyze hotspots in large document processing.

    This test is annotated as slow and skipped by default.
    Run with: python -m pytest tests/test_performance.py::TestProfileLargeDocument -v
    """

    @unittest.skip("Manual profiling — run explicitly when investigating regressions")
    def test_profile_parse_250k(self):
        doc = _load_fixture("250k")
        profiler = self._profile_fn(parse_markdown, doc)
        self._report(profiler, "parse 250K")

    @unittest.skip("Manual profiling — run explicitly when investigating regressions")
    def test_profile_render_250k(self):
        doc = _load_fixture("250k")
        tokens = parse_markdown(doc)
        profiler = self._profile_fn(render_terminal, tokens)
        self._report(profiler, "render 250K")

    @unittest.skip("Manual profiling — run explicitly when investigating regressions")
    def test_profile_v5_feature_doc(self):
        doc = V5_FEATURE_DOC
        tokens = parse_markdown(doc)
        profiler = self._profile_fn(render_terminal, tokens)
        self._report(profiler, "render v5 features")

    @staticmethod
    def _profile_fn(fn, *args, n: int = 10):
        import cProfile
        import pstats
        import io

        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(n):
            fn(*args)
        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
        stats.print_stats(20)
        return stream.getvalue()

    @staticmethod
    def _report(profile_output: str, label: str):
        print(f"\n=== Profile: {label} ===")
        print(profile_output)


def main():
    """Run performance tests and print summary tables."""
    # Discover and run all test cases
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for cls_name in [
        TestParsePerformance,
        TestRenderPerformance,
        TestHTMLExportPerformance,
        TestPDFExportPerformance,
        TestV5FeaturePerformance,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls_name))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print performance summary tables (only if all passed)
    if result.wasSuccessful():
        for cls in [TestParsePerformance, TestRenderPerformance,
                    TestHTMLExportPerformance, TestPDFExportPerformance]:
            # Trigger setUpClass so results exist
            if hasattr(cls, 'setUpClass'):
                cls.setUpClass()
            # Print via an instance
            instance = cls()
            instance._print_results()


if __name__ == "__main__":
    main()
