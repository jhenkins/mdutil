"""ANSI renderer for parsed Markdown tokens."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .syntax_highlighter import highlight_code
from .themes import DEFAULT_THEME, load_theme

RESET = "\033[0m"
BOLD = "\033[1m"
REVERSE = "\033[7m"


def render(
    parsed_content: list[dict[str, Any]],
    theme: str = DEFAULT_THEME,
    theme_file: str | None = None,
    syntax_theme: str = "default",
    line_numbers: bool = False,
    quiet: bool = False,
    math_fallback: bool = False,
    footnote_style: str = "numbered",
) -> str:
    """Render parsed Markdown content into an ANSI/plain terminal string."""
    if quiet:
        return ""

    selected_theme = load_theme(theme, theme_file)
    result_lines: list[str] = []

    for token in parsed_content:
        result_lines.extend(_render_token(
            token, selected_theme, syntax_theme,
            math_fallback=math_fallback,
            footnote_style=footnote_style,
        ))

    if line_numbers:
        return "\n".join(f"{idx:4d} | {line}" for idx, line in enumerate(result_lines, 1))
    return "\n".join(result_lines)


def _render_token(
    token: dict[str, Any],
    theme: dict[str, Any],
    syntax_theme: str = "default",
    *,
    math_fallback: bool = False,
    footnote_style: str = "numbered",
) -> list[str]:
    ttype = token.get("type")
    if ttype == "heading":
        return [_render_heading(token, theme)]
    if ttype == "paragraph":
        return [_render_paragraph(token, theme, math_fallback=math_fallback, footnote_style=footnote_style)]
    if ttype == "blank":
        return [""]
    if ttype == "code":
        return _render_code(token, theme, syntax_theme)
    if ttype == "list":
        return _render_list(token, theme)
    if ttype == "blockquote":
        return _render_blockquote(token, theme)
    if ttype == "table":
        return _render_table(token)
    if ttype == "horizontal_rule":
        return [_style(str(token.get("content", token.get("text", ""))), theme, "hr")]
    if ttype == "footnote_definition":
        return _render_footnote_definition(token, theme)
    if ttype == "definition":
        return _render_definition(token, theme)
    return str(token.get("content", "")).split("\n")


def _render_footnote_definition(token: dict[str, Any], theme: dict[str, Any]) -> list[str]:
    """Render a footnote definition token as indented text."""
    fn_id = token.get("id", "")
    content = token.get("content", "")
    # Strip inline tags for terminal display
    text = _strip_inline_tags(content, theme)
    # Format as "  ¹  Footnote text..." with indentation
    superscript = _superscript(fn_id)
    rendered = f"    {superscript}  {text}"
    return [rendered]


def _render_definition(token: dict[str, Any], theme: dict[str, Any]) -> list[str]:
    """Render a definition list token.

    Terminal display::

        Term  —
            Definition text

    Multiple terms are joined with " / ". First definition appears under term;
    additional definitions are indented.
    """
    term_text = token.get("term_text", "")
    definitions = token.get("definitions", [])

    lines: list[str] = []
    styled_term = _style(term_text, theme, "definition_term", bold=True)
    lines.append(styled_term + " —")

    for defn in definitions:
        # Strip inline tags for terminal display
        plain_defn = _strip_inline_tags(defn, theme)
        lines.append("    " + _style(plain_defn, theme, "definition_definition"))

    return lines


def _render_heading(token: dict[str, Any], theme: dict[str, Any]) -> str:
    level = int(token.get("level", 1))
    content = str(token.get("content") or _heading_content_from_text(token, level))
    return _style(content, theme, f"h{level}", bold=True)


def _heading_content_from_text(token: dict[str, Any], level: int) -> str:
    text = str(token.get("text", ""))
    return f"{'#' * level} {text}" if text else "#" * level


def _render_paragraph(
    token: dict[str, Any],
    theme: dict[str, Any] | None = None,
    *,
    math_fallback: bool = False,
    footnote_style: str = "numbered",
) -> str:
    content = str(token.get("content", token.get("text", "")))
    return _strip_inline_tags(content, theme, math_fallback=math_fallback, footnote_style=footnote_style)


def _render_code(token: dict[str, Any], theme: dict[str, Any], syntax_theme: str = "default") -> list[str]:
    code = str(token.get("content", ""))
    language = str(token.get("language") or "")
    return highlight_code(code, language, theme, syntax_theme=syntax_theme).split("\n")


def _render_list(token: dict[str, Any], theme: dict[str, Any], indent_level: int = 0) -> list[str]:
    """Render a list token, recursively handling nested sub-lists.

    Args:
        token: Parsed list token with ``parsed_items``.
        indent_level: Current nesting depth (each level adds 2 spaces).
    """
    parsed_items = token.get("parsed_items", [])
    is_task_list = token.get("task", False)
    ordered = token.get("ordered", False)
    indent = "  " * indent_level

    result: list[str] = []
    if parsed_items:
        for idx, item in enumerate(parsed_items):
            text = str(item.get("text", ""))

            # Task item with checkbox
            if is_task_list and item.get("task") and item.get("checked") is not None:
                prefix = "☑" if item["checked"] else "☐"
                prefix_key = "task_list_checked" if item["checked"] else "task_list_unchecked"
                prefix = _style(prefix, theme, prefix_key)
                line = f"{indent}{prefix} {text}"
            elif is_task_list and item.get("task"):
                # Task item without resolved checkbox
                if ordered:
                    line = f"{indent}{idx + 1}. {text}"
                else:
                    line = f"{indent}- {text}"
            elif ordered:
                line = f"{indent}{idx + 1}. {text}"
            else:
                line = f"{indent}- {text}"

            result.append(line)

            # Recurse into sub-list if present
            sub = item.get("sub_list")
            if sub:
                result.extend(_render_list(sub, theme, indent_level + 1))
    else:
        # Legacy path: plain ``items`` list
        items = [str(item) for item in token.get("items", [])]
        for idx, item in enumerate(items, 1):
            if ordered:
                line = f"{indent}{idx}. {item}"
            else:
                line = f"{indent}- {item}"
            result.append(line)
    return result


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


def _highlight_text(text: str, theme: dict[str, Any]) -> str:
    """Apply ANSI highlight (background color) to text using theme's highlight color."""
    color = theme.get("markdown", {}).get("highlight")
    if not color:
        return text
    # Use background color (48;2;R;G;B) for highlight effect
    match = re.fullmatch(r"#([0-9a-fA-F]{6})", color.strip())
    if not match:
        return text
    hex_value = match.group(1)
    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)
    return f"\033[48;2;{red};{green};{blue}m{text}\033[0m"


def _strip_inline_tags(
    text: str,
    theme: dict[str, Any] | None = None,
    *,
    math_fallback: bool = False,
    footnote_style: str = "numbered",
) -> str:
    """Collapse the parser's lightweight HTML-like inline markup to visible text.

    Args:
        text: Inline HTML-like markup from the parser.
        theme: Theme dict for color application.
        math_fallback: When True, preserve ``$...$`` delimiters around math content.
        footnote_style: ``"numbered"`` for superscript (default) or
            ``"bracketed"`` for ``[1]``-style references.
    """
    theme = theme or {}

    def render_link(match: re.Match[str]) -> str:
        label = re.sub(r"</?(?:strong|em|del|code|math|img)>", "", match.group(2))
        return _style(f"{label} ({match.group(1)})", theme, "link")

    text = re.sub(
        r"<a\s+href=\"([^\"]+)\">(.*?)</a>",
        render_link,
        text,
    )

    # Image: render as [image: alt text] or [image: url] if no alt
    text = re.sub(
        r'<img\s+src="([^"]+)"\s+alt="([^"]*)"[^>]*/?>',
        lambda m: _style(f"[image: {m.group(2) or m.group(1)}]", theme, "link"),
        text,
    )
    # Self-closing <img> without alt (fallback)
    text = re.sub(
        r'<img\s+src="([^"]+)"[^>]*/?>',
        lambda m: _style(f"[image: {m.group(1)}]", theme, "link"),
        text,
    )

    # Footnote references: superscript (default) or bracketed
    if footnote_style == "bracketed":
        text = re.sub(
            r"<fnref\s+id=\"(\d+)\">",
            lambda m: _style(f"[{m.group(1)}]", theme, "footnote_ref"),
            text,
        )
    else:
        text = re.sub(
            r"<fnref\s+id=\"(\d+)\">",
            lambda m: _style(_superscript(m.group(1)), theme, "footnote_ref"),
            text,
        )

    inner_re = r"</?(?:strong|em|del|code|math)>"
    text = re.sub(r"<sub>(.*?)</sub>", lambda m: _style(_subscript(re.sub(inner_re, "", m.group(1))), theme, "subscript"), text)
    text = re.sub(r"<sup>(.*?)</sup>", lambda m: _style(_superscript(re.sub(inner_re, "", m.group(1))), theme, "superscript"), text)
    text = re.sub(r"<mark>(.*?)</mark>", lambda m: _highlight_text(re.sub(inner_re, "", m.group(1)), theme), text)

    # Strikethrough
    text = re.sub(r"<del>(.*?)</del>", lambda m: _style(re.sub(inner_re, "", m.group(1)), theme, "strikethrough", bold=False), text)

    # Math: show raw $...$ delimiters when math_fallback is enabled
    if math_fallback:
        text = re.sub(r"<math>(.*?)</math>", lambda m: f"${m.group(1)}$", text)
    else:
        text = re.sub(r"<math>(.*?)</math>", lambda m: re.sub(inner_re, "", m.group(1)), text)

    text = re.sub(r"</?(?:strong|em|del|code|math|sub|sup|mark)>", "", text)
    return text


def _superscript(n: str) -> str:
    """Convert a string to Unicode superscript characters."""
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
        "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ",
        "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ",
        "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ",
        "p": "ᵖ", "q": "ʳ", "r": "ʳ", "s": "ˢ", "t": "ᵗ",
        "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
        "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ",
        "E": "ᴱ", "F": "ᶠ", "G": "ᴳ", "H": "ᴴ", "I": "ᴵ",
        "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ", "N": "ᴺ",
        "O": "ᴼ", "P": "ᴾ", "Q": "ᴽ", "R": "ᴿ", "S": "ˢ",
        "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ",
        "Y": "ʸ", "-": "⁻", "+": "⁺", "=": "⁼",
        "(": "⁽", ")": "⁾",
    }
    return "".join(superscript_map.get(c, c) for c in n)


def _subscript(n: str) -> str:
    """Convert a string to Unicode subscript characters."""
    subscript_map = {
        "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
        "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
        "a": "ₐ", "b": "b", "c": "c", "d": "d", "e": "ₑ",
        "f": "f", "g": "g", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
        "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
        "p": "ₚ", "q": "q", "r": "ᵣ", "s": "ₛ", "t": "ₜ",
        "u": "ᵤ", "v": "ᵥ", "w": "w", "x": "ₓ", "y": "y",
        "z": "z", "A": "A", "B": "B", "C": "C", "D": "D",
        "E": "E", "F": "F", "G": "G", "H": "H", "I": "I",
        "J": "J", "K": "K", "L": "L", "M": "M", "N": "N",
        "O": "O", "P": "P", "Q": "Q", "R": "R", "S": "S",
        "T": "T", "U": "U", "V": "V", "W": "W", "X": "X",
        "Y": "Y", "Z": "Z", "-": "₋", "+": "₊", "=": "₌",
        "(": "₍", ")": "₎",
    }
    return "".join(subscript_map.get(c, c) for c in n)
