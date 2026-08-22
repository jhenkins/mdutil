"""Tests for link title attribute parsing (KB-071).

GFM allows `[text](url "title")` syntax with optional title attribute.
"""

import unittest

from mdutil.parser import parse_markdown, _parse_inline, _parse_link_attributes, _visible_inline_text


class LinkTitleParserTests(unittest.TestCase):
    """Parser tests for link title attribute."""

    def test_basic_link_without_title(self):
        """Basic link without title works as before."""
        tokens = parse_markdown("[click](https://example.com)")

        self.assertEqual(tokens[0]["type"], "paragraph")
        self.assertIn('<a href="https://example.com">click</a>', tokens[0]["content"])
        link_span = [s for s in tokens[0]["spans"] if s["type"] == "link"][0]
        self.assertEqual(link_span["href"], "https://example.com")
        self.assertNotIn("title", link_span)

    def test_link_with_double_quoted_title(self):
        """Link with double-quoted title is parsed correctly."""
        result = _parse_inline('[click](https://example.com "Example Site")')

        self.assertIn('<a href="https://example.com" title="Example Site">', result["content"])
        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        self.assertEqual(link_span["href"], "https://example.com")
        self.assertEqual(link_span["title"], "Example Site")

    def test_link_with_single_quoted_title(self):
        """Link with single-quoted title is parsed correctly."""
        result = _parse_inline("[click](https://example.com 'Example Site')")

        self.assertIn('<a href="https://example.com" title="Example Site">', result["content"])
        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        self.assertEqual(link_span["title"], "Example Site")

    def test_link_with_special_characters_in_title(self):
        """Link title with special characters is preserved (HTML-escaped in output)."""
        result = _parse_inline('[click](https://example.com "Click & Go v2")')

        # HTML output escapes & to &amp;
        self.assertIn('title="Click &amp; Go v2"', result["content"])
        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        # Raw title is preserved unescaped in the span
        self.assertEqual(link_span["title"], "Click & Go v2")

    def test_link_with_spaces_in_title(self):
        """Link title with spaces is preserved."""
        result = _parse_inline('[click](https://example.com "Click me now please")')

        self.assertIn('title="Click me now please"', result["content"])
        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        self.assertEqual(link_span["title"], "Click me now please")

    def test_link_with_empty_title(self):
        """Link with empty title attribute is treated as no title."""
        result = _parse_inline('[click](https://example.com "")')

        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        # Empty title — the title is present but empty
        self.assertIn('title=""', result["content"])
        self.assertEqual(link_span["title"], "")

    def test_link_without_title_no_regression(self):
        """Links without title still work without title key in span."""
        result = _parse_inline("[click](https://example.com)")

        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        self.assertNotIn("title", link_span)

    def test_autolink_unchanged(self):
        """Autolinks do not gain a title attribute (they have no title syntax)."""
        result = _parse_inline("<https://example.com>")

        link_span = [s for s in result["spans"] if s["type"] == "link"][0]
        self.assertEqual(link_span["href"], "https://example.com")
        self.assertNotIn("title", link_span)

    def test_multiple_links_in_one_line(self):
        """Multiple links, some with titles, are all parsed correctly."""
        result = _parse_inline(
            '[one](/a "First") and [two](/b "Second") and [three](/c)'
        )

        link_spans = [s for s in result["spans"] if s["type"] == "link"]
        self.assertEqual(len(link_spans), 3)
        self.assertEqual(link_spans[0]["href"], "/a")
        self.assertEqual(link_spans[0]["title"], "First")
        self.assertEqual(link_spans[1]["href"], "/b")
        self.assertEqual(link_spans[1]["title"], "Second")
        self.assertEqual(link_spans[2]["href"], "/c")
        self.assertNotIn("title", link_spans[2])

    def test_visible_inline_text_strips_title(self):
        """_visible_inline_text strips link title from HTML output."""
        result = _visible_inline_text('<a href="url" title="t">text</a>')
        self.assertEqual(result, "text")

    def test_link_title_with_nested_inline_formatting(self):
        """Link with title and nested formatting is parsed correctly."""
        result = _parse_inline('**[bold link](/url "title")**')

        self.assertIn("<strong>", result["content"])
        self.assertIn('<a href="/url" title="title">bold link</a>', result["content"])

    def test_full_paragraph_with_mixed_links(self):
        """Full paragraph with links that have and lack titles."""
        tokens = parse_markdown(
            'See [labeled](/url "Label") and [plain](/other).'
        )

        self.assertEqual(tokens[0]["type"], "paragraph")
        link_spans = [s for s in tokens[0]["spans"] if s["type"] == "link"]
        self.assertEqual(len(link_spans), 2)
        self.assertEqual(link_spans[0]["title"], "Label")
        self.assertNotIn("title", link_spans[1])


class LinkTitleAttributeHelperTests(unittest.TestCase):
    """Tests for _parse_link_attributes helper."""

    def test_no_title(self):
        href, title = _parse_link_attributes("https://example.com")
        self.assertEqual(href, "https://example.com")
        self.assertIsNone(title)

    def test_double_quoted_title(self):
        href, title = _parse_link_attributes('https://example.com "Example"')
        self.assertEqual(href, "https://example.com")
        self.assertEqual(title, "Example")

    def test_single_quoted_title(self):
        href, title = _parse_link_attributes("https://example.com 'Example'")
        self.assertEqual(href, "https://example.com")
        self.assertEqual(title, "Example")

    def test_empty_title(self):
        href, title = _parse_link_attributes('https://example.com ""')
        self.assertEqual(href, "https://example.com")
        self.assertEqual(title, "")

    def test_title_with_surrounding_spaces(self):
        href, title = _parse_link_attributes('https://example.com  "My Title"')
        self.assertEqual(href, "https://example.com")
        self.assertEqual(title, "My Title")

    def test_url_with_query_params(self):
        href, title = _parse_link_attributes('https://example.com?q=1 "Search"')
        self.assertEqual(href, "https://example.com?q=1")
        self.assertEqual(title, "Search")

    def test_relative_url_with_title(self):
        href, title = _parse_link_attributes('/page "Page Title"')
        self.assertEqual(href, "/page")
        self.assertEqual(title, "Page Title")

    def test_whitespace_before_title_only(self):
        href, title = _parse_link_attributes('https://example.com  "Title"')
        self.assertEqual(href, "https://example.com")
        self.assertEqual(title, "Title")


if __name__ == "__main__":
    unittest.main()
