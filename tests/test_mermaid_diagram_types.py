"""Unit tests for mermaid diagram type rendering (KB-023/KB-006).

Tests that all supported diagram types are detected by the parser and
rendered correctly through the HTML exporter pipeline with a mock
merman-cli binary.
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
def fake_merman(tmp_path):
    """Create a fake merman-cli that echoes <svg>ok</svg>."""
    fake_bin = tmp_path / "merman-cli-linux-x86_64"
    fake_bin.write_text('#!/bin/sh\necho \'<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>\'\n')
    fake_bin.chmod(0o755)
    return fake_bin


def _mock_renderer(exporter, fake_bin, available=True):
    """Patch MermanRenderer to use a fake binary."""
    real_renderer_cls = exporter.__class__.__bases__[0] if hasattr(exporter.__class__, '__bases__') else type(exporter)

    class FakeMermanRenderer:
        def __init__(self, **kwargs):
            self.available = available
            self._binary_path = fake_bin
            self._timeout = 5

        def render_mermaid_svg(self, mermaid_code, theme="default"):
            return '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>'

        def render_diagrams(self, diagrams, theme="default"):
            return [(code, idx, '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>') for idx, (code, _) in enumerate(diagrams)]

    return FakeMermanRenderer()


# ---------------------------------------------------------------------------
# Parser: All diagram types detected
# ---------------------------------------------------------------------------

class TestDiagramTypeDetection:
    """Tests that parser recognizes all mermaid diagram types."""

    FLOWCHART = "graph TD\n    A-->B"
    SEQUENCE = "sequenceDiagram\n    A->>B: hi"
    STATE = "stateDiagram-v2\n    [*] --> A\n    A --> [*]"
    CLASS = "classDiagram\n    class A { int x; }"
    GANTT = "gantt\n    title Project\n    section Phase 1\n    Task 1 :a1, 2024-01-01, 30d"
    PIE = "pie title Pets\n    \"Dogs\" : 40\n    \"Cats\" : 30"
    GIT = "gitGraph\n    commit\n    branch develop\n    checkout develop"
    ER = "erDiagram\n    CUSTOMER ||--o{ ORDER : places"
    USER_JOURNEY = "userjourney\n    title My Journey\n    section Section 1\n      Task 1 : 5: Done"
    SANKEY = "sankey-beta\n    A,B,1"

    DIAGRAM_TYPES = {
        "flowchart": FLOWCHART,
        "sequence": SEQUENCE,
        "state": STATE,
        "class": CLASS,
        "gantt": GANTT,
        "pie": PIE,
        "git": GIT,
        "er": ER,
        "userjourney": USER_JOURNEY,
        "sankey": SANKEY,
    }

    @pytest.mark.parametrize("name,diagram", DIAGRAM_TYPES.items())
    def test_parser_detects_diagram_type(self, name, diagram):
        md = f"```mermaid\n{diagram}\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1, f"Expected 1 mermaid token for {name}, got {len(mermaid_tokens)}"
        assert diagram in mermaid_tokens[0]["content"]

    @pytest.mark.parametrize("name,diagram", DIAGRAM_TYPES.items())
    def test_diagram_content_preserved(self, name, diagram):
        md = f"```mermaid\n{diagram}\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        # Verify key parts of the diagram are preserved
        assert len(mermaid_tokens[0]["content"].strip()) > 0

    def test_all_diagram_types_count(self):
        """All diagram types should be detected in a single document."""
        types_dict = TestDiagramTypeDetection.DIAGRAM_TYPES
        md = "\n\n".join(f"```mermaid\n{d}\n```" for d in types_dict.values())
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == len(types_dict)


# ---------------------------------------------------------------------------
# HTML Export: All diagram types render with SVG
# ---------------------------------------------------------------------------

class TestDiagramTypeRendering:
    """Tests that all diagram types render to SVG in HTML export."""

    @pytest.mark.parametrize("name,diagram", [
        ("flowchart", "graph TD\n    A-->B"),
        ("sequence", "sequenceDiagram\n    A->>B: hi"),
        ("state", "stateDiagram-v2\n    [*] --> A\n    A --> [*]"),
        ("class", "classDiagram\n    class A { int x; }"),
    ])
    def test_diagram_type_renders_svg(self, exporter, fake_merman, name, diagram):
        """Each diagram type should produce SVG output when merman is available."""
        tokens = parse_markdown(f"```mermaid\n{diagram}\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (diagram, 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            result = exporter.render(tokens, {}, options)

        assert "<svg" in result, f"Diagram type {name} should produce SVG output"
        assert "mermaid" in result.lower()

    def test_gantt_diagram_renders_svg(self, exporter, fake_merman):
        """Gantt diagrams should render to SVG."""
        tokens = parse_markdown("```mermaid\ngantt\n    title Project\n    section Phase 1\n    Task 1 :a1, 2024-01-01, 30d\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (mermaid_tokens[0]["content"], 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            result = exporter.render(tokens, {}, options)

        assert "<svg" in result

    def test_pie_diagram_renders_svg(self, exporter, fake_merman):
        """Pie charts should render to SVG."""
        tokens = parse_markdown("```mermaid\npie title Pets\n    \"Dogs\" : 40\n    \"Cats\" : 30\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (mermaid_tokens[0]["content"], 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            result = exporter.render(tokens, {}, options)

        assert "<svg" in result

    def test_git_diagram_renders_svg(self, exporter, fake_merman):
        """Git graphs should render to SVG."""
        tokens = parse_markdown("```mermaid\ngitGraph\n    commit\n    branch develop\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (mermaid_tokens[0]["content"], 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            result = exporter.render(tokens, {}, options)

        assert "<svg" in result

    def test_er_diagram_renders_svg(self, exporter, fake_merman):
        """ER diagrams should render to SVG."""
        tokens = parse_markdown("```mermaid\nerDiagram\n    CUSTOMER ||--o{ ORDER : places\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (mermaid_tokens[0]["content"], 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            result = exporter.render(tokens, {}, options)

        assert "<svg" in result


# ---------------------------------------------------------------------------
# Rendering: Theme passthrough for different diagram types
# ---------------------------------------------------------------------------

class TestDiagramTypeThemes:
    """Tests that theme configuration works for all diagram types."""

    THEMES = ["default", "forest", "dark", "neutral"]

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_passed_for_flowchart(self, exporter, fake_merman, theme):
        tokens = parse_markdown("```mermaid\ngraph TD\n    A-->B\n```")
        options = {"mermaid": True, "syntax_theme": "default", "mermaid_theme": theme}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                ("graph TD\n    A-->B", 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            exporter.render(tokens, {}, options)

            call_kwargs = instance.render_diagrams.call_args[1]
            assert call_kwargs["theme"] == theme

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_passed_for_sequence(self, exporter, fake_merman, theme):
        tokens = parse_markdown("```mermaid\nsequenceDiagram\n    A->>B: hi\n```")
        options = {"mermaid": True, "syntax_theme": "default", "mermaid_theme": theme}

        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                ("sequenceDiagram\n    A->>B: hi", 0, '<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            ]
            exporter.render(tokens, {}, options)

            call_kwargs = instance.render_diagrams.call_args[1]
            assert call_kwargs["theme"] == theme


# ---------------------------------------------------------------------------
# Rendering: Invalid mermaid syntax across diagram types
# ---------------------------------------------------------------------------

class TestDiagramTypeInvalidSyntax:
    """Tests that invalid mermaid syntax is handled gracefully for all types."""

    INVALID_DIAGRAMS = [
        ("graph", "graph TD ; ; ; ;"),
        ("sequence", "sequenceDiagram --- invalid syntax ---"),
        ("state", "stateDiagram-v2 ; ; ;"),
        ("class", "classDiagram {invalid}"),
    ]

    @pytest.mark.parametrize("name,diagram", INVALID_DIAGRAMS)
    def test_invalid_syntax_returns_error_comment(self, exporter, name, diagram):
        """Invalid mermaid syntax should produce an error comment in output."""
        tokens = parse_markdown(f"```mermaid\n{diagram}\n```")
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

        options = {"mermaid": True, "syntax_theme": "default"}
        with patch("mdutil.export.html.MermanRenderer") as MockRenderer:
            instance = MockRenderer.return_value
            instance.available = True
            instance.render_diagrams.return_value = [
                (diagram, 0, "<!-- render error: invalid syntax -->")
            ]
            result = exporter.render(tokens, {}, options)

        # Should contain error indicator
        assert "error" in result.lower() or "could not" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
