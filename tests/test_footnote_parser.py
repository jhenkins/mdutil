"""Tests for KB-057: Footnote definitions and references in parser."""
import unittest

from mdutil.parser import parse_markdown


class FootnoteParserTests(unittest.TestCase):
    def test_parse_footnote_definition_basic(self):
        """Footnote definition at document end is extracted."""
        md = "Some text.\n\n[^1]: This is a footnote."
        tokens = parse_markdown(md)
        # Should have a footnote_definition token
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        self.assertEqual(fn_tokens[0]["id"], "1")
        self.assertEqual(fn_tokens[0]["content"], "This is a footnote.")

    def test_parse_footnote_definition_with_alphanumeric_id(self):
        """Footnote definition with alphanumeric index."""
        md = "Text here.\n\n[^abc123]: A footnote with alphanumeric index."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        self.assertEqual(fn_tokens[0]["id"], "abc123")
        self.assertEqual(fn_tokens[0]["content"], "A footnote with alphanumeric index.")

    def test_parse_footnote_reference_inline(self):
        """Footnote reference [^1] in inline text is detected."""
        md = "Text with a footnote[^1] reference."
        tokens = parse_markdown(md)
        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn("<fnref", tokens[0]["content"])
        self.assertIn('id="1"', tokens[0]["content"])
        self.assertIn("footnote_ref", [s["type"] for s in tokens[0]["spans"]])

    def test_parse_footnote_reference_with_id(self):
        """Footnote reference preserves the footnote ID."""
        md = "See here[^2] for details."
        tokens = parse_markdown(md)
        ref_spans = [s for s in tokens[0]["spans"] if s["type"] == "footnote_ref"]
        self.assertEqual(len(ref_spans), 1)
        self.assertEqual(ref_spans[0]["id"], "2")

    def test_parse_multiple_footnote_references(self):
        """Multiple footnote references in same paragraph."""
        md = "First[^1] and second[^2] references."
        tokens = parse_markdown(md)
        ref_spans = [s for s in tokens[0]["spans"] if s["type"] == "footnote_ref"]
        self.assertEqual(len(ref_spans), 2)
        self.assertEqual(ref_spans[0]["id"], "1")
        self.assertEqual(ref_spans[1]["id"], "2")

    def test_parse_footnote_definition_and_reference(self):
        """Footnote definition collected and reference detected."""
        md = "Text[^1].\n\n[^1]: Footnote content."
        tokens = parse_markdown(md)
        # Should have paragraph with reference
        para = tokens[0]
        self.assertEqual(para["type"], "paragraph")
        self.assertIn("<fnref", para["content"])
        # Should have footnote definition at end
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        self.assertEqual(fn_tokens[0]["id"], "1")
        self.assertEqual(fn_tokens[0]["content"], "Footnote content.")

    def test_parse_multiple_footnote_definitions(self):
        """Multiple footnote definitions collected."""
        md = "Text with refs.\n\n[^1]: First footnote.\n\n[^2]: Second footnote."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 2)
        self.assertEqual(fn_tokens[0]["id"], "1")
        self.assertEqual(fn_tokens[1]["id"], "2")

    def test_parse_footnote_definition_with_inline_formatting(self):
        """Footnote definition can contain inline formatting."""
        md = "Text.\n\n[^1]: A **bold** footnote with *emphasis*."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        # Content should have inline tags
        self.assertIn("<strong>bold</strong>", fn_tokens[0]["content"])
        self.assertIn("<em>emphasis</em>", fn_tokens[0]["content"])

    def test_parse_no_footnote_definitions(self):
        """Document without footnotes has no footnote_definition tokens."""
        md = "Just a normal paragraph.\n\nAnother paragraph."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 0)

    def test_parse_footnote_definition_in_middle(self):
        """Footnote definition in middle of document is still collected."""
        md = "Before.\n\n[^1]: Footnote.\n\nAfter."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        # Main tokens should have 2 paragraphs (before and after)
        para_tokens = [t for t in tokens if t["type"] == "paragraph"]
        self.assertEqual(len(para_tokens), 2)

    def test_parse_footnote_reference_in_list(self):
        """Footnote reference in list item."""
        md = "- Item with ref[^1]\n\n[^1]: Footnote."
        tokens = parse_markdown(md)
        list_token = [t for t in tokens if t["type"] == "list"][0]
        # The list item text should have fnref tag
        self.assertIn("<fnref", list_token["parsed_items"][0]["content"])

    def test_parse_footnote_definition_preserves_text_field(self):
        """Footnote definition token has text field."""
        md = "Text.\n\n[^1]: This is the footnote text."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        self.assertEqual(fn_tokens[0]["text"], "This is the footnote text.")


class FootnoteParserEdgeCases(unittest.TestCase):
    def test_parse_footnote_definition_optional_space(self):
        """Footnote definition with optional space after colon."""
        md = "Text.\n\n[^1]:Footnote without space."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        # Content should be trimmed
        self.assertEqual(fn_tokens[0]["content"], "Footnote without space.")

    def test_parse_footnote_reference_in_code(self):
        """Footnote reference in inline code is not detected."""
        md = "Use `[^1]` literally."
        tokens = parse_markdown(md)
        ref_spans = [s for s in tokens[0]["spans"] if s["type"] == "footnote_ref"]
        self.assertEqual(len(ref_spans), 0)
        # Should have inline code
        self.assertIn("<code>", tokens[0]["content"])

    def test_parse_footnote_definition_with_inline_formatting(self):
        """Footnote definition with inline formatting."""
        md = "Text.\n\n[^1]: A **bold** footnote with *emphasis*."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        # Content should have inline tags
        self.assertIn("<strong>bold</strong>", fn_tokens[0]["content"])
        self.assertIn("<em>emphasis</em>", fn_tokens[0]["content"])

    def test_parse_footnote_definition_with_links(self):
        """Footnote definition with link."""
        md = "Text.\n\n[^1]: Visit [example](https://example.com)."
        tokens = parse_markdown(md)
        fn_tokens = [t for t in tokens if t["type"] == "footnote_definition"]
        self.assertEqual(len(fn_tokens), 1)
        self.assertIn("<a", fn_tokens[0]["content"])


if __name__ == "__main__":
    unittest.main()
