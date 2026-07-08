"""Syntax highlighting for mdutil code blocks."""

from __future__ import annotations

from typing import Any

from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import get_lexer_by_name
from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Text, Token
from pygments.util import ClassNotFound

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

    Looks up the style from Pygments and extracts the relevant token colors.
    """
    try:
        style = get_style_by_name(syntax_theme)
        # Extract colors from the style's styles dictionary
        styles: dict[Any, str] = {}
        for token_type, color in style.styles.items():
            # Map Pygments token types to our config keys
            if _is_hex_color(color):
                styles[token_type] = str(color)
        return styles
    except Exception:
        return {}


def _is_hex_color(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])


# Pygments style lookup (cached for performance)
_style_cache: dict[str, dict[Any, str]] = {}


def get_syntax_theme_colors(syntax_theme: str = "default") -> dict[Any, str]:
    """Get color mappings for a Pygments style by name.

    Uses a cache to avoid repeated lookups.
    """
    if syntax_theme in _style_cache:
        return _style_cache[syntax_theme]

    try:
        style = get_style_by_name(syntax_theme)
        styles: dict[Any, str] = {}
        for token_type, color in style.styles.items():
            if _is_hex_color(color):
                styles[token_type] = str(color)
        _style_cache[syntax_theme] = styles
        return styles
    except Exception:
        _style_cache[syntax_theme] = {}
        return {}
