"""Theme definitions and loading for mdutil."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MARKDOWN_COLORS: dict[str, str] = {
    "h1": "#1a1a1a",
    "h2": "#2a2a2a",
    "h3": "#3a3a3a",
    "h4": "#4a4a4a",
    "h5": "#5a5a5a",
    "h6": "#6a6a6a",
    "link": "#0000ff",
    "blockquote": "#888888",
    "hr": "#cccccc",
    "blockquote_border": "#444444",
}

CODE_COLORS: dict[str, str] = {
    "default": "#888888",
    "text": "#cccccc",
    "keyword": "#0000ff",
    "comment": "#888888",
    "function": "#0000ff",
    "builtin": "#ff0000",
    "string": "#cc0000",
    "number": "#cc0000",
    "operator": "#330033",
    "punctuation": "#330033",
}

# Default Pygments syntax style — used when --syntax-theme is not specified
SYNTAX_THEME_DEFAULT = "default"

# Syntax themes per built-in theme — Pygments style names
# These match the Pygments built-in styles and provide a reasonable default
# for each visual theme. Users can override via --syntax-theme or config.
THEME_SYNTAX_THEMES: dict[str, str] = {
    "colored": "default",
    "dracula": "dracula",
    "high-contrast": "bw",
    "one-dark": "one-dark",
    "onedark": "one-dark",
}

STATUS_BAR_COLORS: dict[str, str] = {
    "normal": "fg:#ffffff bg:#303030",
    "insert": "fg:#111111 bg:#f4d35e",
    "dirty": "fg:#ffffff bg:#8a5a00",
    "error": "fg:#ffffff bg:#8b0000",
}

COLORED: dict[str, Any] = {
    "name": "colored",
    "markdown": MARKDOWN_COLORS.copy(),
    "code": CODE_COLORS.copy(),
    "syntax": "default",
    "status_bar": STATUS_BAR_COLORS.copy(),
}

DRACULA: dict[str, Any] = {
    "name": "dracula",
    "markdown": {
        "h1": "#ff79c6",
        "h2": "#ff79c6",
        "h3": "#ff79c6",
        "h4": "#ff79c6",
        "h5": "#ff79c6",
        "h6": "#ff79c6",
        "link": "#8be9fd",
        "blockquote": "#6272a4",
        "hr": "#6272a4",
        "blockquote_border": "#44475a",
    },
    "code": {
        "keyword": "#ff79c6",
        "comment": "#6272a4",
        "function": "#50fa7b",
        "builtin": "#ff79c6",
        "string": "#f1fa8c",
        "number": "#bd93f9",
        "operator": "#6272a4",
        "punctuation": "#6272a4",
    },
    "status_bar": {
        "normal": "fg:#f8f8f2 bg:#44475a",
        "insert": "fg:#282a36 bg:#50fa7b",
        "dirty": "fg:#282a36 bg:#f1fa8c",
        "error": "fg:#f8f8f2 bg:#ff5555",
    },
    "syntax": "default",
}

HIGH_CONTRAST: dict[str, Any] = {
    "name": "high-contrast",
    "markdown": {
        "h1": "#ffffff",
        "h2": "#ffffff",
        "h3": "#ffffff",
        "h4": "#ffffff",
        "h5": "#ffffff",
        "h6": "#ffffff",
        "link": "#00ffff",
        "blockquote": "#ffffff",
        "hr": "#e5e5e5",
        "blockquote_border": "#000000",
    },
    "code": {
        "keyword": "#ffff00",
        "comment": "#888888",
        "function": "#00ff00",
        "builtin": "#ffff00",
        "string": "#ff5555",
        "number": "#ffff00",
        "operator": "#00ffff",
        "punctuation": "#00ffff",
    },
    "status_bar": {
        "normal": "fg:#ffffff bg:#000000",
        "insert": "fg:#000000 bg:#ffff00",
        "dirty": "fg:#000000 bg:#00ffff",
        "error": "fg:#ffffff bg:#ff0000",
    },
    "syntax": "default",
}

ONE_DARK: dict[str, Any] = {
    "name": "one-dark",
    "markdown": {
        "h1": "#61afef",
        "h2": "#61afef",
        "h3": "#61afef",
        "h4": "#61afef",
        "h5": "#61afef",
        "h6": "#61afef",
        "link": "#e5c07b",
        "blockquote": "#495974",
        "hr": "#e5e5e5",
        "blockquote_border": "#373b44",
    },
    "code": {
        "keyword": "#c678dd",
        "comment": "#5c6370",
        "function": "#61afef",
        "builtin": "#e06c75",
        "string": "#98c379",
        "number": "#d19a66",
        "operator": "#56b6c2",
        "punctuation": "#56b6c2",
    },
    "status_bar": {
        "normal": "fg:#abb2bf bg:#282c34",
        "insert": "fg:#282c34 bg:#98c379",
        "dirty": "fg:#282c34 bg:#e5c07b",
        "error": "fg:#ffffff bg:#e06c75",
    },
    "syntax": "default",
}

BUILT_IN_THEMES: dict[str, dict[str, Any]] = {
    "colored": COLORED,
    "dracula": DRACULA,
    "high-contrast": HIGH_CONTRAST,
    "one-dark": ONE_DARK,
    "onedark": ONE_DARK,
}

DEFAULT_THEME = "colored"


def theme_names() -> list[str]:
    """Return valid built-in theme names for CLI validation/help."""
    return sorted(BUILT_IN_THEMES)


def syntax_theme_names() -> list[str]:
    """Return valid syntax (Pygments) style names for CLI validation/help."""
    from pygments.styles import get_all_styles

    return sorted(get_all_styles())


def load_theme(theme: str = DEFAULT_THEME, theme_file: str | None = None) -> dict[str, Any]:
    """Load a built-in theme and optionally merge a JSON/TOML custom theme over it."""
    if theme not in BUILT_IN_THEMES:
        valid = ", ".join(theme_names())
        raise ValueError(f"Unknown theme '{theme}'. Valid themes: {valid}")

    selected = _deep_copy(BUILT_IN_THEMES[theme])
    if not theme_file:
        return selected

    custom_theme = _read_theme_file(Path(theme_file))
    return _merge_dicts(selected, custom_theme)


def _read_theme_file(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".toml":
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"Theme file must contain an object: {path}")
    return data


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = _deep_copy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _deep_copy(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _deep_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_deep_copy(item) for item in value]
    return value
