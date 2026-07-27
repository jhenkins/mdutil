"""HTML exporter for mdutil v3.0."""

from __future__ import annotations

from typing import Any

from mdutil.export.base import Exporter


class HtmlExporter(Exporter):
    """Export Markdown to HTML with embedded CSS."""

    DEFAULT_FONT_SIZE = 16  # 1em
    DEFAULT_LINE_HEIGHT = 1.6
    CODE_FONT_SIZE = 14  # 0.875em
    MARGIN = 40  # px

    # Color palette
    TEXT_COLOR = "#24292e"
    LINK_COLOR = "#0366d6"
    CODE_BG = "#f6f8fa"
    BORDER_COLOR = "#e1e4e8"
    BLOCKQUOTE_COLOR = "#6a737d"
    TABLE_HEADER_BG = "#f6f8fa"
    TABLE_BORDER_COLOR = "#dfe2e5"

    def supports(self, format: str) -> bool:
        return format.lower() == "html"

    def render(self, tokens: list[dict], theme: dict, options: dict) -> str:
        """Render tokens to HTML."""
        css = self._generate_css(theme)
        custom_css = options.get("custom_css", "")
        body = self._render_tokens(tokens)
        style_block = f"{css}"
        if custom_css:
            style_block += f"\n/* Custom CSS */\n{custom_css}\n"
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>mdutil export</title>
    <style>
{style_block}
    </style>
</head>
<body>
{body}
</body>
</html>"""

    def _generate_css(self, theme: dict) -> str:
        """Generate CSS from theme."""
        # Use theme colors if available, otherwise use defaults
        text_color = theme.get("text", self.TEXT_COLOR)
        link_color = theme.get("link", self.LINK_COLOR)
        code_bg = theme.get("code_bg", self.CODE_BG)
        border_color = theme.get("border", self.BORDER_COLOR)
        blockquote_color = theme.get("blockquote", self.BLOCKQUOTE_COLOR)
        table_header_bg = theme.get("table_header_bg", self.TABLE_HEADER_BG)
        table_border = theme.get("table_border", self.TABLE_BORDER_COLOR)

        return f"""
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: {self.DEFAULT_FONT_SIZE}px;
    line-height: {self.DEFAULT_LINE_HEIGHT};
    color: {text_color};
    max-width: 960px;
    margin: 0 auto;
    padding: {self.MARGIN}px 20px;
}}

h1, h2, h3, h4, h5, h6 {{
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}}

h1 {{ font-size: 2em; border-bottom: 1px solid {table_border}; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid {table_border}; padding-bottom: 0.3em; }}
h3 {{ font-size: 1.25em; }}
h4 {{ font-size: 1em; }}
h5 {{ font-size: 0.875em; }}
h6 {{ font-size: 0.85em; color: {blockquote_color}; }}

p {{
    margin: 0 0 16px 0;
}}

a {{
    color: {link_color};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: {self.CODE_FONT_SIZE}px;
    background-color: {code_bg};
    border-radius: 3px;
    padding: 0.2em 0.4em;
}}

pre {{
    padding: 16px;
    overflow: auto;
    font-size: {self.CODE_FONT_SIZE}px;
    line-height: 1.45;
    background-color: {code_bg};
    border-radius: 3px;
}}

pre code {{
    background-color: transparent;
    padding: 0;
    font-size: 100%;
}}

blockquote {{
    padding: 0 1em;
    color: {blockquote_color};
    border-left: 0.25em solid {table_border};
    margin: 0 0 16px 0;
}}

hr {{
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: {table_border};
    border: 0;
}}

table {{
    border-spacing: 0;
    border-collapse: collapse;
    margin: 0 0 16px 0;
    width: auto;
    max-width: 100%;
    overflow: auto;
    display: block;
}}

th {{
    font-weight: 600;
    padding: 6px 13px;
    border: 1px solid {table_border};
    background-color: {table_header_bg};
}}

td {{
    padding: 6px 13px;
    border: 1px solid {table_border};
}}

tr:nth-child(2n) {{
    background-color: {code_bg};
}}

ul, ol {{
    padding-left: 2em;
    margin: 0 0 16px 0;
}}

li + li {{
    margin-top: 0.25em;
}}

li > ul, li > ol {{
    margin-top: 0.25em;
}}

img {{
    max-width: 100%;
    box-sizing: border-box;
}}
"""

    def _render_tokens(self, tokens: list[dict]) -> str:
        """Render a list of tokens to HTML."""
        output = []
        for token in tokens:
            token_type = token.get("type")

            if token_type == "blank":
                output.append("")
                continue

            if token_type == "heading":
                output.append(self._render_heading(token))
                continue

            if token_type == "paragraph":
                output.append(self._render_paragraph(token))
                continue

            if token_type == "code":
                output.append(self._render_code_block(token))
                continue

            if token_type == "horizontal_rule":
                output.append("<hr>")
                continue

            if token_type == "table":
                output.append(self._render_table(token))
                continue

            if token_type == "blockquote":
                output.append(self._render_blockquote(token))
                continue

            if token_type == "list":
                output.append(self._render_list(token))
                continue

        return "\n".join(output)

    def _render_heading(self, token: dict) -> str:
        """Render a heading."""
        level = token.get("level", 1)
        text = token.get("text", "")
        return f"<h{level}>{text}</h{level}>"

    def _render_paragraph(self, token: dict) -> str:
        """Render a paragraph."""
        spans = token.get("spans", [])
        if spans:
            text = self._render_spans(spans)
        else:
            text = token.get("text", "")
        return f"<p>{text}</p>"

    def _render_spans(self, spans: list[dict]) -> str:
        """Render inline spans with formatting."""
        output = []
        for span in spans:
            span_type = span.get("type", "text")
            content = span.get("content", "")

            if span_type == "text":
                output.append(content)
            elif span_type == "bold":
                output.append(f"<strong>{content}</strong>")
            elif span_type == "italic":
                output.append(f"<em>{content}</em>")
            elif span_type == "code":
                output.append(f"<code>{content}</code>")
            elif span_type == "link":
                href = span.get("href", "#")
                output.append(f'<a href="{href}">{content}</a>')
            else:
                output.append(content)

        return "".join(output)

    def _render_code_block(self, token: dict) -> str:
        """Render a code block."""
        content = token.get("content", "")
        language = token.get("language", "")

        # Escape HTML entities
        content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if language:
            return f'<pre><code class="language-{language}">{content}</code></pre>'
        return f"<pre><code>{content}</code></pre>"

    def _render_table(self, token: dict) -> str:
        """Render a table."""
        headers = token.get("headers", [])
        rows = token.get("rows", [])
        alignments = token.get("alignments", [])

        if not headers:
            return ""

        # Build header row
        header_cells = []
        for i, header in enumerate(headers):
            align = alignments[i] if i < len(alignments) else "left"
            header_cells.append(f"<th style=\"text-align: {align}\">{header}</th>")
        header_row = "<tr>" + "".join(header_cells) + "</tr>"

        # Build body rows
        body_rows = []
        for row in rows:
            cells = []
            for i, cell in enumerate(row):
                align = alignments[i] if i < len(alignments) else "left"
                cells.append(f"<td style=\"text-align: {align}\">{cell}</td>")
            body_rows.append("<tr>" + "".join(cells) + "</tr>")

        body = "<tbody>" + "".join(body_rows) + "</tbody>"

        return f"<table>\n<thead>{header_row}</thead>\n{body}\n</table>"

    def _render_blockquote(self, token: dict) -> str:
        """Render a blockquote."""
        content = token.get("content", "")
        # Remove leading > from each line
        lines = content.split("\n")
        cleaned_lines = [line.lstrip(">").strip() for line in lines]
        text = "\n".join(cleaned_lines)
        return f"<blockquote>\n{text}\n</blockquote>"

    def _render_list(self, token: dict) -> str:
        """Render an ordered or unordered list."""
        items = token.get("items", [])
        ordered = token.get("ordered", False)
        list_type = "ol" if ordered else "ul"

        list_items = []
        for item in items:
            list_items.append(f"<li>{item}</li>")

        return f"<{list_type}>\n" + "\n".join(list_items) + f"\n</{list_type}>"
