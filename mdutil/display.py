"""Interactive terminal display for rendered Markdown."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
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
from prompt_toolkit.widgets import Shadow


@dataclass
class ViewerState:
    """Mutable state for interactive viewer chrome."""

    help_visible: bool = False

    def toggle_help(self) -> None:
        self.help_visible = not self.help_visible

    def close_help(self) -> None:
        self.help_visible = False


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
            "Escape: close help",
            "q: quit",
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


def build_status_bar_text(document_name: str | None = None) -> str:
    """Return the compact bottom status bar text."""
    name = document_name or "stdin"
    return f"F1 Help  •  {name}  •  q Quit"


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


def build_interactive_app(
    lines: Iterable[str],
    *,
    line_numbers: bool = False,
    document_name: str | None = None,
    input: Any | None = None,
    output: Any | None = None,
) -> Application:
    """Build the prompt-toolkit application for a rendered Markdown buffer."""
    scroll_buffer = ScrollBuffer(lines, line_numbers=line_numbers)
    viewer_state = ViewerState()
    key_bindings = KeyBindings()

    def current_text() -> ANSI:
        app = get_app()
        # Leave one row for the help/status line.
        scroll_buffer.set_height(max(1, app.output.get_size().rows - 1))
        return ANSI("\n".join(scroll_buffer.visible_lines()))

    @key_bindings.add("q")
    @key_bindings.add("c-c")
    def _quit(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        event.app.exit()

    @key_bindings.add("j")
    @key_bindings.add("down")
    def _scroll_down(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.scroll_down()
        event.app.invalidate()

    @key_bindings.add("k")
    @key_bindings.add("up")
    def _scroll_up(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.scroll_up()
        event.app.invalidate()

    @key_bindings.add("pagedown")
    def _page_down(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.page_down()
        event.app.invalidate()

    @key_bindings.add("pageup")
    def _page_up(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.page_up()
        event.app.invalidate()

    @key_bindings.add("f1")
    def _toggle_help(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        viewer_state.toggle_help()
        event.app.invalidate()

    @key_bindings.add("escape")
    def _close_help(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        viewer_state.close_help()
        event.app.invalidate()

    @key_bindings.add("l")
    def _toggle_line_numbers(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.toggle_line_numbers()
        event.app.invalidate()

    body = Window(
        content=FormattedTextControl(current_text, focusable=True),
        wrap_lines=True,
        always_hide_cursor=True,
    )
    help_line = Window(
        height=1,
        content=FormattedTextControl(build_status_bar_text(document_name)),
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
        content=HSplit([body, help_line]),
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
        layout=Layout(root_container, focused_element=body),
        key_bindings=key_bindings,
        full_screen=True,
        mouse_support=False,
        style=Style.from_dict({"shadow": "bg:#444444"}),
        input=input,
        output=output,
    )
    setattr(app, "mdutil_viewer_state", viewer_state)
    return app


def run_interactive_viewer(
    lines: Iterable[str],
    *,
    line_numbers: bool = False,
    document_name: str | None = None,
) -> None:
    """Run the interactive prompt-toolkit Markdown viewer."""
    build_interactive_app(
        lines,
        line_numbers=line_numbers,
        document_name=document_name,
    ).run()
