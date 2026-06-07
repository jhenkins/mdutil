"""Pure editing state and text operations for mdutil's file editor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class EditingMode(Enum):
    """High-level editor mode."""

    NORMAL = "normal"
    INSERT = "insert"


@dataclass
class FileEditorState:
    """Small editing-state model independent of prompt-toolkit rendering."""

    text: str
    saved_text: str | None = None
    mode: EditingMode = EditingMode.NORMAL

    def __post_init__(self) -> None:
        if self.saved_text is None:
            self.saved_text = self.text

    @property
    def dirty(self) -> bool:
        """Return True when the editor text differs from the last saved text."""
        return self.text != self.saved_text

    def enter_insert_mode(self) -> None:
        """Switch to insert mode."""
        self.mode = EditingMode.INSERT

    def return_to_normal_mode(self) -> None:
        """Switch back to normal mode."""
        self.mode = EditingMode.NORMAL

    def mark_saved(self) -> None:
        """Record the current text as saved."""
        self.saved_text = self.text

    def delete_current_line(self, cursor_position: int) -> tuple[str, int]:
        """Delete the line containing cursor_position and return text plus new cursor."""
        self.text, cursor_position = delete_current_line(self.text, cursor_position)
        return self.text, cursor_position

    def change_word(self, cursor_position: int) -> tuple[str, int]:
        """Delete the word at/after cursor_position and enter insert mode."""
        self.text, cursor_position = change_word(self.text, cursor_position)
        self.enter_insert_mode()
        return self.text, cursor_position


def delete_current_line(text: str, cursor_position: int) -> tuple[str, int]:
    """Return text with the current line removed and cursor placed safely."""
    if text == "":
        return "", 0

    cursor_position = _clamp_cursor(text, cursor_position)
    line_start = text.rfind("\n", 0, cursor_position) + 1
    next_newline = text.find("\n", cursor_position)

    if next_newline == -1:
        if line_start == 0:
            return "", 0
        new_text = text[: line_start - 1]
        return new_text, min(line_start - 1, len(new_text))

    new_text = text[:line_start] + text[next_newline + 1 :]
    return new_text, min(line_start, len(new_text))


def change_word(text: str, cursor_position: int) -> tuple[str, int]:
    """Delete the word at or after cursor_position and return text plus cursor."""
    if text == "":
        return "", 0

    cursor_position = _clamp_cursor(text, cursor_position)
    match = re.search(r"\w+", text[cursor_position:])
    if match is None:
        return text, cursor_position

    start = cursor_position + match.start()
    end = cursor_position + match.end()
    return text[:start] + text[end:], start


def _clamp_cursor(text: str, cursor_position: int) -> int:
    return max(0, min(cursor_position, len(text)))
