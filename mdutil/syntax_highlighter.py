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


def highlight_code(code: str, language: str = "", theme: dict[str, Any] | None = None) -> str:
    """Highlight code using Pygments, falling back to plain text.

    Unknown or missing languages intentionally return the original code unchanged so
    Markdown viewing never depends on lexer availability.
    """
    lexer_name = language.strip().lower()
    if not lexer_name or lexer_name in _PLAIN_TEXT_LANGUAGE_ALIASES:
        return code

    try:
        lexer = get_lexer_by_name(lexer_name, stripall=False)
    except ClassNotFound:
        return code

    formatter = TerminalTrueColorFormatter(style=_style_for_theme(theme), bg="")
    highlighted = highlight(code, lexer, formatter)
    return highlighted.rstrip("\n")


def _style_for_theme(theme: dict[str, Any] | None) -> type[Style]:
    code_theme = (theme or {}).get("code", {})
    styles: dict[Any, str] = {}
    for token_type, key in _CODE_TOKEN_KEYS.items():
        color = code_theme.get(key) or code_theme.get("default")
        if _is_hex_color(color):
            styles[token_type] = str(color)

    return type(
        "MdutilStyle",
        (Style,),
        {"default_style": "", "background_color": "", "styles": styles},
    )


def _is_hex_color(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])
