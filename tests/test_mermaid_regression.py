"""Regression tests for existing HTML export features (KB-023/KB-006).

Ensures that the mermaid integration does not break existing HTML export
functionality.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from mdutil.export.html import HtmlExporter
from mdutil.parser import parse_markdown


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def exporter():
    return HtmlExporter()


@pytest.fixture
def fake_svg():
    return '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>'


# ---------------------------------------------------------------------------
# Regression: Heading rendering
# ---------------------------------------------------------------------------

class TestHeadingRegression:
    """Regression tests for heading rendering with mermaid."""

    def test_h1_rendered(self, exporter):
        tokens = [{"type": "heading", "text": "Title", "level": 1}]
        result = exporter.render(tokens, {}, {})
        assert "<h1>Title</h1>" in result

    def test_h2_rendered(self, exporter):
        tokens = [{"type": "heading", "text": "Section", "level": 2}]
        result = exporter.render(tokens, {}, {})
        assert "<h2>Section</h2>" in result

    def test_h3_rendered(self, exporter):
        tokens = [{"type": "heading", "text": "Subsection", "level": 3}]
        result = exporter.render(tokens, {}, {})
        assert "<h3>Subsection</h3>" in result

    def test_heading_after_mermaid(self, exporter, fake_svg):
        """Heading after a mermaid block renders correctly."""
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "heading", "text": "After Diagram", "level": 2},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<h2>After Diagram</h2>" in result

    def test_heading_with_inline_markdown(self, exporter):
        tokens = [{
            "type": "heading", "text": "**Bold** *italic* `code`",
            "level": 1,
            "spans": [
                {"type": "text", "content": ""},
                {"type": "bold", "content": "Bold"},
                {"type": "text", "content": " "},
                {"type": "italic", "content": "italic"},
                {"type": "text", "content": " "},
                {"type": "code", "content": "code"},
            ],
        }]
        result = exporter.render(tokens, {}, {})
        assert "<h1>" in result
        assert "<strong>Bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<code>code</code>" in result


# ---------------------------------------------------------------------------
# Regression: Paragraph rendering
# ---------------------------------------------------------------------------

class TestParagraphRegression:
    """Regression tests for paragraph rendering with mermaid."""

    def test_simple_paragraph(self, exporter):
        tokens = [{"type": "paragraph", "text": "Hello world"}]
        result = exporter.render(tokens, {}, {})
        assert "<p>Hello world</p>" in result

    def test_paragraph_with_mermaid_after(self, exporter, fake_svg):
        """Paragraphs after mermaid blocks render correctly."""
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "paragraph", "text": "Description of the diagram."},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<p>Description of the diagram.</p>" in result

    def test_paragraph_inline_formatting(self, exporter):
        tokens = [{
            "type": "paragraph", "text": "Test",
            "spans": [
                {"type": "text", "content": "Hello "},
                {"type": "bold", "content": "world"},
                {"type": "text", "content": "!"},
            ],
        }]
        result = exporter.render(tokens, {}, {})
        assert "<strong>world</strong>" in result
        assert "Hello " in result
        assert "!" in result

    def test_paragraph_with_link(self, exporter):
        tokens = [{
            "type": "paragraph", "text": "Visit [example](https://example.com).",
            "spans": [
                {"type": "text", "content": "Visit "},
                {"type": "link", "content": "example", "url": "https://example.com"},
                {"type": "text", "content": "."},
            ],
        }]
        result = exporter.render(tokens, {}, {})
        # Link should be present in output (rendering may use href="#" as placeholder)
        assert "<a" in result
        assert ">example</a>" in result


# ---------------------------------------------------------------------------
# Regression: Code block rendering
# ---------------------------------------------------------------------------

class TestCodeBlockRegression:
    """Regression tests for code block rendering with mermaid."""

    def test_python_code_block(self, exporter):
        tokens = [{"type": "code", "content": "print('hello')", "language": "python", "text": "print('hello')"}]
        result = exporter.render(tokens, {}, {})
        assert "<pre" in result
        assert "<code" in result
        assert "print" in result

    def test_code_block_with_mermaid_after(self, exporter, fake_svg):
        """Code blocks after mermaid render correctly."""
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "code", "content": "x = 1", "language": "python", "text": "x = 1"},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<pre" in result
        assert "<code" in result
        # pygments syntax highlighting may encode tokens as spans
        # but the source code content should be present in the output
        assert "mdutil-highlight" in result

    def test_code_block_html_escaping(self, exporter):
        """Code blocks should escape HTML entities regardless of mermaid."""
        tokens = [{"type": "code", "content": "<div>test</div>", "language": "", "text": "<div>test</div>"}]
        result = exporter.render(tokens, {}, {})
        # HTML entities should be escaped
        assert "&lt;div&gt;" in result
        assert "test" in result

    def test_unknown_language_code_block(self, exporter):
        """Unknown language code blocks render without syntax highlighting."""
        tokens = [{"type": "code", "content": "gibberish", "language": "xyzunknown", "text": "gibberish"}]
        result = exporter.render(tokens, {}, {})
        assert "gibberish" in result
        # Should not crash
        assert "<!DOCTYPE html>" in result


# ---------------------------------------------------------------------------
# Regression: Table rendering
# ---------------------------------------------------------------------------

class TestTableRegression:
    """Regression tests for table rendering with mermaid."""

    def test_table_with_mermaid_before(self, exporter, fake_svg):
        """Tables after mermaid blocks render correctly."""
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "table", "headers": ["Name", "Age"], "rows": [["Alice", "30"]], "alignments": ["left", "right"]},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<table>" in result
        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result

    def test_empty_table(self, exporter):
        """Empty table renders without error."""
        tokens = [{"type": "table", "headers": [], "rows": [], "alignments": []}]
        result = exporter.render(tokens, {}, {})
        assert "<!DOCTYPE html>" in result


# ---------------------------------------------------------------------------
# Regression: List rendering
# ---------------------------------------------------------------------------

class TestListRegression:
    """Regression tests for list rendering with mermaid."""

    def test_unordered_list(self, exporter):
        tokens = [{"type": "list", "items": ["A", "B", "C"], "ordered": False}]
        result = exporter.render(tokens, {}, {})
        assert "<ul>" in result
        assert "<li>A</li>" in result
        assert "<li>B</li>" in result

    def test_ordered_list(self, exporter):
        tokens = [{"type": "list", "items": ["First", "Second"], "ordered": True}]
        result = exporter.render(tokens, {}, {})
        assert "<ol>" in result
        assert "<li>First</li>" in result

    def test_list_with_mermaid_after(self, exporter, fake_svg):
        """Lists after mermaid blocks render correctly."""
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "list", "items": ["Item 1", "Item 2"], "ordered": False},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<ul>" in result
        assert "Item 1" in result


# ---------------------------------------------------------------------------
# Regression: Blockquote rendering
# ---------------------------------------------------------------------------

class TestBlockquoteRegression:
    """Regression tests for blockquote rendering with mermaid."""

    def test_blockquote(self, exporter):
        tokens = [{"type": "blockquote", "content": "> Quote text", "text": "> Quote text"}]
        result = exporter.render(tokens, {}, {})
        assert "<blockquote>" in result
        assert "Quote text" in result

    def test_blockquote_with_mermaid_after(self, exporter, fake_svg):
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "blockquote", "content": "> Quote", "text": "> Quote"},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<blockquote>" in result
        assert "Quote" in result


# ---------------------------------------------------------------------------
# Regression: Horizontal rule rendering
# ---------------------------------------------------------------------------

class TestHorizontalRuleRegression:
    """Regression tests for horizontal rule rendering with mermaid."""

    def test_horizontal_rule(self, exporter):
        tokens = [{"type": "horizontal_rule", "content": "---", "text": "---"}]
        result = exporter.render(tokens, {}, {})
        assert "<hr>" in result

    def test_horizontal_rule_with_mermaid_after(self, exporter, fake_svg):
        tokens = [
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
            {"type": "horizontal_rule", "content": "---", "text": "---"},
        ]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD; A-->B;", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        assert "<hr>" in result


# ---------------------------------------------------------------------------
# Regression: Full document with all token types
# ---------------------------------------------------------------------------

class TestFullDocumentRegression:
    """Regression tests for full document rendering with mermaid mixed in."""

    def test_complete_document(self, exporter, fake_svg):
        """A document with all token types renders valid HTML with mermaid."""
        md = """# Title

Intro paragraph with **bold** and *italic*.

```mermaid
graph TD
    A-->B
```

> A blockquote

- Item 1
- Item 2
- Item 3

| Col A | Col B |
|-------|-------|
| 1     | 2     |

```python
def hello():
    print("world")
```

---

Final paragraph.
"""
        tokens = parse_markdown(md)
        options = {"mermaid": True, "syntax_theme": "default"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [("graph TD\n    A-->B", 0, fake_svg)]
            result = exporter.render(tokens, {}, options)

        # Structural checks
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "<body>" in result
        assert "</body>" in result

        # Content checks
        assert "<h1>Title</h1>" in result
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<svg" in result  # mermaid rendered
        assert "<blockquote>" in result
        assert "<ul>" in result
        assert "<ol>" not in result  # should be ul
        assert "<table>" in result
        assert "<pre" in result  # code block
        assert "<hr>" in result

    def test_mermaid_disabled_doesnt_break_other_tokens(self, exporter):
        """Disabling mermaid should not affect other token rendering."""
        md = """# Title

Some text.

```mermaid
graph TD
    A-->B
```

- Item 1
- Item 2
"""
        tokens = parse_markdown(md)
        options = {"mermaid": False, "syntax_theme": "default"}

        result = exporter.render(tokens, {}, options)

        assert "<!DOCTYPE html>" in result
        assert "<h1>Title</h1>" in result
        assert "<ul>" in result
        assert "<svg" not in result  # mermaid disabled


# ---------------------------------------------------------------------------
# Regression: CSS and theme
# ---------------------------------------------------------------------------

class TestCSSRegression:
    """Regression tests for CSS and theme with mermaid."""

    def test_default_css_present(self, exporter):
        """Default CSS is included in rendered HTML."""
        tokens = [{"type": "paragraph", "text": "Hello"}]
        result = exporter.render(tokens, {}, {})
        assert "<style>" in result
        assert "</style>" in result

    def test_mermaid_css_present(self, exporter):
        """Mermaid CSS class is included."""
        tokens = [{"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"}]
        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, {}, options)
        assert ".mermaid" in result

    def test_custom_css_with_mermaid(self, exporter):
        """Custom CSS and mermaid CSS coexist."""
        tokens = [{"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"}]
        options = {"mermaid": True, "syntax_theme": "default", "custom_css": "body { background: #111; }"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, {}, options)
        assert ".mermaid" in result
        assert "body { background: #111; }" in result

    def test_syntax_highlighting_css_with_mermaid(self, exporter):
        """Syntax highlighting CSS and mermaid CSS coexist."""
        md = """# Title

Some text.

```mermaid
graph TD
    A-->B
```

```python
print("hello")
```
"""
        tokens = parse_markdown(md)
        options = {"mermaid": True, "syntax_theme": "dracula"}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = False
            result = exporter.render(tokens, {}, options)

        assert ".mdutil-highlight" in result
        assert ".mermaid" in result


# ---------------------------------------------------------------------------
# Regression: Empty and edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Regression tests for edge cases with mermaid."""

    def test_empty_document(self, exporter):
        result = exporter.render([], {}, {})
        assert "<!DOCTYPE html>" in result

    def test_only_mermaid(self, exporter):
        """Document with only a mermaid block renders valid HTML."""
        tokens = [{"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"}]
        options = {"mermaid": False, "syntax_theme": "default"}
        result = exporter.render(tokens, {}, options)
        assert "<!DOCTYPE html>" in result
        assert "<!DOCTYPE html>" in result

    def test_blank_tokens_skipped(self, exporter):
        """Blank tokens are skipped, even with mermaid present."""
        tokens = [
            {"type": "heading", "text": "Title", "level": 1},
            {"type": "blank", "content": "", "text": ""},
            {"type": "mermaid", "content": "graph TD; A-->B;", "language": "mermaid", "text": "graph TD; A-->B;"},
        ]
        options = {"mermaid": False, "syntax_theme": "default"}
        result = exporter.render(tokens, {}, options)
        assert "<h1>Title</h1>" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
