import unittest
from unittest.mock import patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from mdutil.display import (
    ScrollBuffer,
    ViewerState,
    build_help_modal_overlay,
    build_help_modal_text,
    build_interactive_app,
    build_status_bar_text,
)


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


if __name__ == "__main__":
    unittest.main()
