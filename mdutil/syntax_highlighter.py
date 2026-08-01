"""Syntax highlighting for mdutil code blocks."""

from __future__ import annotations

import re
from typing import Any

from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import get_lexer_by_name
from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Text, Token
from pygments.util import ClassNotFound

_STYLE_CACHE: dict[str, dict[Any, str]] = {}

_CODE_TOKEN_KEYS = {
    Token: "text",
    Text: "text",
    Keyword: "keyword",
    Comment: "comment",
    Name.Function: "function",
    Name.Builtin: "builtin",
    String: "string",
    Number: "number",
    Operator: "operator",
}

_PLAIN_TEXT_LANGUAGE_ALIASES = {"text", "txt", "plain", "plaintext"}


def highlight_code(
    code: str,
    language: str = "",
    theme: dict[str, Any] | None = None,
    syntax_theme: str = "default",
) -> str:
    """Highlight code using Pygments, falling back to plain text.

    Unknown or missing languages intentionally return the original code unchanged so
    Markdown viewing never depends on lexer availability.

    Args:
        code: The code string to highlight.
        language: The language name for lexer detection.
        theme: Theme dict with code colors.
        syntax_theme: Pygments style name for code highlighting. Defaults to "default"
                      (uses theme's code colors only).
    """
    lexer_name = language.strip().lower()
    if not lexer_name or lexer_name in _PLAIN_TEXT_LANGUAGE_ALIASES:
        return code

    try:
        lexer = get_lexer_by_name(lexer_name, stripall=False)
    except ClassNotFound:
        return code

    formatter = TerminalTrueColorFormatter(
        style=_style_for_theme(theme, syntax_theme), bg=""
    )
    highlighted = highlight(code, lexer, formatter)
    return highlighted.rstrip("\n")


def highlight_code_html(
    code: str,
    language: str = "",
    syntax_theme: str = "default",
) -> str:
    """Return Pygments-highlighted HTML for a code block.

    Uses Pygments HtmlFormatter to generate syntax-highlighted HTML with
    CSS classes for token types. Falls back to plain text for unknown
    languages or plain text aliases.

    Args:
        code: The code string to highlight.
        language: The language name for lexer detection.
        syntax_theme: Pygments style name for color scheme.

    Returns:
        HTML string with <span> tags for token types, or plain text code.
    """
    lexer_name = language.strip().lower()
    if not lexer_name or lexer_name in _PLAIN_TEXT_LANGUAGE_ALIASES:
        return code  # Plain text, no highlighting needed

    try:
        lexer = get_lexer_by_name(lexer_name, stripall=False)
    except ClassNotFound:
        return code  # Unknown language, return as-is

    from pygments.formatters import HtmlFormatter
    formatter = HtmlFormatter(style=syntax_theme)
    highlighted = highlight(code, lexer, formatter)
    return highlighted.rstrip("\n")


def highlight_code_pdf(
    code: str,
    language: str = "",
    theme: dict[str, Any] | None = None,
    syntax_theme: str = "default",
) -> list[dict[str, Any]]:
    """Return list of (text, rgb_dict) segments for PDF rendering.

    Tokenizes code and groups consecutive tokens of the same style,
    mapping token types to RGB colors via theme + syntax theme colors.
    Falls back to plain text for unknown languages.

    Args:
        code: The code string to highlight.
        language: The language name for lexer detection.
        theme: Theme dict with code colors.
        syntax_theme: Pygments style name for color scheme.

    Returns:
        List of dicts with keys:
        - text: The code text for this segment
        - rgb: Optional dict with r, g, b keys (0-255) for text color
    """
    lexer_name = language.strip().lower()
    if not lexer_name or lexer_name in _PLAIN_TEXT_LANGUAGE_ALIASES:
        return [{"text": code, "rgb": None}]  # Plain text, no highlighting

    try:
        lexer = get_lexer_by_name(lexer_name, stripall=False)
    except ClassNotFound:
        return [{"text": code, "rgb": None}]  # Unknown language, no highlighting

    # Get merged colors from theme + syntax theme
    all_colors = _extract_all_token_colors(theme, syntax_theme)

    # Tokenize the code
    tokens = list(lexer.get_tokens(code))

    # Group consecutive tokens with same style
    segments: list[dict[str, Any]] = []
    current_text = ""
    current_rgb: dict[str, int] | None = None

    for token_type, text in tokens:
        # Get color for this token type
        rgb = _rgb_for_token_type(token_type, all_colors)

        # If color changed or text is empty, start new segment
        if (current_text and not text) or (
            (current_rgb is not None or rgb is not None)
            and current_rgb != rgb
        ):
            segments.append({"text": current_text, "rgb": current_rgb})
            current_text = ""
            current_rgb = rgb

        current_text += text

    # Don't forget the last segment
    if current_text:
        segments.append({"text": current_text, "rgb": current_rgb})

    # If no segments were created (e.g., all tokens had no color), return plain text
    if not segments:
        return [{"text": code, "rgb": None}]

    return segments


def _extract_all_token_colors(
    theme: dict[str, Any] | None,
    syntax_theme: str = "default",
) -> dict[Any, str]:
    """Extract all token-to-color mappings from theme + syntax theme.

    Merges theme code colors with syntax theme colors. Syntax theme takes
    precedence for overlapping token types. Handles Pygments style definitions
    that include modifiers like 'italic', 'bold' before the hex color.

    Args:
        theme: Theme dict with code colors.
        syntax_theme: Pygments style name.

    Returns:
        Dict mapping token types to hex color strings.
    """
    theme_colors = {}
    if theme:
        theme_colors = _extract_theme_code_colors(theme)

    syntax_colors = get_syntax_theme_colors(syntax_theme)

    # Merge: syntax theme overrides theme defaults
    merged = {**theme_colors, **syntax_colors}
    return merged


def _rgb_for_token_type(
    token_type: Any,
    all_colors: dict[Any, str],
) -> dict[str, int] | None:
    """Convert token type to RGB dict if color exists.

    Args:
        token_type: The Pygments token type.
        all_colors: Dict mapping token types to hex color strings.

    Returns:
        Dict with r, g, b keys (0-255), or None if no color.
    """
    # Look up color for this token type
    color = all_colors.get(token_type)

    # Walk up parent token types if no exact match (e.g., Token.Name.Builtin → Token.Name → Token)
    if not color:
        current = token_type
        while hasattr(current, 'parent') and current.parent is not None:
            current = current.parent
            color = all_colors.get(current)
            if color:
                break

    if color and _is_hex_color(color):
        # Convert hex to RGB
        hex_color = color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return {"r": r, "g": g, "b": b}

    return None


def _style_for_theme(
    theme: dict[str, Any] | None,
    syntax_theme: str = "default",
) -> type[Style]:
    """Build the Pygments Style class for code highlighting.

    Combines the theme's code colors with the syntax theme's colors.
    The syntax theme takes precedence where both define a color.
    """
    theme_colors = _extract_theme_code_colors(theme)
    syntax_colors = _extract_syntax_theme_colors(syntax_theme)

    # Merge: syntax theme overrides theme defaults
    merged_colors = {**theme_colors, **syntax_colors}

    return type(
        "MdutilStyle",
        (Style,),
        {"default_style": "", "background_color": "", "styles": merged_colors},
    )


def _extract_theme_code_colors(
    theme: dict[str, Any] | None,
) -> dict[Any, str]:
    """Extract code color mappings from a theme dict."""
    if not theme:
        return {}

    code_colors = theme.get("code", {})
    styles: dict[Any, str] = {}

    for token_type, key in _CODE_TOKEN_KEYS.items():
        color = code_colors.get(key) or code_colors.get("default")
        if _is_hex_color(color):
            styles[token_type] = str(color)

    return styles


def _extract_syntax_theme_colors(
    syntax_theme: str = "default",
) -> dict[Any, str]:
    """Extract color mappings from a Pygments style by name.

    Handles Pygments style definitions that include modifiers like 'italic' or 'bold'.
    """
    try:
        style = get_style_by_name(syntax_theme)
        # Extract colors from the style's styles dictionary
        styles: dict[Any, str] = {}
        for token_type, color in style.styles.items():
            hex_color = _extract_hex_color_from_style(color)
            if hex_color:
                styles[token_type] = hex_color
        return styles
    except Exception:
        return {}


def _is_hex_color(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])


def _extract_hex_color_from_style(style_value: str) -> str | None:
    """Extract hex color from Pygments style definition.

    Handles formats like '#008000', 'italic #3D7B7B', 'bold #FF0000 italic'.
    Returns None if no hex color found.
    """
    match = re.search(r'#([0-9a-fA-F]{6})', style_value)
    if match:
        return f"#{match.group(1)}"
    return None


def get_syntax_theme_colors(syntax_theme: str = "default") -> dict[Any, str]:
    """Get color mappings for a Pygments style by name.

    Uses a cache to avoid repeated lookups. Handles full Pygments style
    definitions that may include modifiers (italic, bold, etc.).
    """
    if syntax_theme in _STYLE_CACHE:
        return _STYLE_CACHE[syntax_theme]

    try:
        style = get_style_by_name(syntax_theme)
        styles: dict[Any, str] = {}

        for token_type, color in style.styles.items():
            # Extract hex color from full style definition
            hex_color = _extract_hex_color_from_style(color)
            if hex_color:
                styles[token_type] = hex_color

        _STYLE_CACHE[syntax_theme] = styles
        return styles
    except Exception:
        _STYLE_CACHE[syntax_theme] = {}
        return {}
