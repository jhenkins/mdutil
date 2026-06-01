import unittest

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from mdutil.display import ScrollBuffer, build_interactive_app


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

    def test_empty_documents_render_as_empty_visible_lines(self):
        buffer = ScrollBuffer([], height=3)

        self.assertEqual(buffer.visible_lines(), [])
        buffer.scroll_down()
        self.assertEqual(buffer.offset, 0)

    def test_prompt_toolkit_app_can_be_built_for_rendered_lines(self):
        with create_pipe_input() as pipe_input:
            app = build_interactive_app(["# Title", "body"], input=pipe_input, output=DummyOutput())

        self.assertTrue(app.full_screen)
        self.assertIsNotNone(app.layout)
        self.assertIsNotNone(app.key_bindings)


if __name__ == "__main__":
    unittest.main()
