"""Interactive terminal display for rendered Markdown."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
from typing import Any

from prompt_toolkit import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl


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
    input: Any | None = None,
    output: Any | None = None,
) -> Application:
    """Build the prompt-toolkit application for a rendered Markdown buffer."""
    scroll_buffer = ScrollBuffer(lines, line_numbers=line_numbers)
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

    @key_bindings.add("l")
    def _toggle_line_numbers(event) -> None:  # pragma: no cover - exercised by prompt-toolkit runtime
        scroll_buffer.toggle_line_numbers()
        event.app.invalidate()

    body = Window(
        content=FormattedTextControl(current_text, focusable=True),
        wrap_lines=False,
        always_hide_cursor=True,
    )
    help_line = Window(
        height=1,
        content=FormattedTextControl("j/k, arrows, PgUp/PgDn: scroll  •  l: line numbers  •  q: quit"),
        style="reverse",
        always_hide_cursor=True,
    )

    return Application(
        layout=Layout(HSplit([body, help_line]), focused_element=body),
        key_bindings=key_bindings,
        full_screen=True,
        mouse_support=False,
        input=input,
        output=output,
    )


def run_interactive_viewer(lines: Iterable[str], *, line_numbers: bool = False) -> None:
    """Run the interactive prompt-toolkit Markdown viewer."""
    build_interactive_app(lines, line_numbers=line_numbers).run()
