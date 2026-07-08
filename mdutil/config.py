"""Configuration file handling for mdutil."""

from __future__ import annotations

import configparser
import platform
from pathlib import Path
from typing import Any

from .themes import DEFAULT_THEME, syntax_theme_names, theme_names

DEFAULTS: dict[str, Any] = {
    "theme": DEFAULT_THEME,
    "theme_file": None,
    "syntax_theme": "default",
    "line_numbers": False,
    "quiet": False,
    "status_bar_normal": None,
    "status_bar_insert": None,
}

SECTION = "mdutil"


def default_config_path(home: Path | None = None) -> Path:
    """Return the conventional per-user mdutil configuration path."""
    home_path = Path.home() if home is None else Path(home)
    if platform.system() == "Windows":
        return home_path / "mdutil.ini"
    return home_path / ".mdutilcfg"


def ensure_config_file(path: Path) -> bool:
    """Create a default configuration file when missing.

    Returns True when a new file was created and False when an existing file was
    left untouched.
    """
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_config_text(), encoding="utf-8")
    return True


def load_config(path: Path) -> dict[str, Any]:
    """Load mdutil runtime defaults from an INI configuration file."""
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    loaded = DEFAULTS.copy()
    if not parser.has_section(SECTION):
        return loaded

    section = parser[SECTION]
    if "theme" in section:
        raw_theme = (
            section.get("theme", fallback=DEFAULTS["theme"])
            or DEFAULTS["theme"]
        )
        loaded["theme"] = raw_theme.strip() or DEFAULTS["theme"]
    if "theme_file" in section:
        raw_theme_file = section.get("theme_file", fallback="") or ""
        theme_file = raw_theme_file.strip()
        loaded["theme_file"] = theme_file or None
    if "syntax_theme" in section:
        raw_syntax_theme = section.get("syntax_theme", fallback="") or ""
        syntax_theme = raw_syntax_theme.strip()
        if syntax_theme not in syntax_theme_names():
            valid = ", ".join(syntax_theme_names())
            raise ValueError(f"invalid syntax theme in configuration: {syntax_theme!r} (choose from {valid})")
        loaded["syntax_theme"] = syntax_theme or DEFAULTS["syntax_theme"]
    if "line_numbers" in section:
        loaded["line_numbers"] = section.getboolean(
            "line_numbers",
            fallback=DEFAULTS["line_numbers"],
        )
    if "quiet" in section:
        loaded["quiet"] = section.getboolean(
            "quiet",
            fallback=DEFAULTS["quiet"],
        )
    for key in ("status_bar_normal", "status_bar_insert"):
        if key in section:
            raw_style = section.get(key, fallback="") or ""
            style = raw_style.strip()
            loaded[key] = style or None
    return loaded


def default_config_text() -> str:
    """Return the commented starter configuration with current runtime defaults."""
    themes = ", ".join(theme_names())
    syntax_themes = ", ".join(syntax_theme_names())
    return f"""# mdutil configuration file
#
# This file is plain INI-style text and can be edited with any standard text
# editor. It is created automatically when missing.
#
# Runtime precedence:
#   built-in defaults -> this configuration file -> explicit CLI options

[{SECTION}]
# Built-in theme to use when --theme is not supplied.
# Available built-in themes: {themes}
theme = {DEFAULTS['theme']}

# Syntax theme for code highlighting (Pygments style name).
# Available styles: {syntax_themes}
syntax_theme = {DEFAULTS['syntax_theme']}

# Optional path to a JSON or TOML custom theme file.
# Leave empty to use only the selected built-in theme.
theme_file =

# Show line numbers by default when --line-numbers is not supplied.
# Accepted values: true, false, yes, no, on, off, 1, 0
line_numbers = false

# Suppress rendered output by default when --quiet is not supplied.
# Accepted values: true, false, yes, no, on, off, 1, 0
quiet = false

# Optional prompt-toolkit style overrides for the bottom status bar.
# Leave empty to use the selected theme's status_bar.normal and status_bar.insert colors.
# Example: fg:#ffffff bg:#303030
status_bar_normal =
status_bar_insert =
"""
