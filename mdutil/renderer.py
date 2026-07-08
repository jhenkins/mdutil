"""ANSI renderer for parsed Markdown tokens."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .syntax_highlighter import highlight_code
from .themes import DEFAULT_THEME, load_theme

RESET = "\033[0m"
BOLD = "\033[1m"


def render(
    parsed_content: list[dict[str, Any]],
    theme: str = DEFAULT_THEME,
    theme_file: str | None = None,
    syntax_theme: str = "default",
    line_numbers: bool = False,
    quiet: bool = False,
) -> str:
    """Render parsed Markdown content into an ANSI/plain terminal string."""
    if quiet:
        return ""

    selected_theme = load_theme(theme, theme_file)
    result_lines: list[str] = []

    for token in parsed_content:
        result_lines.extend(_render_token(token, selected_theme, syntax_theme))

    if line_numbers:
        return "\n".join(f"{idx:4d} | {line}" for idx, line in enumerate(result_lines, 1))
    return "\n".join(result_lines)


def _render_token(
    token: dict[str, Any],
    theme: dict[str, Any],
    syntax_theme: str = "default",
) -> list[str]:
    ttype = token.get("type")
    if ttype == "heading":
        return [_render_heading(token, theme)]
    if ttype == "paragraph":
        return [_render_paragraph(token, theme)]
    if ttype == "blank":
        return [""]
    if ttype == "code":
        return _render_code(token, theme, syntax_theme)
    if ttype == "list":
        return _render_list(token)
    if ttype == "blockquote":
        return _render_blockquote(token, theme)
    if ttype == "table":
        return _render_table(token)
    if ttype == "horizontal_rule":
        return [_style(str(token.get("content", token.get("text", ""))), theme, "hr")]
    return str(token.get("content", "")).split("\n")


def _render_heading(token: dict[str, Any], theme: dict[str, Any]) -> str:
    level = int(token.get("level", 1))
    content = str(token.get("content") or _heading_content_from_text(token, level))
    return _style(content, theme, f"h{level}", bold=True)


def _heading_content_from_text(token: dict[str, Any], level: int) -> str:
    text = str(token.get("text", ""))
    return f"{'#' * level} {text}" if text else "#" * level


def _render_paragraph(token: dict[str, Any], theme: dict[str, Any] | None = None) -> str:
    return _strip_inline_tags(str(token.get("content", token.get("text", ""))), theme)


def _render_code(token: dict[str, Any], theme: dict[str, Any], syntax_theme: str = "default") -> list[str]:
    code = str(token.get("content", ""))
    language = str(token.get("language") or "")
    return highlight_code(code, language, theme, syntax_theme=syntax_theme).split("\n")


def _render_list(token: dict[str, Any]) -> list[str]:
    content = token.get("content") or token.get("text")
    if content:
        return str(content).split("\n")

    items = [str(item) for item in token.get("items", [])]
    if token.get("ordered"):
        return [f"{idx}. {item}" for idx, item in enumerate(items, 1)]
    return [f"- {item}" for item in items]


def _render_blockquote(token: dict[str, Any], theme: dict[str, Any]) -> list[str]:
    content = str(token.get("content", token.get("text", "")))
    rendered: list[str] = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
        rendered.append(_style(f"│ {stripped}", theme, "blockquote"))
    return rendered


def _render_table(token: dict[str, Any]) -> list[str]:
    headers = token.get("headers")
    rows = token.get("rows")
    if headers is None or rows is None:
        return str(token.get("content", token.get("text", ""))).split("\n")

    table_rows = [[str(cell) for cell in headers]] + [
        [str(cell) for cell in row] for row in rows
    ]
    if not table_rows or not table_rows[0]:
        return []

    column_count = len(table_rows[0])
    widths = [0] * column_count
    for row in table_rows:
        for idx in range(column_count):
            cell = row[idx] if idx < len(row) else ""
            widths[idx] = max(widths[idx], _display_width(cell))

    alignments: list[str | None] = list(token.get("alignments") or [None] * column_count)
    rendered = [_format_table_row(table_rows[0], widths, alignments)]
    rendered.append(" | ".join("-" * width for width in widths))
    for row in table_rows[1:]:
        rendered.append(_format_table_row(row, widths, alignments))
    return rendered


def _format_table_row(row: list[str], widths: list[int], alignments: list[str | None]) -> str:
    cells: list[str] = []
    for idx, width in enumerate(widths):
        cell = row[idx] if idx < len(row) else ""
        alignment = alignments[idx] if idx < len(alignments) else None
        if alignment == "right":
            cells.append(_rjust_display(cell, width))
        elif alignment == "center":
            cells.append(_center_display(cell, width))
        else:
            cells.append(_ljust_display(cell, width))
    return " | ".join(cells)


def _ljust_display(text: str, width: int) -> str:
    return text + " " * max(0, width - _display_width(text))


def _rjust_display(text: str, width: int) -> str:
    return " " * max(0, width - _display_width(text)) + text


def _center_display(text: str, width: int) -> str:
    padding = max(0, width - _display_width(text))
    left = padding // 2
    right = padding - left
    return " " * left + text + " " * right


def _display_width(text: str) -> int:
    """Return terminal display width, ignoring ANSI codes and combining marks."""
    visible = re.sub(r"\033\[[0-9;]*m", "", text)
    width = 0
    for char in visible:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


def _style(text: str, theme: dict[str, Any], markdown_key: str, *, bold: bool = False) -> str:
    codes: list[str] = []
    color = theme.get("markdown", {}).get(markdown_key)
    color_code = _ansi_color(color)
    if color_code:
        codes.append(color_code)
    if bold:
        codes.append(BOLD)
    if not codes:
        return text
    return "".join(codes) + text + RESET


def _ansi_color(color: Any) -> str:
    if not isinstance(color, str):
        return ""
    match = re.fullmatch(r"#([0-9a-fA-F]{6})", color.strip())
    if not match:
        return ""
    hex_value = match.group(1)
    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)
    return f"\033[38;2;{red};{green};{blue}m"


def _strip_inline_tags(text: str, theme: dict[str, Any] | None = None) -> str:
    """Collapse the parser's lightweight HTML-like inline markup to visible text."""
    def render_link(match: re.Match[str]) -> str:
        label = re.sub(r"</?(?:strong|em|code)>", "", match.group(2))
        return _style(f"{label} ({match.group(1)})", theme or {}, "link")

    text = re.sub(
        r"<a\s+href=\"([^\"]+)\">(.*?)</a>",
        render_link,
        text,
    )
    text = re.sub(r"</?(?:strong|em|code)>", "", text)
    return text
