"""Interactive terminal display for rendered Markdown."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
from typing import Any

from prompt_toolkit import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import ConditionalContainer, Float, FloatContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Shadow, TextArea

from .editor import EditingMode, FileEditorState, change_word, delete_current_line
from .parser import parse_markdown
from .renderer import render
from .themes import DEFAULT_THEME


@dataclass
class ViewerState:
    """Mutable state for interactive viewer chrome."""

    help_visible: bool = False
    save_error: str | None = None

    def toggle_help(self) -> None:
        self.help_visible = not self.help_visible

    def close_help(self) -> None:
        self.help_visible = False

    def clear_save_error(self) -> None:
        self.save_error = None

    def record_save_error(self, error: OSError) -> None:
        self.save_error = f"{error.__class__.__name__}: {error}"


def build_help_modal_text() -> str:
    """Return the interactive help text shown in the F1 modal."""
    return "\n".join(
        [
            "mdutil help",
            "",
            "F1: toggle this help",
            "j / Down: scroll down",
            "k / Up: scroll up",
            "PageDown: page down",
            "PageUp: page up",
            "l: toggle line numbers",
            "i: insert mode",
            "Ctrl-S: save explicitly when a file target is available",
            "!q: discard unsaved changes and quit",
            "Escape: close help / leave insert mode",
            "q: quit when buffer is unmodified",
        ]
    )


HELP_MODAL_TITLE = "F1 - Help"


def build_help_modal_overlay(columns: int, rows: int) -> str:
    """Return the bordered F1 help modal content without positioning or shadow."""
    content_lines = build_help_modal_text().splitlines()
    content_width = max(len(line) for line in content_lines)
    inner_width = max(content_width + 6, len(HELP_MODAL_TITLE) + 4)

    modal_lines = [
        _build_titled_top_border(inner_width),
        "│" + " " * inner_width + "│",
        *[
            "│  " + line.ljust(inner_width - 4) + "  │"
            for line in content_lines
        ],
        "│" + " " * inner_width + "│",
        "└" + "─" * inner_width + "┘",
    ]

    return "\n".join(modal_lines)


def _build_titled_top_border(inner_width: int) -> str:
    title = f" {HELP_MODAL_TITLE} "
    remaining_width = inner_width - len(title)
    if remaining_width <= 0:
        return "┌" + "─" * inner_width + "┐"
    return "┌" + "─" + title + "─" * (remaining_width - 1) + "┐"


def help_modal_size() -> tuple[int, int]:
    """Return the width and height of the rendered help modal box."""
    lines = build_help_modal_overlay(columns=0, rows=0).splitlines()
    return max(len(line) for line in lines), len(lines)


def build_status_bar_text(
    document_name: str | None = None,
    *,
    mode: EditingMode = EditingMode.NORMAL,
    dirty: bool = False,
    save_error: str | None = None,
    scroll_percent: int | None = None,
) -> str:
    """Return the compact bottom status bar text."""
    name = document_name or "stdin"
    document_segment = name if scroll_percent is None else f"{name}  •  {scroll_percent}%"
    if save_error:
        return f"F1 Help  •  {name}  •  save failed: {save_error}"
    if mode is EditingMode.INSERT:
        dirty_text = "modified" if dirty else "unmodified"
        return f"INSERT  •  {name}  •  {dirty_text}  •  Esc Normal"
    if dirty:
        return f"F1 Help  •  {document_segment}  •  modified  •  Ctrl-S Save  •  !q Discard"
    return f"F1 Help  •  {document_segment}  •  q Quit"


@dataclass
class ScrollBuffer:
    """A bounded scroll viewport over pre-rendered lines."""

    lines: list[str]
    height: int = 24
    offset: int = 0
    line_numbers: bool = False

    def __init__(
        self,
        lines: Iterable[str],
        height: int = 24,
        *,
        line_numbers: bool = False,
    ) -> None:
        self.lines = list(lines)
        self.height = max(1, height)
        self.offset = 0
        self.line_numbers = line_numbers

    @property
    def max_offset(self) -> int:
        return max(0, len(self.lines) - self.height)

    def visible_lines(self) -> list[str]:
        end = self.offset + self.height
        lines = self.lines[self.offset:end]
        if not self.line_numbers:
            return lines
        return [
            f"{line_number:4d} | {line}"
            for line_number, line in enumerate(lines, self.offset + 1)
        ]

    def toggle_line_numbers(self) -> None:
        self.line_numbers = not self.line_numbers

    def scroll_down(self, amount: int = 1) -> None:
        self.offset = min(self.max_offset, self.offset + max(1, amount))

    def scroll_up(self, amount: int = 1) -> None:
        self.offset = max(0, self.offset - max(1, amount))

    def page_down(self) -> None:
        self.scroll_down(self.height)

    def page_up(self) -> None:
        self.scroll_up(self.height)

    def set_height(self, height: int) -> None:
        self.height = max(1, height)
        self.offset = min(self.offset, self.max_offset)


def atomic_write_text(path: Path, text: str) -> None:
    """Atomically write UTF-8 text, preserving the original file on failure."""
    target = Path(path)
    directory = target.parent
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=directory,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(text)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, target)
    except Exception:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def build_interactive_app(
    lines: Iterable[str],
    *,
    line_numbers: bool = False,
    document_name: str | None = None,
    save_path: str | None = None,
    theme: str = DEFAULT_THEME,
    theme_file: str | None = None,
    input: Any | None = None,
    output: Any | None = None,
) -> Application:
    """Build the prompt-toolkit application for a source Markdown file editor."""
    source_lines = list(lines)
    original_text = "\n".join(source_lines)
    editor_state = FileEditorState(original_text)
    key_bindings = KeyBindings()
    viewer_state = ViewerState()
    line_numbers_enabled = {"value": line_numbers}
    normal_scroll_offset = {"value": 0}
    normal_mode = Condition(lambda: editor_state.mode is EditingMode.NORMAL)
    insert_mode = Condition(lambda: editor_state.mode is EditingMode.INSERT)

    def sync_state_from_editor() -> None:
        editor_state.text = editor.text

    def is_dirty() -> bool:
        sync_state_from_editor()
        return editor_state.dirty

    def editor_line_prefix(line_number: int, wrap_count: int) -> str:
        if not line_numbers_enabled["value"]:
            return ""
        if wrap_count:
            return "       "
        return f"{line_number + 1:4d} | "

    rendered_preview_cache: dict[str, Any] = {
        "text": None,
        "line_numbers": None,
        "lines": [],
    }

    def rendered_editor_lines() -> list[str]:
        sync_state_from_editor()
        cache_is_current = (
            rendered_preview_cache["text"] == editor_state.text
            and rendered_preview_cache["line_numbers"] == line_numbers_enabled["value"]
        )
        if not cache_is_current:
            rendered_text = render(
                parse_markdown(editor_state.text),
                theme=theme,
                theme_file=theme_file,
                line_numbers=line_numbers_enabled["value"],
            )
            rendered_preview_cache["text"] = editor_state.text
            rendered_preview_cache["line_numbers"] = line_numbers_enabled["value"]
            rendered_preview_cache["lines"] = rendered_text.splitlines()
        return rendered_preview_cache["lines"]

    def rendered_editor_text() -> str:
        return "\n".join(rendered_editor_lines())

    def normal_view_height() -> int:
        try:
            active_output = output if output is not None else get_app().output
            # Leave room for the one-line status bar.
            return max(1, active_output.get_size().rows - 1)
        except Exception:
            return 24

    def max_normal_scroll_offset() -> int:
        line_count = len(rendered_editor_lines())
        return max(0, line_count - normal_view_height())

    def normal_scroll_percent() -> int:
        max_offset = max_normal_scroll_offset()
        if max_offset == 0:
            return 100
        return round((normal_scroll_offset["value"] / max_offset) * 100)

    def visible_rendered_editor_text() -> str:
        start = normal_scroll_offset["value"]
        end = start + normal_view_height()
        return "\n".join(rendered_editor_lines()[start:end])

    def clamp_normal_scroll_offset() -> None:
        normal_scroll_offset["value"] = min(
            normal_scroll_offset["value"],
            max_normal_scroll_offset(),
        )

    def scroll_normal_view(amount: int) -> None:
        normal_scroll_offset["value"] = max(
            0,
            min(max_normal_scroll_offset(), normal_scroll_offset["value"] + amount),
        )

    def jump_normal_view_to_top() -> None:
        normal_scroll_offset["value"] = 0

    def jump_normal_view_to_bottom() -> None:
        normal_scroll_offset["value"] = max_normal_scroll_offset()

    editor = TextArea(
        text=original_text,
        multiline=True,
        wrap_lines=True,
        scrollbar=True,
        focusable=True,
        read_only=normal_mode,
        get_line_prefix=editor_line_prefix,
    )
    normal_viewer = Window(
        content=FormattedTextControl(lambda: ANSI(visible_rendered_editor_text())),
        wrap_lines=True,
    )

    def delete_editor_current_line() -> None:
        sync_state_from_editor()
        new_text, new_cursor = delete_current_line(
            editor_state.text,
            editor.buffer.cursor_position,
        )
        editor_state.text = new_text
        editor.text = new_text
        editor.buffer.cursor_position = new_cursor

    def change_editor_word() -> None:
        sync_state_from_editor()
        new_text, new_cursor = change_word(
            editor_state.text,
            editor.buffer.cursor_position,
        )
        editor_state.text = new_text
        editor.text = new_text
        editor.buffer.cursor_position = new_cursor
        editor_state.enter_insert_mode()

    @key_bindings.add("q", filter=normal_mode)
    @key_bindings.add("c-c")
    def _quit(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        if is_dirty():
            event.app.invalidate()
            return
        event.app.exit()

    @key_bindings.add("!", "q", filter=normal_mode)
    def _discard_and_quit(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        event.app.exit()

    @key_bindings.add("c-s")
    def _save(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        sync_state_from_editor()
        if save_path is not None:
            try:
                atomic_write_text(Path(save_path), editor_state.text)
            except OSError as error:
                viewer_state.record_save_error(error)
            else:
                viewer_state.clear_save_error()
                editor_state.mark_saved()
        event.app.invalidate()

    @key_bindings.add("j", filter=normal_mode)
    @key_bindings.add("down", filter=normal_mode)
    def _cursor_down(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_down(count=1)
        scroll_normal_view(1)
        event.app.invalidate()

    @key_bindings.add("k", filter=normal_mode)
    @key_bindings.add("up", filter=normal_mode)
    def _cursor_up(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_up(count=1)
        scroll_normal_view(-1)
        event.app.invalidate()

    @key_bindings.add("pagedown", filter=normal_mode)
    def _page_down(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_down(count=10)
        scroll_normal_view(normal_view_height())
        event.app.invalidate()

    @key_bindings.add("pageup", filter=normal_mode)
    def _page_up(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_up(count=10)
        scroll_normal_view(-normal_view_height())
        event.app.invalidate()

    @key_bindings.add("home", filter=normal_mode)
    def _jump_to_top(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_position = 0
        jump_normal_view_to_top()
        event.app.invalidate()

    @key_bindings.add("end", filter=normal_mode)
    def _jump_to_bottom(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor.buffer.cursor_position = len(editor.text)
        jump_normal_view_to_bottom()
        event.app.invalidate()

    @key_bindings.add("f1", filter=normal_mode)
    def _toggle_help(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        viewer_state.toggle_help()
        event.app.invalidate()

    @key_bindings.add("escape")
    def _close_help(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        viewer_state.close_help()
        if editor_state.mode is EditingMode.INSERT:
            sync_state_from_editor()
            editor_state.return_to_normal_mode()
            event.app.layout.focus(editor)
        event.app.invalidate()

    @key_bindings.add("l", filter=normal_mode)
    def _toggle_line_numbers(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        line_numbers_enabled["value"] = not line_numbers_enabled["value"]
        event.app.invalidate()

    @key_bindings.add("i", filter=normal_mode)
    def _enter_insert_mode(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        editor_state.enter_insert_mode()
        event.app.layout.focus(editor)
        event.app.invalidate()

    @key_bindings.add("d", "d", filter=normal_mode)
    def _delete_current_line(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        delete_editor_current_line()
        clamp_normal_scroll_offset()
        event.app.invalidate()

    @key_bindings.add("c", "w", filter=normal_mode)
    def _change_word(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        change_editor_word()
        event.app.layout.focus(editor)
        event.app.invalidate()

    help_line = Window(
        height=1,
        content=FormattedTextControl(
            lambda: build_status_bar_text(
                document_name,
                mode=editor_state.mode,
                dirty=is_dirty(),
                save_error=viewer_state.save_error,
                scroll_percent=normal_scroll_percent() if editor_state.mode is EditingMode.NORMAL else None,
            )
        ),
        style="reverse",
        always_hide_cursor=True,
    )

    def current_help_overlay() -> ANSI:
        app = get_app()
        size = app.output.get_size()
        return ANSI(build_help_modal_overlay(columns=size.columns, rows=size.rows))

    modal_width, modal_height = help_modal_size()

    help_modal = ConditionalContainer(
        Shadow(
            Window(
                content=FormattedTextControl(current_help_overlay),
                width=modal_width,
                height=modal_height,
                dont_extend_width=True,
                dont_extend_height=True,
                always_hide_cursor=True,
            )
        ),
        filter=Condition(lambda: viewer_state.help_visible),
    )
    root_container = FloatContainer(
        content=HSplit(
            [
                ConditionalContainer(normal_viewer, filter=normal_mode),
                ConditionalContainer(editor, filter=insert_mode),
                help_line,
            ]
        ),
        floats=[
            Float(
                content=help_modal,
                width=modal_width + 1,
                height=modal_height + 1,
                transparent=True,
            )
        ],
    )

    app = Application(
        layout=Layout(root_container, focused_element=editor),
        key_bindings=key_bindings,
        full_screen=True,
        mouse_support=False,
        style=Style.from_dict({"shadow": "bg:#444444"}),
        input=input,
        output=output,
    )
    setattr(app, "mdutil_viewer_state", viewer_state)
    setattr(app, "mdutil_editor", editor)
    setattr(app, "mdutil_normal_viewer", normal_viewer)
    setattr(app, "mdutil_rendered_text", rendered_editor_text)
    setattr(app, "mdutil_visible_rendered_text", visible_rendered_editor_text)
    setattr(app, "mdutil_normal_scroll_offset", lambda: normal_scroll_offset["value"])
    setattr(app, "mdutil_normal_scroll_percent", normal_scroll_percent)
    setattr(app, "mdutil_editor_state", editor_state)
    setattr(app, "mdutil_editing_mode", lambda: editor_state.mode)
    setattr(app, "mdutil_line_numbers_enabled", lambda: line_numbers_enabled["value"])
    setattr(app, "mdutil_is_dirty", is_dirty)
    return app

def run_interactive_viewer(
    lines: Iterable[str],
    *,
    line_numbers: bool = False,
    document_name: str | None = None,
    save_path: str | None = None,
    theme: str = DEFAULT_THEME,
    theme_file: str | None = None,
) -> None:
    """Run the interactive prompt-toolkit Markdown viewer."""
    build_interactive_app(
        lines,
        line_numbers=line_numbers,
        document_name=document_name,
        save_path=save_path,
        theme=theme,
        theme_file=theme_file,
    ).run()
