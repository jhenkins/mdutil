import re
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.widgets import TextArea

from mdutil.display import (
    EditingMode,
    ScrollBuffer,
    ViewerState,
    atomic_write_text,
    build_help_modal_overlay,
    build_help_modal_text,
    build_interactive_app,
    build_status_bar_text,
)


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


class ViewerStateTests(unittest.TestCase):
    def test_help_modal_starts_hidden_and_can_be_toggled_or_closed(self):
        state = ViewerState()

        self.assertFalse(state.help_visible)

        state.toggle_help()
        self.assertTrue(state.help_visible)

        state.close_help()
        self.assertFalse(state.help_visible)

    def test_help_modal_text_documents_interactive_keys(self):
        help_text = build_help_modal_text()

        self.assertIn("F1", help_text)
        self.assertIn("j / Down", help_text)
        self.assertIn("k / Up", help_text)
        self.assertIn("PageDown", help_text)
        self.assertIn("PageUp", help_text)
        self.assertIn("l", help_text)
        self.assertIn("i", help_text)
        self.assertIn("Ctrl-S", help_text)
        self.assertIn("!q", help_text)
        self.assertIn("Escape", help_text)
        self.assertIn("q", help_text)

    def test_help_modal_overlay_has_titled_border_without_manual_shadow(self):
        overlay = build_help_modal_overlay(columns=80, rows=24)
        lines = overlay.splitlines()

        self.assertTrue(lines[0].startswith("┌"))
        self.assertIn("F1 - Help", lines[0])
        self.assertTrue(lines[0].endswith("┐"))
        self.assertTrue(any("└" in line and "┘" in line for line in lines))
        self.assertTrue(any("│" in line for line in lines))
        self.assertNotIn("░", overlay)
        self.assertIn("F1: toggle this help", overlay)

    def test_help_modal_overlay_is_not_positioned_with_leading_spaces(self):
        overlay = build_help_modal_overlay(columns=80, rows=24)
        lines = overlay.splitlines()

        self.assertTrue(lines)
        self.assertTrue(all(not line.startswith(" ") for line in lines if line))
        self.assertEqual(lines[0][0], "┌")

    def test_help_modal_overlay_is_slightly_larger_than_content(self):
        overlay = build_help_modal_overlay(columns=80, rows=24)
        lines = overlay.splitlines()
        content_width = max(len(line) for line in build_help_modal_text().splitlines())

        self.assertGreaterEqual(len(lines[0]), content_width + 8)
        self.assertGreaterEqual(len(lines), len(build_help_modal_text().splitlines()) + 4)


    def test_status_bar_text_is_short_and_includes_document_name(self):
        status_text = build_status_bar_text("guide.md")

        self.assertEqual(status_text, "F1 Help  •  guide.md  •  q Quit")
        self.assertNotIn("j/k", status_text)
        self.assertNotIn("PgUp", status_text)

    def test_status_bar_text_uses_stdin_when_document_name_is_missing(self):
        self.assertEqual(build_status_bar_text(None), "F1 Help  •  stdin  •  q Quit")

    def test_status_bar_text_shows_prompt_toolkit_insert_mode(self):
        self.assertEqual(
            build_status_bar_text("guide.md", mode=EditingMode.INSERT, dirty=True),
            "INSERT  •  guide.md  •  modified  •  Esc Normal",
        )

    def test_status_bar_text_shows_dirty_normal_mode_safe_quit_hint(self):
        self.assertEqual(
            build_status_bar_text("guide.md", dirty=True),
            "F1 Help  •  guide.md  •  modified  •  Ctrl-S Save  •  !q Discard",
        )

    def test_status_bar_text_reports_save_failures(self):
        self.assertEqual(
            build_status_bar_text("guide.md", dirty=True, save_error="PermissionError: denied"),
            "F1 Help  •  guide.md  •  save failed: PermissionError: denied",
        )


class ScrollBufferTests(unittest.TestCase):
    def test_visible_lines_start_at_top_and_fit_viewport(self):
        buffer = ScrollBuffer(["one", "two", "three"], height=2)

        self.assertEqual(buffer.visible_lines(), ["one", "two"])
        self.assertEqual(buffer.offset, 0)

    def test_scroll_down_and_up_with_j_k_semantics(self):
        buffer = ScrollBuffer(["one", "two", "three", "four"], height=2)

        buffer.scroll_down()
        self.assertEqual(buffer.offset, 1)
        self.assertEqual(buffer.visible_lines(), ["two", "three"])

        buffer.scroll_down()
        buffer.scroll_down()
        self.assertEqual(buffer.offset, 2)
        self.assertEqual(buffer.visible_lines(), ["three", "four"])

        buffer.scroll_up()
        self.assertEqual(buffer.offset, 1)
        self.assertEqual(buffer.visible_lines(), ["two", "three"])

    def test_scroll_bounds_for_short_documents(self):
        buffer = ScrollBuffer(["only"], height=5)

        buffer.scroll_down()
        self.assertEqual(buffer.offset, 0)
        self.assertEqual(buffer.visible_lines(), ["only"])

        buffer.scroll_up()
        self.assertEqual(buffer.offset, 0)

    def test_page_down_and_page_up_scroll_by_viewport_height(self):
        buffer = ScrollBuffer([f"line {number}" for number in range(1, 11)], height=4)

        buffer.page_down()
        self.assertEqual(buffer.offset, 4)
        self.assertEqual(
            buffer.visible_lines(),
            ["line 5", "line 6", "line 7", "line 8"],
        )

        buffer.page_down()
        self.assertEqual(buffer.offset, 6)
        self.assertEqual(
            buffer.visible_lines(),
            ["line 7", "line 8", "line 9", "line 10"],
        )

        buffer.page_up()
        self.assertEqual(buffer.offset, 2)
        self.assertEqual(
            buffer.visible_lines(),
            ["line 3", "line 4", "line 5", "line 6"],
        )

        buffer.page_up()
        self.assertEqual(buffer.offset, 0)
        self.assertEqual(
            buffer.visible_lines(),
            ["line 1", "line 2", "line 3", "line 4"],
        )

    def test_empty_documents_render_as_empty_visible_lines(self):
        buffer = ScrollBuffer([], height=3)

        self.assertEqual(buffer.visible_lines(), [])
        buffer.scroll_down()
        self.assertEqual(buffer.offset, 0)

    def test_line_numbers_can_be_toggled_for_visible_lines(self):
        buffer = ScrollBuffer(["alpha", "beta", "gamma"], height=2)

        self.assertEqual(buffer.visible_lines(), ["alpha", "beta"])

        buffer.toggle_line_numbers()
        self.assertEqual(buffer.visible_lines(), ["   1 | alpha", "   2 | beta"])

        buffer.scroll_down()
        self.assertEqual(buffer.visible_lines(), ["   2 | beta", "   3 | gamma"])

        buffer.toggle_line_numbers()
        self.assertEqual(buffer.visible_lines(), ["beta", "gamma"])

    def test_prompt_toolkit_app_can_be_built_for_rendered_lines(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        self.assertTrue(app.full_screen)
        self.assertIsNotNone(app.layout)
        self.assertIsNotNone(app.key_bindings)

    def test_prompt_toolkit_app_exposes_native_prompt_toolkit_editor_buffer(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "", "body"], input=pipe_input, output=DummyOutput())

        editor = getattr(app, "mdutil_editor")
        self.assertIsInstance(editor, TextArea)
        self.assertEqual(editor.text, "# Title\n\nbody")
        self.assertEqual(getattr(app, "mdutil_editing_mode")(), EditingMode.NORMAL)

    def test_prompt_toolkit_normal_mode_renders_markdown_preview(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "", "body"], input=pipe_input, output=DummyOutput())

        rendered = getattr(app, "mdutil_rendered_text")()
        self.assertIn("\033[", rendered)
        self.assertEqual(strip_ansi(rendered), "# Title\n\nbody")

    def test_prompt_toolkit_normal_mode_syntax_highlights_code_blocks(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(
                ["```python", "def greet():", "    return 'hi'", "```"],
                input=pipe_input,
                output=DummyOutput(),
            )

        rendered = getattr(app, "mdutil_rendered_text")()
        self.assertIn("\033[", rendered)
        self.assertEqual(strip_ansi(rendered), "def greet():\n    return 'hi'")

    def test_prompt_toolkit_body_wraps_long_lines(self):
        long_line = "This is a very long line that should wrap instead of being clipped. " * 4
        with create_pipe_input() as pipe_input:
            app = build_interactive_app([long_line], input=pipe_input, output=DummyOutput())

        normal_viewer = getattr(app, "mdutil_normal_viewer")
        editor = getattr(app, "mdutil_editor")
        self.assertTrue(normal_viewer.wrap_lines())
        self.assertTrue(editor.window.wrap_lines())

    def test_prompt_toolkit_normal_navigation_scrolls_rendered_preview(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(
                [f"- line {number}" for number in range(50)],
                input=pipe_input,
                output=DummyOutput(),
            )

        self.assertIsNotNone(app.key_bindings)
        key_bindings = cast(Any, app.key_bindings)
        down_binding = next(
            binding
            for binding in key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("j",)
        )
        up_binding = next(
            binding
            for binding in key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("k",)
        )

        class FakeApp:
            def __init__(self):
                self.invalidations = 0

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        event = FakeEvent()
        self.assertTrue(strip_ansi(getattr(app, "mdutil_visible_rendered_text")()).startswith("- line 0"))
        down_binding.handler(cast(Any, event))
        self.assertEqual(getattr(app, "mdutil_normal_scroll_offset")(), 1)
        self.assertTrue(strip_ansi(getattr(app, "mdutil_visible_rendered_text")()).startswith("- line 1"))
        up_binding.handler(cast(Any, event))
        self.assertEqual(getattr(app, "mdutil_normal_scroll_offset")(), 0)
        self.assertTrue(strip_ansi(getattr(app, "mdutil_visible_rendered_text")()).startswith("- line 0"))
        self.assertEqual(event.app.invalidations, 2)

    def test_prompt_toolkit_app_binds_page_navigation_keys(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        self.assertIsNotNone(app.key_bindings)
        bound_keys = {
            str(key)
            for binding in app.key_bindings.bindings
            for key in binding.keys
        }
        self.assertIn("Keys.PageDown", bound_keys)
        self.assertIn("Keys.PageUp", bound_keys)

    def test_prompt_toolkit_app_binds_help_modal_keys(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        self.assertIsNotNone(app.key_bindings)
        bound_keys = {
            str(key)
            for binding in app.key_bindings.bindings
            for key in binding.keys
        }
        self.assertIn("Keys.F1", bound_keys)
        self.assertIn("Keys.Escape", bound_keys)

    def test_prompt_toolkit_app_exposes_viewer_state_for_help_modal(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        viewer_state = getattr(app, "mdutil_viewer_state")
        self.assertIsInstance(viewer_state, ViewerState)
        self.assertFalse(viewer_state.help_visible)

    def test_prompt_toolkit_help_key_handlers_toggle_and_close_help_modal(self):
        class FakeApp:
            def __init__(self):
                self.invalidations = 0

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        viewer_state = getattr(app, "mdutil_viewer_state")
        f1_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if any(str(key) == "Keys.F1" for key in binding.keys)
        )
        escape_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if any(str(key) == "Keys.Escape" for key in binding.keys)
        )

        event = FakeEvent()
        f1_binding.handler(event)
        self.assertTrue(viewer_state.help_visible)
        self.assertEqual(event.app.invalidations, 1)

        escape_binding.handler(event)
        self.assertFalse(viewer_state.help_visible)
        self.assertEqual(event.app.invalidations, 2)

    def test_run_interactive_viewer_passes_document_name_to_app_builder(self):
        class FakeApp:
            def __init__(self):
                self.ran = False

            def run(self):
                self.ran = True

        fake_app = FakeApp()
        with patch("mdutil.display.build_interactive_app", return_value=fake_app) as builder:
            from mdutil.display import run_interactive_viewer

            run_interactive_viewer(["# Title"], line_numbers=True, document_name="guide.md")

        builder.assert_called_once_with(
            ["# Title"],
            line_numbers=True,
            document_name="guide.md",
            save_path=None,
            theme="colored",
            theme_file=None,
        )
        self.assertTrue(fake_app.ran)

    def test_prompt_toolkit_app_binds_line_number_toggle_key(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        self.assertIsNotNone(app.key_bindings)
        bound_keys = {
            str(key)
            for binding in app.key_bindings.bindings
            for key in binding.keys
        }
        self.assertIn("l", bound_keys)

    def test_insert_mode_focuses_native_editor_and_escape_returns_to_viewer(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha", "", "omega"], input=pipe_input, output=DummyOutput())

        insert_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("i",)
        )
        escape_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if any(str(key) == "Keys.Escape" for key in binding.keys)
        )

        class FakeApp:
            def __init__(self):
                self.invalidations = 0
                self.focused = None
                self.layout = self

            def focus(self, control):
                self.focused = control

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        event = FakeEvent()
        insert_binding.handler(event)
        self.assertEqual(getattr(app, "mdutil_editing_mode")(), EditingMode.INSERT)
        self.assertIs(event.app.focused, getattr(app, "mdutil_editor"))

        escape_binding.handler(event)
        self.assertEqual(getattr(app, "mdutil_editing_mode")(), EditingMode.NORMAL)
        self.assertGreaterEqual(event.app.invalidations, 2)

    def test_prompt_toolkit_runtime_uses_native_editor_for_cursor_blank_lines_and_backspace(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha", "", "omega"], input=pipe_input, output=DummyOutput())

            def feed_keys():
                time.sleep(0.05)
                pipe_input.send_text("i")
                time.sleep(0.05)
                pipe_input.send_text("\x1b[B")
                time.sleep(0.05)
                pipe_input.send_text("x")
                time.sleep(0.05)
                pipe_input.send_text("\x7f")
                time.sleep(0.05)
                pipe_input.send_text("\x1b")
                time.sleep(0.05)
                pipe_input.send_text("q")

            threading.Thread(target=feed_keys, daemon=True).start()
            app.run()

        editor = getattr(app, "mdutil_editor")
        self.assertEqual(editor.text, "alpha\n\nomega")
        self.assertEqual(getattr(app, "mdutil_editing_mode")(), EditingMode.NORMAL)

    def test_dirty_editor_blocks_plain_quit_and_allows_explicit_discard(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha"], input=pipe_input, output=DummyOutput())

        editor = getattr(app, "mdutil_editor")
        editor.text = "alpha!"
        quit_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("q",)
        )
        discard_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("!", "q")
        )

        class FakeApp:
            def __init__(self):
                self.exited = False
                self.invalidations = 0

            def exit(self):
                self.exited = True

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        event = FakeEvent()
        quit_binding.handler(event)
        self.assertFalse(event.app.exited)
        self.assertEqual(event.app.invalidations, 1)

        discard_binding.handler(event)
        self.assertTrue(event.app.exited)

    def test_dd_deletes_current_line_in_true_file_editor(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha", "beta", "gamma"], input=pipe_input, output=DummyOutput())

        editor = getattr(app, "mdutil_editor")
        editor.buffer.cursor_position = len("alpha\nb")
        delete_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("d", "d")
        )

        class FakeApp:
            def __init__(self):
                self.invalidations = 0

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        event = FakeEvent()
        delete_binding.handler(event)

        self.assertEqual(editor.text, "alpha\ngamma")
        self.assertEqual(editor.buffer.cursor_position, len("alpha\n"))
        self.assertTrue(getattr(app, "mdutil_is_dirty")())
        self.assertEqual(event.app.invalidations, 1)

    def test_cw_changes_word_and_enters_insert_mode_in_true_file_editor(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha beta gamma"], input=pipe_input, output=DummyOutput())

        editor = getattr(app, "mdutil_editor")
        editor.buffer.cursor_position = len("alpha ")
        change_word_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("c", "w")
        )

        class FakeApp:
            def __init__(self):
                self.invalidations = 0
                self.focused = None
                self.layout = self

            def focus(self, control):
                self.focused = control

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        event = FakeEvent()
        change_word_binding.handler(event)

        self.assertEqual(editor.text, "alpha  gamma")
        self.assertEqual(editor.buffer.cursor_position, len("alpha "))
        self.assertEqual(getattr(app, "mdutil_editing_mode")(), EditingMode.INSERT)
        self.assertIs(event.app.focused, editor)
        self.assertEqual(event.app.invalidations, 1)

    def test_line_number_toggle_updates_true_file_editor_prefix_state(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["alpha"], input=pipe_input, output=DummyOutput())

        toggle_binding = next(
            binding
            for binding in app.key_bindings.bindings
            if tuple(str(key) for key in binding.keys) == ("l",)
        )

        class FakeApp:
            def __init__(self):
                self.invalidations = 0

            def invalidate(self):
                self.invalidations += 1

        class FakeEvent:
            def __init__(self):
                self.app = FakeApp()

        self.assertFalse(getattr(app, "mdutil_line_numbers_enabled")())
        event = FakeEvent()
        toggle_binding.handler(event)

        self.assertTrue(getattr(app, "mdutil_line_numbers_enabled")())
        self.assertEqual(event.app.invalidations, 1)

    def test_ctrl_s_saves_file_backed_editor_and_clears_dirty_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("alpha", encoding="utf-8")
            with create_pipe_input() as pipe_input:
                app = build_interactive_app(
                    ["alpha"],
                    save_path=str(path),
                    input=pipe_input,
                    output=DummyOutput(),
                )

            editor = getattr(app, "mdutil_editor")
            editor.text = "alpha!"
            save_binding = next(
                binding
                for binding in app.key_bindings.bindings
                if any(str(key) == "Keys.ControlS" for key in binding.keys)
            )
            quit_binding = next(
                binding
                for binding in app.key_bindings.bindings
                if tuple(str(key) for key in binding.keys) == ("q",)
            )

            class FakeApp:
                def __init__(self):
                    self.exited = False
                    self.invalidations = 0

                def exit(self):
                    self.exited = True

                def invalidate(self):
                    self.invalidations += 1

            class FakeEvent:
                def __init__(self):
                    self.app = FakeApp()

            event = FakeEvent()
            save_binding.handler(event)
            self.assertEqual(path.read_text(encoding="utf-8"), "alpha!")
            self.assertFalse(getattr(app, "mdutil_is_dirty")())

            quit_binding.handler(event)
            self.assertTrue(event.app.exited)

    def test_ctrl_s_write_failure_preserves_file_and_dirty_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("alpha", encoding="utf-8")
            with create_pipe_input() as pipe_input:
                app = build_interactive_app(
                    ["alpha"],
                    save_path=str(path),
                    input=pipe_input,
                    output=DummyOutput(),
                )

            editor = getattr(app, "mdutil_editor")
            editor.text = "alpha!"
            self.assertIsNotNone(app.key_bindings)
            key_bindings = cast(Any, app.key_bindings)
            save_binding = next(
                binding
                for binding in key_bindings.bindings
                if any(str(key) == "Keys.ControlS" for key in binding.keys)
            )

            class FakeApp:
                def __init__(self):
                    self.invalidations = 0

                def invalidate(self):
                    self.invalidations += 1

            class FakeEvent:
                def __init__(self):
                    self.app = FakeApp()

            with patch("mdutil.display.atomic_write_text", side_effect=OSError("disk full")):
                event = FakeEvent()
                save_binding.handler(cast(Any, event))

            self.assertEqual(path.read_text(encoding="utf-8"), "alpha")
            self.assertTrue(getattr(app, "mdutil_is_dirty")())
            self.assertEqual(getattr(app, "mdutil_viewer_state").save_error, "OSError: disk full")
            self.assertEqual(event.app.invalidations, 1)

    def test_ctrl_s_permission_failure_is_reported_without_marking_saved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("alpha", encoding="utf-8")
            with create_pipe_input() as pipe_input:
                app = build_interactive_app(
                    ["alpha"],
                    save_path=str(path),
                    input=pipe_input,
                    output=DummyOutput(),
                )

            editor = getattr(app, "mdutil_editor")
            editor.text = "alpha!"
            self.assertIsNotNone(app.key_bindings)
            key_bindings = cast(Any, app.key_bindings)
            save_binding = next(
                binding
                for binding in key_bindings.bindings
                if any(str(key) == "Keys.ControlS" for key in binding.keys)
            )

            class FakeApp:
                def invalidate(self):
                    pass

            class FakeEvent:
                def __init__(self):
                    self.app = FakeApp()

            with patch("mdutil.display.atomic_write_text", side_effect=PermissionError("denied")):
                save_binding.handler(cast(Any, FakeEvent()))

            self.assertEqual(path.read_text(encoding="utf-8"), "alpha")
            self.assertTrue(getattr(app, "mdutil_is_dirty")())
            self.assertEqual(
                getattr(app, "mdutil_viewer_state").save_error,
                "PermissionError: denied",
            )

    def test_atomic_write_replaces_file_and_cleans_failed_temp_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("alpha", encoding="utf-8")

            atomic_write_text(path, "beta")

            self.assertEqual(path.read_text(encoding="utf-8"), "beta")
            self.assertEqual(list(Path(tmpdir).glob(".doc.md.*.tmp")), [])

    def test_atomic_write_preserves_original_file_when_replace_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("alpha", encoding="utf-8")

            with patch("mdutil.display.os.replace", side_effect=PermissionError("denied")):
                with self.assertRaises(PermissionError):
                    atomic_write_text(path, "beta")

            self.assertEqual(path.read_text(encoding="utf-8"), "alpha")
            self.assertEqual(list(Path(tmpdir).glob(".doc.md.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
