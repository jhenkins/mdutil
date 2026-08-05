"""Unit tests for mermaid block detection in the parser (KB-021)."""

from __future__ import annotations

import pytest

from mdutil.parser import is_mermaid_block, parse_markdown


# ---------------------------------------------------------------------------
# is_mermaid_block
# ---------------------------------------------------------------------------

class TestIsMermaidBlock:
    """Tests for is_mermaid_block()."""

    def test_mermaid_language(self):
        assert is_mermaid_block("mermaid") is True

    def test_mermaid_uppercase(self):
        assert is_mermaid_block("MERMAID") is True

    def test_mermaid_mixed_case(self):
        assert is_mermaid_block("Mermaid") is True

    def test_mermaid_with_extra_info(self):
        assert is_mermaid_block("mermaid: title") is True

    def test_python_not_mermaid(self):
        assert is_mermaid_block("python") is False

    def test_none_language(self):
        assert is_mermaid_block(None) is False

    def test_empty_string(self):
        assert is_mermaid_block("") is False


# ---------------------------------------------------------------------------
# Parser mermaid detection
# ---------------------------------------------------------------------------

class TestParseMermaidBlocks:
    """Tests for mermaid block parsing in parse_markdown()."""

    def test_single_mermaid_block(self):
        md = "```mermaid\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1
        assert mermaid_tokens[0]["content"] == "graph TD; A-->B;"
        assert mermaid_tokens[0]["language"] == "mermaid"

    def test_mermaid_block_preserves_multiline(self):
        md = "```mermaid\ngraph TD\n  A-->B\n  B-->C\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1
        assert "A-->B" in mermaid_tokens[0]["content"]
        assert "B-->C" in mermaid_tokens[0]["content"]

    def test_mermaid_with_heading_around(self):
        md = "# Title\n\n```mermaid\ngraph TD; A-->B;\n```\n\nMore text."
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        assert "heading" in types
        assert "mermaid" in types
        assert "paragraph" in types

    def test_multiple_mermaid_blocks(self):
        md = "```mermaid\ngraph TD; A-->B;\n```\n\n```mermaid\nsequenceDiagram\n  A->>B: hi\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 2
        assert "graph TD" in mermaid_tokens[0]["content"]
        assert "sequenceDiagram" in mermaid_tokens[1]["content"]

    def test_mermaid_case_insensitive(self):
        md = "```Mermaid\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

    def test_mermaid_with_tilde_fences(self):
        md = "~~~mermaid\ngraph TD; A-->B;\n~~~"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1
        assert mermaid_tokens[0]["content"] == "graph TD; A-->B;"

    def test_mermaid_token_has_text_field(self):
        md = "```mermaid\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert "text" in mermaid_tokens[0]
        assert mermaid_tokens[0]["text"] == mermaid_tokens[0]["content"]

    def test_mermaid_not_confused_with_other_languages(self):
        md = "```python\nprint('hello')\n```\n\n```mermaid\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        assert types.count("code") == 1
        assert types.count("mermaid") == 1

    def test_mermaid_with_info_string_after_language(self):
        md = "```mermaid: my-diagram\ngraph TD; A-->B;\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1

    def test_mermaid_interleaved_with_paragraphs(self):
        md = "Para 1.\n\n```mermaid\ngraph TD; A-->B;\n```\n\nPara 2."
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        assert "paragraph" in types
        assert "mermaid" in types
        # Mermaid should appear between the two paragraphs
        mermaid_idx = types.index("mermaid")
        para_indices = [i for i, t in enumerate(types) if t == "paragraph"]
        assert para_indices[0] < mermaid_idx < para_indices[-1]

    def test_empty_mermaid_block(self):
        md = "```mermaid\n\n```"
        tokens = parse_markdown(md)
        mermaid_tokens = [t for t in tokens if t["type"] == "mermaid"]
        assert len(mermaid_tokens) == 1
        assert mermaid_tokens[0]["content"] == ""
