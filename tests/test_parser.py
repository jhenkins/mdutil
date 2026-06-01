import unittest

from mdutil.parser import parse_markdown


class ParserTests(unittest.TestCase):
    def test_parse_atx_headings_with_levels_and_closing_markers(self):
        tokens = parse_markdown("# Title\n### Section ###\n   #### Indented")

        self.assertEqual(
            tokens,
            [
                {"type": "heading", "content": "# Title", "level": 1, "text": "Title"},
                {"type": "heading", "content": "### Section", "level": 3, "text": "Section"},
                {"type": "heading", "content": "#### Indented", "level": 4, "text": "Indented"},
            ],
        )

    def test_hashes_without_required_heading_shape_are_paragraphs(self):
        tokens = parse_markdown("#not a heading\n####### too many")

        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertEqual(tokens[0]["text"], "#not a heading")
        self.assertEqual(tokens[1]["type"], "paragraph")
        self.assertEqual(tokens[1]["text"], "####### too many")

    def test_blank_lines_are_blank_tokens(self):
        tokens = parse_markdown("# Title\n\nText\n")

        self.assertEqual(tokens[0]["type"], "heading")
        self.assertEqual(tokens[1], {"type": "blank", "content": "", "text": ""})
        self.assertEqual(tokens[2]["type"], "paragraph")
        self.assertEqual(tokens[3], {"type": "blank", "content": "", "text": ""})

    def test_parse_inline_spans_in_paragraphs(self):
        tokens = parse_markdown(
            "This is *em* and **strong** with `code` and [link](https://example.com)."
        )

        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertEqual(
            tokens[0]["content"],
            'This is <em>em</em> and <strong>strong</strong> with <code>code</code> and '
            '<a href="https://example.com">link</a>.',
        )
        self.assertEqual(
            tokens[0]["spans"],
            [
                {"type": "emphasis", "text": "em"},
                {"type": "strong", "text": "strong"},
                {"type": "inline_code", "text": "code"},
                {"type": "link", "text": "link", "href": "https://example.com"},
            ],
        )

    def test_parse_unordered_and_ordered_lists_separately(self):
        tokens = parse_markdown("- one\n* two\n\n1. first\n2. second")

        self.assertEqual(tokens[0]["type"], "list")
        self.assertEqual(tokens[0]["ordered"], False)
        self.assertEqual(tokens[0]["items"], ["one", "two"])
        self.assertEqual(tokens[0]["text"], "- one\n* two")
        self.assertEqual(tokens[2]["type"], "list")
        self.assertEqual(tokens[2]["ordered"], True)
        self.assertEqual(tokens[2]["items"], ["first", "second"])
        self.assertEqual(tokens[2]["text"], "1. first\n2. second")

    def test_ordered_and_unordered_lists_do_not_merge(self):
        tokens = parse_markdown("- bullet\n1. number")

        self.assertEqual([token["type"] for token in tokens], ["list", "list"])
        self.assertEqual(tokens[0]["ordered"], False)
        self.assertEqual(tokens[0]["items"], ["bullet"])
        self.assertEqual(tokens[1]["ordered"], True)
        self.assertEqual(tokens[1]["items"], ["number"])

    def test_parse_code_block_excludes_fences_and_preserves_inner_content(self):
        tokens = parse_markdown("```python\nprint(1)\n\nprint(2)\n```\nafter")

        self.assertEqual(
            tokens[0],
            {
                "type": "code",
                "content": "print(1)\n\nprint(2)",
                "language": "python",
                "text": "print(1)\n\nprint(2)",
            },
        )
        self.assertEqual(tokens[1]["type"], "paragraph")
        self.assertEqual(tokens[1]["text"], "after")

    def test_parse_tilde_code_block_and_info_string(self):
        tokens = parse_markdown("~~~ js linenums\nconst x = 1;\n~~~")

        self.assertEqual(tokens[0]["type"], "code")
        self.assertEqual(tokens[0]["language"], "js")
        self.assertEqual(tokens[0]["content"], "const x = 1;")

    def test_unclosed_code_fence_is_plain_paragraph_text(self):
        tokens = parse_markdown("```python\nprint(1)")

        self.assertEqual([token["type"] for token in tokens], ["paragraph", "paragraph"])
        self.assertEqual(tokens[0]["text"], "```python")
        self.assertEqual(tokens[1]["text"], "print(1)")

    def test_parse_tables_with_and_without_outer_pipes(self):
        tokens = parse_markdown("A | B\n:--- | ---:\n1 | 2\n3 | 4")

        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0]["type"], "table")
        self.assertEqual(tokens[0]["headers"], ["A", "B"])
        self.assertEqual(tokens[0]["alignments"], ["left", "right"])
        self.assertEqual(tokens[0]["rows"], [["1", "2"], ["3", "4"]])
        self.assertEqual(tokens[0]["text"], "A | B\n:--- | ---:\n1 | 2\n3 | 4")

    def test_separator_without_header_pipe_is_not_table(self):
        tokens = parse_markdown("No table\n---\ntext")

        self.assertEqual([token["type"] for token in tokens], ["paragraph", "horizontal_rule", "paragraph"])

    def test_parse_horizontal_rules(self):
        tokens = parse_markdown("---\n***\n___")

        self.assertEqual(tokens, [
            {"type": "horizontal_rule", "content": "---", "text": "---"},
            {"type": "horizontal_rule", "content": "***", "text": "***"},
            {"type": "horizontal_rule", "content": "___", "text": "___"},
        ])


if __name__ == "__main__":
    unittest.main()
