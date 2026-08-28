"""Tests for nested list parsing, rendering, and export.

Covers:
- 1, 2, 3 levels of nesting
- Mixed ordered/unordered nesting
- Nested lists with inline formatting (bold, italic, code)
- Empty nested lists (items with no sub-items)
- Nested task lists
"""

import re
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render
from mdutil.export.html import HtmlExporter
from mdutil.export.pdf import PdfExporter


class NestedListParserTests(unittest.TestCase):
    """Parser: nested list structure preservation."""

    def _parse(self, md: str):
        return parse_markdown(md)

    # ---- 1 level of nesting ----

    def test_one_level_of_nesting(self):
        tokens = self._parse("- a\n  - b\n  - c\n- d")
        lst = tokens[0]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(lst["items"], ["a", "d"])
        parsed = lst["parsed_items"]
        self.assertEqual(parsed[0]["text"], "a")
        self.assertIsNotNone(parsed[0].get("sub_list"))
        sub = parsed[0]["sub_list"]
        self.assertEqual(sub["items"], ["b", "c"])
        self.assertEqual(sub["parsed_items"][0]["text"], "b")
        self.assertEqual(sub["parsed_items"][1]["text"], "c")
        self.assertEqual(parsed[1]["text"], "d")
        self.assertIsNone(parsed[1].get("sub_list"))

    def test_one_level_ordered_nested(self):
        tokens = self._parse("1. a\n   1. first\n   2. second\n2. b")
        lst = tokens[0]
        self.assertTrue(lst["ordered"])
        sub = lst["parsed_items"][0]["sub_list"]
        self.assertEqual(sub["items"], ["first", "second"])
        self.assertTrue(sub["ordered"])

    # ---- 2 levels of nesting ----

    def test_two_levels_of_nesting(self):
        md = "- top\n  - mid\n    - deep\n  - mid2\n- end"
        tokens = self._parse(md)
        lst = tokens[0]
        top = lst["parsed_items"][0]
        self.assertEqual(top["text"], "top")
        sub1 = top["sub_list"]
        self.assertEqual(sub1["items"], ["mid", "mid2"])
        mid = sub1["parsed_items"][0]
        self.assertEqual(mid["text"], "mid")
        self.assertIsNotNone(mid.get("sub_list"))
        deep = mid["sub_list"]
        self.assertEqual(deep["items"], ["deep"])

    def test_three_levels_of_nesting(self):
        md = "- l1\n  - l2\n    - l3\n      - l4"
        tokens = self._parse(md)
        lst = tokens[0]
        item = lst["parsed_items"][0]
        self.assertEqual(item["text"], "l1")
        l2 = item["sub_list"]["parsed_items"][0]
        self.assertEqual(l2["text"], "l2")
        l3 = l2["sub_list"]["parsed_items"][0]
        self.assertEqual(l3["text"], "l3")
        l4 = l3["sub_list"]["parsed_items"][0]
        self.assertEqual(l4["text"], "l4")

    # ---- Mixed ordered/unordered ----

    def test_mixed_ordered_under_unordered(self):
        tokens = self._parse("- bullet\n  1. numbered\n  2. also")
        lst = tokens[0]
        sub = lst["parsed_items"][0]["sub_list"]
        self.assertEqual(sub["items"], ["numbered", "also"])
        self.assertTrue(sub["ordered"])

    def test_mixed_unordered_under_ordered(self):
        tokens = self._parse("1. first\n   - bullet\n   - another")
        lst = tokens[0]
        sub = lst["parsed_items"][0]["sub_list"]
        self.assertEqual(sub["items"], ["bullet", "another"])
        self.assertFalse(sub["ordered"])

    def test_separate_unordered_and_ordered_lists_not_merged(self):
        tokens = self._parse("- bullet\n1. number")
        self.assertEqual([t["type"] for t in tokens], ["list", "list"])
        self.assertFalse(tokens[0]["ordered"])
        self.assertTrue(tokens[1]["ordered"])

    # ---- Nested with inline formatting ----

    def test_nested_with_bold(self):
        tokens = self._parse("- item\n  - **bold** nested")
        sub = tokens[0]["parsed_items"][0]["sub_list"]
        sub_text = sub["parsed_items"][0]["text"]
        self.assertEqual(sub_text, "**bold** nested")

    def test_nested_with_code(self):
        tokens = self._parse("- item\n  - `code` nested")
        sub = tokens[0]["parsed_items"][0]["sub_list"]
        sub_text = sub["parsed_items"][0]["text"]
        self.assertEqual(sub_text, "`code` nested")

    def test_nested_with_italic(self):
        tokens = self._parse("- item\n  - *italic* nested")
        sub = tokens[0]["parsed_items"][0]["sub_list"]
        sub_text = sub["parsed_items"][0]["text"]
        self.assertEqual(sub_text, "*italic* nested")

    # ---- Nested task lists ----

    def test_nested_task_list(self):
        tokens = self._parse("- [ ] todo\n  - [x] done\n  - [ ] todo2")
        lst = tokens[0]
        self.assertTrue(lst["task"])
        sub = lst["parsed_items"][0]["sub_list"]
        sub_items = sub["parsed_items"]
        self.assertTrue(sub_items[0]["task"])
        self.assertTrue(sub_items[0]["checked"])
        self.assertTrue(sub_items[1]["task"])
        self.assertFalse(sub_items[1]["checked"])

    # ---- Blank lines between items ----

    def test_blank_line_does_not_merge_separate_lists(self):
        """A blank line between unordered and ordered lists should keep them separate."""
        tokens = self._parse("- one\n- two\n\n1. first\n2. second")
        lists = [t for t in tokens if t["type"] == "list"]
        self.assertEqual(len(lists), 2)
        self.assertFalse(lists[0]["ordered"])
        self.assertTrue(lists[1]["ordered"])


class NestedListRendererTests(unittest.TestCase):
    """Terminal renderer: nested list display."""

    def _render(self, md: str) -> str:
        tokens = parse_markdown(md)
        return render(tokens)

    def test_one_level_nested_render(self):
        result = self._render("- a\n  - b\n  - c")
        lines = result.split("\n")
        self.assertEqual(lines[0], "- a")
        self.assertEqual(lines[1], "  - b")
        self.assertEqual(lines[2], "  - c")

    def test_two_level_nested_render(self):
        result = self._render("- top\n  - mid\n    - deep")
        lines = result.split("\n")
        self.assertEqual(lines[0], "- top")
        self.assertEqual(lines[1], "  - mid")
        self.assertEqual(lines[2], "    - deep")

    def test_mixed_nested_render(self):
        result = self._render("- bullet\n  1. numbered")
        lines = result.split("\n")
        self.assertEqual(lines[0], "- bullet")
        self.assertEqual(lines[1], "  1. numbered")

    def test_nested_task_list_render(self):
        result = self._render("- [ ] todo\n  - [x] done")
        # ANSI codes wrap checkbox symbols with theme colors — strip for assertion
        plain = re.sub(r"\x1b\[[0-9;]*m", "", result)
        self.assertIn("☐ todo", plain)
        self.assertIn("☑ done", plain)


class NestedListHtmlTests(unittest.TestCase):
    """HTML exporter: nested list rendering."""

    def _render(self, md: str) -> str:
        tokens = parse_markdown(md)
        return HtmlExporter().render(tokens, {}, {})

    def test_one_level_nested(self):
        result = self._render("- a\n  - b\n  - c")
        # Sub-list <ul> should be nested inside the parent <li>
        idx_a = result.index("<li>a")
        # Find the matching </li> that closes the outer list's <li>a
        depth = 1
        pos = idx_a + len("<li>a")
        while depth > 0 and pos < len(result):
            if result[pos:pos + 4] == "<li>":
                depth += 1
            elif result[pos:pos + 5] == "</li>":
                depth -= 1
                if depth == 0:
                    between = result[idx_a:pos + 5]
                    self.assertIn("<ul>", between)
            pos += 1

    def test_two_level_nested(self):
        result = self._render("- top\n  - mid\n    - deep")
        # Should have nested <ul> elements
        self.assertGreater(result.count("<ul>"), 1)


class NestedListPdfTests(unittest.TestCase):
    """PDF exporter: nested list rendering."""

    def _render(self, md: str) -> bytes:
        tokens = parse_markdown(md)
        return PdfExporter().render(tokens, {}, {})

    def test_one_level_nested(self):
        pdf_bytes = self._render("- a\n  - b")
        self.assertGreater(len(pdf_bytes), 0)
        # PDF should contain text content
        text = pdf_bytes.decode("latin-1", errors="ignore")
        self.assertIn("a", text)
        self.assertIn("b", text)

    def test_two_level_nested(self):
        pdf_bytes = self._render("- top\n  - mid\n    - deep")
        # PDF should be valid (starts with %PDF header and ends with %%EOF)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(pdf_bytes.endswith(b"%%EOF\n"))
        # Should produce a non-trivial PDF
        self.assertGreater(len(pdf_bytes), 500)


if __name__ == "__main__":
    unittest.main()
