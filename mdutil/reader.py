"""Markdown reader module - reads markdown from files or stdin."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PathLike = str | os.PathLike[str]


def read_markdown_file(file_path: PathLike) -> str:
    """Read content from a Markdown file as UTF-8 text.

    Raises filesystem/encoding exceptions for the CLI or caller to present.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")

    return path.read_text(encoding="utf-8")


def read_stdin() -> str:
    """Read all Markdown content from stdin."""
    return sys.stdin.read()


def read_input(file_path: PathLike | None = None) -> str:
    """Read Markdown content from a file path, '-' or stdin.

    Args:
        file_path: Path to a Markdown file. If None or '-', stdin is read.

    Raises:
        FileNotFoundError: if the requested file does not exist.
        IsADirectoryError: if the requested path is a directory.
        UnicodeDecodeError: if the file is not valid UTF-8.
    """
    if file_path in (None, "-"):
        return read_stdin()
    return read_markdown_file(file_path)
