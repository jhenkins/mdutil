"""Comprehensive parser tests for KB-077: All new syntax features.

Tests cross-feature parsing, edge cases, and interaction between features.
Covers: strikethrough, task lists, math, footnotes, sub/superscript,
highlight, definition lists, images, link titles, and nested lists.
"""
import re
import unittest

from mdutil.parser import parse_markdown


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _span_types(tokens: list[dict]) -> list[dict]:
    """Collect all span types from all tokens (convenience)."""
    spans: list[dict] = []
    for t in tokens:
        spans.extend(t.get("spans", []))
    return spans


def _has_span_type(tokens: list[dict], stype: str) -> bool:
    return any(s.get("type") == stype for t in tokens for s in t.get("spans", []))


# ===========================================================================
# Cross-feature: all features in one document
# ===========================================================================

class CrossFeatureParserTests(unittest.TestCase):
    """Parse a document containing every new syntax feature simultaneously."""

    def test_full_document_with_all_features(self):
        md = (
            "# Title\n\n"
            "Paragraph with ~~strike~~, **bold**, *em*, `code`, "
            '[link](url "title"), ![alt](img.png), $E=mc^2$, '
            "[^1], H~2~O, e^2^, ==highlight==.\n\n"
            "- [x] Task 1\n"
            "- [ ] Task 2\n\n"
            "Term\n:   Definition\n\n"
            "[^1]: Footnote."
        )
        tokens = parse_markdown(md)

        # Types present
        types = {t["type"] for t in tokens}
        self.assertIn("heading", types)
        self.assertIn("paragraph", types)
        self.assertIn("list", types)
        self.assertIn("definition", types)
        self.assertIn("footnote_definition", types)

        # All span types present in paragraph
        para = next(t for t in tokens if t["type"] == "paragraph")
        span_types = [s["type"] for s in para["spans"]]
        self.assertIn("strikethrough", span_types)
        self.assertIn("strong", span_types)
        self.assertIn("emphasis", span_types)
        self.assertIn("inline_code", span_types)
        self.assertIn("link", span_types)
        self.assertIn("image", span_types)
        self.assertIn("math", span_types)
        self.assertIn("footnote_ref", span_types)
        self.assertIn("subscript", span_types)
        self.assertIn("superscript", span_types)
        self.assertIn("highlight", span_types)

    def test_link_with_title_parsed(self):
        tokens = parse_markdown('[See docs](https://example.com "Documentation")')
        para = tokens[0]
        link_span = next(s for s in para["spans"] if s["type"] == "link")
        self.assertEqual(link_span.get("title"), "Documentation")

    def test_nested_list_preserves_structure(self):
        md = "- item 1\n  - nested 1\n  - nested 2\n- item 2"
        tokens = parse_markdown(md)
        self.assertEqual(tokens[0]["type"], "list")
        items = tokens[0]["parsed_items"]
        self.assertEqual(len(items), 2)
        self.assertTrue(items[0].get("sub_list"))
        self.assertEqual(len(items[0]["sub_list"]["parsed_items"]), 2)


# ===========================================================================
# Strikethrough edge cases
# ===========================================================================

class StrikethroughEdgeCases(unittest.TestCase):

    def test_consecutive_strikethrough(self):
        tokens = parse_markdown("~~a~~ ~~b~~")
        para = tokens[0]
        self.assertIn("<del>a</del>", para["content"])
        self.assertIn("<del>b</del>", para["content"])

    def test_strikethrough_inside_bold(self):
        tokens = parse_markdown("**~~striked bold~~**")
        para = tokens[0]
        self.assertIn("<del>", para["content"])
        self.assertIn("<strong>", para["content"])

    def test_strikethrough_inside_em(self):
        tokens = parse_markdown("*~~striked em~~*")
        para = tokens[0]
        self.assertIn("<del>", para["content"])
        self.assertIn("<em>", para["content"])

    def test_strikethrough_with_inline_code(self):
        tokens = parse_markdown("~~`code`~~")
        para = tokens[0]
        self.assertIn("<del>", para["content"])
        self.assertIn("<code>code</code>", para["content"])


# ===========================================================================
# Math edge cases
# ===========================================================================

class MathEdgeCases(unittest.TestCase):

    def test_math_with_special_characters(self):
        tokens = parse_markdown("$a + b = c$")
        para = tokens[0]
        self.assertIn("<math>a + b = c</math>", para["content"])

    def test_math_inline_with_surrounding_text(self):
        tokens = parse_markdown("The value $x$ is unknown.")
        para = tokens[0]
        self.assertEqual(para["type"], "paragraph")
        self.assertIn("<math>x</math>", para["content"])

    def test_multiple_math_expressions(self):
        tokens = parse_markdown("$a$ and $b$ and $c$")
        para = tokens[0]
        math_spans = [s for s in para["spans"] if s["type"] == "math"]
        self.assertEqual(len(math_spans), 3)

    def test_math_not_triggered_by_code(self):
        tokens = parse_markdown("`$not math$`")
        para = tokens[0]
        self.assertNotIn("<math>", para["content"])
        self.assertIn("<code>$not math$</code>", para["content"])


# ===========================================================================
# Footnote edge cases
# ===========================================================================

class FootnoteEdgeCases(unittest.TestCase):

    def test_footnote_with_multiple_references(self):
        md = "Text [^1] and [^2].\n\n[^1]: Note 1.\n[^2]: Note 2."
        tokens = parse_markdown(md)
        fn_refs = [s for t in tokens if t.get("spans") for s in t["spans"] if s["type"] == "footnote_ref"]
        self.assertEqual(len(fn_refs), 2)

    def test_footnote_definition_collected(self):
        md = "Text.\n\n[^1]: Footnote text."
        tokens = parse_markdown(md)
        fn_types = [t["type"] for t in tokens]
        self.assertIn("footnote_definition", fn_types)

    def test_footnote_definition_inline_formatting(self):
        md = "Text[^1].\n\n[^1]: A **bold** footnote."
        tokens = parse_markdown(md)
        fn_def = next(t for t in tokens if t["type"] == "footnote_definition")
        self.assertIn("bold", fn_def["content"])


# ===========================================================================
# Subscript / Superscript edge cases
# ===========================================================================

class SubSuperEdgeCases(unittest.TestCase):

    def test_subscript_multiple_chars(self):
        tokens = parse_markdown("H~2~O")
        para = tokens[0]
        self.assertIn("<sub>2</sub>", para["content"])

    def test_superscript_multiple_chars(self):
        tokens = parse_markdown("e^2^")
        para = tokens[0]
        self.assertIn("<sup>2</sup>", para["content"])

    def test_escaped_subscript(self):
        tokens = parse_markdown(r"\~not sub~")
        para = tokens[0]
        self.assertNotIn("<sub>", para["content"])

    def test_escaped_superscript(self):
        tokens = parse_markdown(r"\^not super")
        para = tokens[0]
        self.assertNotIn("<sup>", para["content"])

    def test_unclosed_subscript_literal(self):
        tokens = parse_markdown("~not closed")
        para = tokens[0]
        self.assertNotIn("<sub>", para["content"])


# ===========================================================================
# Highlight edge cases
# ===========================================================================

class HighlightEdgeCases(unittest.TestCase):

    def test_multiple_highlights(self):
        tokens = parse_markdown("==first== and ==second==")
        para = tokens[0]
        self.assertIn("<mark>first</mark>", para["content"])
        self.assertIn("<mark>second</mark>", para["content"])

    def test_highlight_with_bold_inside(self):
        tokens = parse_markdown("==**bold inside**==")
        para = tokens[0]
        self.assertIn("<mark>", para["content"])
        self.assertIn("<strong>", para["content"])

    def test_highlight_not_triggered_by_single_equals(self):
        tokens = parse_markdown("= not highlight")
        para = tokens[0]
        self.assertNotIn("<mark>", para["content"])

    def test_highlight_with_inline_code(self):
        tokens = parse_markdown("==`code`==")
        para = tokens[0]
        self.assertIn("<mark>", para["content"])
        self.assertIn("<code>code</code>", para["content"])


# ===========================================================================
# Definition list edge cases
# ===========================================================================

class DefinitionListEdgeCases(unittest.TestCase):

    def test_definition_followed_by_paragraph(self):
        md = "Term\n:   Definition\n\nParagraph text."
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        self.assertIn("definition", types)
        self.assertIn("paragraph", types)

    def test_definition_not_triggered_by_colon_in_paragraph(self):
        tokens = parse_markdown("See: this is a paragraph.")
        # Should be a paragraph, not a definition
        self.assertEqual(tokens[0]["type"], "paragraph")

    def test_definition_with_inline_formatting(self):
        md = "Term\n:   **Bold** and *em* definition."
        tokens = parse_markdown(md)
        defn = next(t for t in tokens if t["type"] == "definition")
        self.assertIn("<strong>", defn["content"])
        self.assertIn("<em>", defn["content"])


# ===========================================================================
# Image edge cases
# ===========================================================================

class ImageEdgeCases(unittest.TestCase):

    def test_image_with_dimensions(self):
        tokens = parse_markdown("![alt](img.png =300x200)")
        para = tokens[0]
        self.assertIn('<img src="img.png"', para["content"])
        self.assertIn('width="300"', para["content"])
        self.assertIn('height="200"', para["content"])

    def test_image_with_width_only(self):
        tokens = parse_markdown("![alt](img.png =300x200)")
        para = tokens[0]
        self.assertIn('width="300"', para["content"])
        self.assertIn('height="200"', para["content"])

    def test_image_not_confused_with_link(self):
        # ![alt](url) should be image, not link
        tokens = parse_markdown("![alt](url)")
        para = tokens[0]
        image_spans = [s for s in para["spans"] if s["type"] == "image"]
        link_spans = [s for s in para["spans"] if s["type"] == "link"]
        self.assertEqual(len(image_spans), 1)
        self.assertEqual(len(link_spans), 0)


# ===========================================================================
# Task list edge cases
# ===========================================================================

class TaskListEdgeCases(unittest.TestCase):

    def test_mixed_task_and_regular_items(self):
        md = "- [x] Done\n- Regular\n- [ ] Todo"
        tokens = parse_markdown(md)
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0]["task"])
        self.assertTrue(items[0]["checked"])
        self.assertFalse(items[1]["task"])
        self.assertTrue(items[2]["task"])
        self.assertFalse(items[2]["checked"])

    def test_task_list_in_ordered_list(self):
        md = "1. [x] First\n2. [ ] Second"
        tokens = parse_markdown(md)
        self.assertTrue(tokens[0]["task"])
        self.assertTrue(tokens[0]["ordered"])
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0]["checked"])
        self.assertFalse(items[1]["checked"])


# ===========================================================================
# Nested list edge cases
# ===========================================================================

class NestedListEdgeCases(unittest.TestCase):

    def test_deep_nesting_three_levels(self):
        md = "- l1\n  - l2\n    - l3"
        tokens = parse_markdown(md)
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0].get("sub_list"))
        sub_items = items[0]["sub_list"]["parsed_items"]
        self.assertTrue(sub_items[0].get("sub_list"))

    def test_separate_lists_not_merged(self):
        md = "- a\n- b\n\n- c\n- d"
        tokens = parse_markdown(md)
        list_tokens = [t for t in tokens if t["type"] == "list"]
        self.assertEqual(len(list_tokens), 2)


# ===========================================================================
# Link title edge cases
# ===========================================================================

class LinkTitleEdgeCases(unittest.TestCase):

    def test_double_quoted_title(self):
        tokens = parse_markdown('[text](url "double title")')
        link = next(s for s in tokens[0]["spans"] if s["type"] == "link")
        self.assertEqual(link["title"], "double title")

    def test_single_quoted_title(self):
        tokens = parse_markdown("[text](url 'single title')")
        link = next(s for s in tokens[0]["spans"] if s["type"] == "link")
        self.assertEqual(link["title"], "single title")

    def test_no_title(self):
        tokens = parse_markdown("[text](url)")
        link = next(s for s in tokens[0]["spans"] if s["type"] == "link")
        self.assertNotIn("title", link)

    def test_url_with_query_params(self):
        tokens = parse_markdown('[text](https://example.com?a=1&b=2 "Title")')
        link = next(s for s in tokens[0]["spans"] if s["type"] == "link")
        self.assertEqual(link["href"], "https://example.com?a=1&b=2")
        self.assertEqual(link["title"], "Title")


# ===========================================================================
# Combined interaction tests
# ===========================================================================

class ParserInteractionTests(unittest.TestCase):
    """Test how features interact when combined in complex documents."""

    def test_strikethrough_in_list(self):
        md = "- ~~deleted item~~"
        tokens = parse_markdown(md)
        self.assertEqual(tokens[0]["type"], "list")
        items = tokens[0]["parsed_items"]
        self.assertIn("<del>", items[0]["content"])

    def test_task_with_inline_formatting(self):
        md = "- [x] **Done** with *emphasis* and `code`"
        tokens = parse_markdown(md)
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0]["checked"])
        self.assertIn("<strong>", items[0]["content"])
        self.assertIn("<em>", items[0]["content"])
        self.assertIn("<code>", items[0]["content"])

    def test_math_with_surrounding_formatting(self):
        tokens = parse_markdown("The **equation** $E=mc^2$ is **famous**.")
        para = tokens[0]
        self.assertIn("<strong>", para["content"])
        self.assertIn("<math>E=mc^2</math>", para["content"])

    def test_footnote_with_link_in_definition(self):
        md = "Text[^1].\n\n[^1]: See [link](url) for details."
        tokens = parse_markdown(md)
        fn_def = next(t for t in tokens if t["type"] == "footnote_definition")
        self.assertIn("<a", fn_def["content"])

    def test_nested_list_with_task_items(self):
        md = "- [x] Top task\n  - [ ] Sub task"
        tokens = parse_markdown(md)
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0]["checked"])
        sub = items[0]["sub_list"]
        self.assertTrue(sub["task"])
        sub_items = sub["parsed_items"]
        self.assertFalse(sub_items[0]["checked"])


if __name__ == "__main__":
    unittest.main()
