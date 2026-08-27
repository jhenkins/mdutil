"""Tests for inline parsing in table cells.

Verifies that `$math$`, `**bold**`, `*italic*`, etc. work inside table cells.
"""

from __future__ import annotations

import pytest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


class TestTableInlineParsing:
    """Table cells should get inline parsing applied."""

    def test_math_in_table_cell(self):
        md = "| A | B |\n| --- | --- |\n| $E = mc^2$ | test |"
        tokens = parse_markdown(md)
        # Find the table token
        table_token = next(t for t in tokens if t["type"] == "table")
        # First data row, first cell should have math tags
        assert "<math>" in table_token["rows"][0][0]

    def test_math_rendered_in_terminal_table(self):
        md = "| A | B |\n| --- | --- |\n| $E = mc^2$ | test |"
        tokens = parse_markdown(md)
        result = render(tokens)
        # Should not contain raw $ delimiters
        assert "$E = mc^2$" not in result
        # Should contain the math content
        assert "E = mc^2" in result

    def test_bold_in_table_cell(self):
        md = "| **bold** | normal |\n| --- | --- |\n| more | text |"
        tokens = parse_markdown(md)
        table_token = next(t for t in tokens if t["type"] == "table")
        # Check header cell (first header)
        assert "<strong>" in table_token["headers"][0]

    def test_bold_rendered_in_terminal_table(self):
        md = "| **bold** | normal |\n| --- | --- |\n| more | text |"
        tokens = parse_markdown(md)
        result = render(tokens)
        # Should not contain raw ** delimiters
        assert "**bold**" not in result
        # Should contain the bold content
        assert "bold" in result

    def test_italic_in_table_cell(self):
        md = "| *italic* | normal |\n| --- | --- |\n| more | text |"
        tokens = parse_markdown(md)
        table_token = next(t for t in tokens if t["type"] == "table")
        # Check header cell (first header)
        assert "<em>" in table_token["headers"][0]

    def test_italic_rendered_in_terminal_table(self):
        md = "| *italic* | normal |\n| --- | --- |\n| more | text |"
        tokens = parse_markdown(md)
        result = render(tokens)
        # Should not contain raw * delimiters
        assert "*italic*" not in result
        # Should contain the italic content
        assert "italic" in result
