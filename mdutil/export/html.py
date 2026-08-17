"""HTML exporter for mdutil v3.0."""

from __future__ import annotations

import logging
import re
from typing import Any

from mdutil.export.base import Exporter
from mdutil.export.merman_renderer import MermanRenderer, MermanBinaryNotFoundError, MermanRenderError
from mdutil.parser import _parse_inline

_logger = logging.getLogger("mdutil.export.html")


class HtmlExporter(Exporter):
    """Export Markdown to HTML with embedded CSS."""

    _DOCUMENT_HEADER_LINE_RE = re.compile(
        r"^\*\*(?:author|version|last[-‑]updated|license|repository):\*\*\s+",
        re.IGNORECASE,
    )

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
        self._options = options
        css = self._generate_css(theme)
        custom_css = options.get("custom_css", "")
        syntax_theme = options.get("syntax_theme", "default")
        
        # Inject Pygments syntax theme CSS for highlighted code blocks
        try:
            from pygments.formatters import HtmlFormatter
            from pygments.styles import get_style_by_name
            style_defs = HtmlFormatter(style=get_style_by_name(syntax_theme)).get_style_defs(".mdutil-highlight")
            if style_defs.strip():
                css = f"{css}\n{style_defs}"
        except Exception:
            # If style can't be loaded, proceed without syntax CSS
            pass
        
        body = self._render_tokens(tokens, syntax_theme=syntax_theme)
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

.mermaid {{
    text-align: center;
    margin: 16px 0;
}}

.mermaid svg {{
    max-width: 100%;
    height: auto;
}}
"""

    def _render_tokens(self, tokens: list[dict], syntax_theme: str = "default") -> str:
        """Render a list of tokens to HTML."""
        # Collect mermaid diagrams and render them upfront (batched).
        mermaid_diagrams: list[tuple[dict, int]] = []
        for i, token in enumerate(tokens):
            if token.get("type") == "mermaid":
                mermaid_diagrams.append((token, i))

        rendered_svgs = {}
        if mermaid_diagrams:
            mermaid_enabled = self._options.get("mermaid", True)
            if mermaid_enabled:
                rendered_svgs = self._render_mermaid_batch(mermaid_diagrams)
            else:
                # mermaid disabled: treat mermaid tokens as plain code blocks
                pass

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
                output.append(self._render_code_block(token, syntax_theme))
                continue

            if token_type == "mermaid":
                output.append(self._render_mermaid(token, rendered_svgs))
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
        """Render a heading with inline formatting."""
        level = token.get("level", 1)
        text = token.get("text", "")
        inline = _parse_inline(text)
        content = inline["content"]
        return f"<h{level}>{content}</h{level}>"

    def _render_paragraph(self, token: dict) -> str:
        """Render a paragraph.

        The parser's ``content`` field already contains HTML inline tags
        (<strong>, <em>, <code>, <a>) — use it directly so that bold,
        italic, code, and links render correctly in the browser.
        """
        if self._is_document_header_metadata(token):
            return "<p>" + "<br>\n".join(token["content_lines"]) + "</p>"

        content = token.get("content", "")
        if content:
            return f"<p>{content}</p>"
        # Fallback for tokens without inline-parsed content
        spans = token.get("spans", [])
        if spans:
            text = self._render_spans(spans)
        else:
            text = token.get("text", "")
        return f"<p>{text}</p>"

    def _is_document_header_metadata(self, token: dict) -> bool:
        """Return True when a paragraph is the spec-style document metadata header."""
        source_lines = token.get("source_lines", [])
        content_lines = token.get("content_lines", [])
        if len(source_lines) < 2 or len(source_lines) != len(content_lines):
            return False
        return all(
            isinstance(line, str) and self._DOCUMENT_HEADER_LINE_RE.match(line)
            for line in source_lines
        )

    def _render_spans(self, spans: list[dict]) -> str:
        """Render inline spans with formatting."""
        output = []
        for span in spans:
            span_type = span.get("type", "text")
            content = span.get("content", span.get("text", ""))

            if span_type == "text":
                output.append(content)
            elif span_type in ("bold", "strong"):
                output.append(f"<strong>{content}</strong>")
            elif span_type in ("italic", "emphasis"):
                output.append(f"<em>{content}</em>")
            elif span_type in ("code", "inline_code"):
                output.append(f"<code>{content}</code>")
            elif span_type == "link":
                href = span.get("href", "#")
                output.append(f'<a href="{href}">{content}</a>')
            else:
                output.append(content)

        return "".join(output)

    def _render_mermaid(self, token: dict, rendered_svgs: dict) -> str:
        """Render a mermaid token to HTML.

        Uses pre-rendered SVG if available; falls back to a fenced code block
        when rendering failed or the binary is unavailable.
        """
        mermaid_enabled = self._options.get("mermaid", True)
        if not mermaid_enabled:
            return self._render_code_block(token, syntax_theme="")

        content = token.get("content", "")
        # Try to get pre-rendered SVG from batch render.
        svg = rendered_svgs.get(id(token))
        if svg and not svg.startswith("<!--"):
            return f'<div class="mermaid">\n{svg}\n</div>'

        # Fallback: render as a code block with an error note.
        if svg and svg.startswith("<!--"):
            return f'<div class="mermaid">\n<p><em>Diagram could not be rendered:</em></p>\n<pre><code>{self._escape_html(content)}</code></pre>\n</div>'

        # No SVG rendered at all (binary unavailable or disabled) — emit code block.
        return self._render_code_block(token, syntax_theme="")

    def _render_mermaid_batch(self, diagrams: list[tuple[dict, int]]) -> dict:
        """Render multiple mermaid diagrams and return a dict mapping token id → SVG."""
        renderer = MermanRenderer()
        if not renderer.available:
            return {}

        theme = self._options.get("mermaid_theme", "default")
        code_index_pairs = [(d.get("content", ""), i) for i, (d, _) in enumerate(diagrams)]
        results = renderer.render_diagrams(code_index_pairs, theme=theme)

        rendered = {}
        for code, idx, svg in results:
            token = diagrams[idx][0]
            rendered[id(token)] = svg
        return rendered

    def _escape_html(self, text: str) -> str:
        """Escape HTML entities in text."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _render_code_block(self, token: dict, syntax_theme: str = "default") -> str:
        """Render a code block with syntax highlighting."""
        content = token.get("content", "")
        language = token.get("language", "")

        # Escape HTML entities for non-highlighted content
        escaped_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if language:
            # Use Pygments for highlighted code
            from mdutil.syntax_highlighter import highlight_code_html
            highlighted = highlight_code_html(content, language, syntax_theme)
            
            # Strip the outer <div class="highlight"> wrapper from Pygments output
            # Pygments returns: <div class="highlight"><pre>...</pre></div>
            # We want just the content between <pre> and </pre>
            import re
            match = re.search(r'<div class="highlight">.*?<pre>(.*?)</pre></div>', highlighted, re.DOTALL)
            if match:
                inner_content = match.group(1)
                return f'<pre class="mdutil-highlight"><code class="language-{language}">{inner_content}</code></pre>'
            else:
                # Fallback: use escaped content
                return f"<pre><code class=\"language-{language}\">{escaped_content}</code></pre>"
        else:
            # No language, use escaped content
            return f"<pre><code>{escaped_content}</code></pre>"

    def _render_table(self, token: dict) -> str:
        """Render a table."""
        headers = token.get("headers", [])
        rows = token.get("rows", [])
        alignments = token.get("alignments", [])

        if not headers:
            return ""

        # Helper to parse inline formatting in a cell.
        def cell_html(text: str) -> str:
            if isinstance(text, str):
                inline = _parse_inline(text)
                return inline["content"]
            return str(text)

        def cell_align(i: int) -> str:
            if i < len(alignments) and alignments[i]:
                return alignments[i]
            return "left"

        # Build header row
        header_cells = []
        for i, header in enumerate(headers):
            align = cell_align(i)
            header_cells.append(f"<th style=\"text-align: {align}\">{cell_html(header)}</th>")
        header_row = "<tr>" + "".join(header_cells) + "</tr>"

        # Build body rows
        body_rows = []
        for row in rows:
            cells = []
            for i, cell in enumerate(row):
                align = cell_align(i)
                cells.append(f"<td style=\"text-align: {align}\">{cell_html(cell)}</td>")
            body_rows.append("<tr>" + "".join(cells) + "</tr>")

        body = "<tbody>" + "".join(body_rows) + "</tbody>"

        return f"<table>\n<thead>{header_row}</thead>\n{body}\n</table>"

    def _render_blockquote(self, token: dict) -> str:
        """Render a blockquote.

        Strips leading ``>`` markers, parses inline formatting, and
        renders nested lists as proper HTML.
        """
        content = token.get("content", "")
        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.lstrip(">").strip()
            cleaned_lines.append(stripped)
        raw_text = "\n".join(cleaned_lines)

        # Re-parse the blockquote content so inline formatting and nested
        # lists are rendered correctly.
        from mdutil.parser import parse_markdown
        sub_tokens = parse_markdown(raw_text)
        inner_html = self._render_tokens(sub_tokens)
        return f"<blockquote>\n{inner_html}\n</blockquote>"

    def _render_list(self, token: dict) -> str:
        """Render an ordered or unordered list."""
        parsed_items = token.get("parsed_items", [])
        ordered = token.get("ordered", False)
        list_type = "ol" if ordered else "ul"

        list_items = []
        if parsed_items:
            for item in parsed_items:
                content = item.get("content", item.get("text", ""))
                list_items.append(f"<li>{content}</li>")
        else:
            # Fallback for tokens without parsed_items (tests, legacy)
            items = token.get("items", [])
            for item in items:
                if isinstance(item, dict):
                    content = item.get("content", item.get("text", ""))
                else:
                    content = str(item)
                list_items.append(f"<li>{content}</li>")

        return f"<{list_type}>\n" + "\n".join(list_items) + f"\n</{list_type}>"
