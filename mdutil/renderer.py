"""ANSI renderer for parsed Markdown tokens."""

from __future__ import annotations

import re
import shutil
import unicodedata
from typing import Any

from .syntax_highlighter import highlight_code
from .themes import DEFAULT_THEME, load_theme


def _get_terminal_width() -> int:
    """Return the current terminal width, defaulting to 80."""
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80

RESET = "\033[0m"
BOLD = "\033[1m"
REVERSE = "\033[7m"
STRIKETHROUGH = "\033[9m"
STRIKETHROUGH_OFF = "\033[29m"

# Default per-type colours for GFM callouts (admonitions). Unknown types fall
# back to the neutral ``blockquote`` colour.
_CALLOUT_DEFAULT_COLORS: dict[str, str] = {
    "NOTE": "#0088ff",
    "QUESTION": "#0088ff",
    "TIP": "#00cc00",
    "SUCCESS": "#00cc00",
    "INFO": "#0088ff",
    "IMPORTANT": "#aa00ff",
    "CAUTION": "#ff8800",
    "WARNING": "#ffcc00",
    "DANGER": "#ff0000",
}


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
        return _render_heading(token, theme)
    if ttype == "paragraph":
        return [_render_paragraph(token, theme, math_fallback=math_fallback, footnote_style=footnote_style)]
    if ttype == "blank":
        return [""]
    if ttype == "code":
        return _render_code(token, theme, syntax_theme)
    if ttype == "math_display":
        return _render_math_display(token, theme, syntax_theme)
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


def _render_heading(
    token: dict[str, Any], theme: dict[str, Any]
) -> list[str]:
    """Render a heading token with level-appropriate decoration.

    Visual hierarchy:
      h1: colour + bold + underline with ═ (double horizontal)
      h2: colour + bold + underline with ─ (single horizontal)
      h3-h6: colour + bold (no underline)

    Returns a list of strings — one per rendered line — so that line-number
    tracking stays aligned.
    """
    level = int(token.get("level", 1))
    text = str(token.get("text") or token.get("content", ""))
    markdown_key = f"h{level}"
    colour = theme.get("markdown", {}).get(markdown_key)
    lines: list[str] = [_style(text, theme, markdown_key, bold=True)]
    if level == 1 and colour:
        # h1: double-horizontal underline spanning heading text width
        lines.append(_style("═" * len(text), theme, markdown_key))
    elif level == 2 and colour:
        # h2: single-horizontal underline spanning heading text width
        lines.append(_style("─" * len(text), theme, markdown_key))
    return lines


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


def _render_math_display(token: dict[str, Any], theme: dict[str, Any], syntax_theme: str = "default") -> list[str]:
    """Render a display-math block ($$...$$) as centered mono text."""
    content = str(token.get("content", ""))
    language = str(token.get("language") or "")
    highlighted = highlight_code(content, language, theme, syntax_theme=syntax_theme)
    # Center each line within the terminal width.
    lines = highlighted.split("\n")
    width = _get_terminal_width()
    return [line.center(width) for line in lines]


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
            # Use parsed content (with inline HTML tags) so bold/italic/code
            # render correctly, falling back to raw text if no content present.
            text = str(item.get("content", item.get("text", "")))
            text = _strip_inline_tags(text, theme)

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


def _callout_color(callout_type: str, theme: dict[str, Any]) -> str | None:
    """Return the ANSI colour code for a callout type.

    Uses an optional per-theme ``callouts`` mapping first, then the built-in
    default colours, falling back to the neutral ``blockquote`` colour.
    """
    theme_callouts = theme.get("markdown", {}).get("callouts")
    if isinstance(theme_callouts, dict):
        color = theme_callouts.get(callout_type) or theme_callouts.get("default")
    else:
        color = _CALLOUT_DEFAULT_COLORS.get(callout_type)
    if not color:
        color = theme.get("markdown", {}).get("blockquote")
    return _ansi_color(color)


def _render_blockquote(token: dict[str, Any], theme: dict[str, Any]) -> list[str]:
    content = str(token.get("content", token.get("text", "")))
    callout_type = token.get("callout_type")
    rendered: list[str] = []

    if callout_type:
        # GFM callout/admonition: render a styled header line followed by body
        # lines carrying a coloured left border to distinguish them from
        # ordinary blockquotes.
        header_color = _callout_color(callout_type, theme)
        lines = [line.strip()[1:].lstrip() if line.strip().startswith(">") else line.strip()
                 for line in content.split("\n")]
        lines = [line for line in lines if line != ""]
        if not lines:
            # Empty callout (e.g. ``> [!NOTE]``) still shows its header marker.
            return [_style_with_color(f"▌ [!{callout_type}]", header_color, bold=True)]

        header = lines[0]
        marker = f"▌ [!{callout_type}]"
        header_text = f"{marker}  {header}" if header else marker
        # Style the header with the callout colour (bold); body lines carry a
        # matching coloured left border to distinguish them from plain quotes.
        rendered.append(_style_with_color(header_text, header_color, bold=True))
        for line in lines[1:]:
            border = _style_with_color("│", header_color)
            rendered.append(f"{border} {line}")
        return rendered

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
    # Strip inline tags from table cells so <math>, <strong>, etc. render
    # as visible text instead of raw markup.
    table_rows = [
        [_strip_inline_tags(cell) for cell in row]
        for row in table_rows
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


ITALIC = "\033[3m"


def _style(text: str, theme: dict[str, Any], markdown_key: str, *, bold: bool = False, italic: bool = False) -> str:
    codes: list[str] = []
    color = theme.get("markdown", {}).get(markdown_key)
    color_code = _ansi_color(color)
    if color_code:
        codes.append(color_code)
    if bold:
        codes.append(BOLD)
    if italic:
        codes.append(ITALIC)
    if not codes:
        return text
    return "".join(codes) + text + RESET


def _style_with_color(text: str, color_code: str | None, *, bold: bool = False, italic: bool = False) -> str:
    """Style ``text`` with an explicit ANSI colour code (no theme lookup)."""
    codes: list[str] = []
    if color_code:
        codes.append(color_code)
    if bold:
        codes.append(BOLD)
    if italic:
        codes.append(ITALIC)
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


def _style_inline_code(text: str, theme: dict[str, Any]) -> str:
    """Apply ANSI background color to inline code using theme's inline_code color."""
    color = theme.get("markdown", {}).get("inline_code")
    if not color:
        return text
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
        href = match.group(1)
        # Extract title attribute if present
        title = ""
        title_match = re.search(r'title="([^"]*)"', match.group(0))
        if title_match:
            title = title_match.group(1)
        if title:
            return _style(f"{label} ({href})", theme, "link")
        return _style(f"{label} ({href})", theme, "link")

    text = re.sub(
        r'<a\s+href="([^"]+)"\s*[^>]*>(.*?)</a>',
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
            r'<fnref\s+id="([^"]+)">',
            lambda m: _style(f"[{m.group(1)}]", theme, "footnote_ref"),
            text,
        )
    else:
        text = re.sub(
            r'<fnref\s+id="([^"]+)">',
            lambda m: _style(_superscript(m.group(1)), theme, "footnote_ref"),
            text,
        )

    inner_re = r"</?(?:strong|em|del|code|math)>"
    text = re.sub(r"<sub>(.*?)</sub>", lambda m: _style(_subscript(re.sub(inner_re, "", m.group(1))), theme, "subscript"), text)
    text = re.sub(r"<sup>(.*?)</sup>", lambda m: _style(_superscript(re.sub(inner_re, "", m.group(1))), theme, "superscript"), text)
    text = re.sub(r"<mark>(.*?)</mark>", lambda m: _highlight_text(re.sub(inner_re, "", m.group(1)), theme), text)

    # Strikethrough: ~~text~~ → coloured text with strikethrough escape
    def _strikethrough_handler(m: re.Match) -> str:
        raw = m.group(1)
        clean = re.sub(inner_re, "", raw)
        has_em = "<em>" in raw
        styled = _style(clean, theme, "strikethrough", bold=False, italic=has_em)
        return f"{STRIKETHROUGH}{styled}{STRIKETHROUGH_OFF}"

    text = re.sub(r"<del>(.*?)</del>", _strikethrough_handler, text)

    # Bold / bold+italic: <strong>text</strong> → ANSI bold
    # If the captured content contains <em>, apply bold+italic together.
    def _bold_handler(m: re.Match) -> str:
        raw = m.group(1)
        clean = re.sub(inner_re, "", raw)
        if "<em>" in raw:
            return _style(clean, theme, "strong", bold=True, italic=True)
        return _style(clean, theme, "strong", bold=True)

    text = re.sub(r"<strong>(.*?)</strong>", _bold_handler, text)

    # Italic: <em>text</em> → ANSI italic
    text = re.sub(
        r"<em>(.*?)</em>",
        lambda m: _style(re.sub(inner_re, "", m.group(1)), theme, "emphasis", italic=True),
        text,
    )

    # Math: show raw $...$ delimiters when math_fallback is enabled
    if math_fallback:
        text = re.sub(r"<math>(.*?)</math>", lambda m: f"${m.group(1)}$", text)
    else:
        text = re.sub(
            r"<math>(.*?)</math>",
            lambda m: _convert_math_notation(re.sub(inner_re, "", m.group(1))),
            text,
        )

    # Inline code: apply background color
    text = re.sub(
        r"<code>(.*?)</code>",
        lambda m: _style_inline_code(re.sub(inner_re, "", m.group(1)), theme),
        text,
    )

    # Strip any remaining inline tags that we did not handle above
    text = re.sub(r"</?(?:del|code|math|sub|sup|mark)>", "", text)
    return text


def _convert_math_notation(text: str) -> str:
    r"""Convert TeX-style ``^superscript`` and ``_subscript`` in math content to Unicode.

    Handles bare notation (``^2``, ``_i``) and grouped notation (``^{23}``, ``_{n}``),
    but leaves backslash commands (``\sum``, ``\frac``) untouched.
    """
    # Grouped superscript: ^{...} → superscript
    text = re.sub(
        r"(?<!\\)\^\{([^}]*)\}",
        lambda m: _superscript(m.group(1)),
        text,
    )
    # Bare superscript: ^<chars> → superscript (no whitespace/braces/backslash)
    text = re.sub(
        r"(?<!\\)\^([^\s{}\\]+)",
        lambda m: _superscript(m.group(1)),
        text,
    )
    # Grouped subscript: _{...} → subscript
    text = re.sub(
        r"(?<!\\)_\{([^}]*)\}",
        lambda m: _subscript(m.group(1)),
        text,
    )
    # Bare subscript: _<chars> → subscript (no whitespace/braces/backslash)
    text = re.sub(
        r"(?<!\\)_([^\s{}\\]+)",
        lambda m: _subscript(m.group(1)),
        text,
    )
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


