import unittest

from mdutil.editor import EditingMode, FileEditorState, change_word, delete_current_line


class FileEditorStateTests(unittest.TestCase):
    def test_starts_in_normal_mode_and_tracks_dirty_state(self):
        state = FileEditorState("alpha")

        self.assertEqual(state.mode, EditingMode.NORMAL)
        self.assertFalse(state.dirty)

        state.text = "alpha!"
        self.assertTrue(state.dirty)

        state.mark_saved()
        self.assertFalse(state.dirty)

    def test_enter_insert_and_return_to_normal_mode(self):
        state = FileEditorState("alpha")

        state.enter_insert_mode()
        self.assertEqual(state.mode, EditingMode.INSERT)

        state.return_to_normal_mode()
        self.assertEqual(state.mode, EditingMode.NORMAL)

    def test_delete_current_line_removes_line_under_cursor(self):
        text, cursor = delete_current_line("alpha\nbeta\ngamma", len("alpha\nb"))

        self.assertEqual(text, "alpha\ngamma")
        self.assertEqual(cursor, len("alpha\n"))

    def test_delete_current_line_handles_last_and_only_line(self):
        self.assertEqual(delete_current_line("alpha\nbeta", len("alpha\nb")), ("alpha", 5))
        self.assertEqual(delete_current_line("only", 0), ("", 0))

    def test_change_word_removes_word_at_or_after_cursor(self):
        text, cursor = change_word("alpha beta gamma", len("alpha "))

        self.assertEqual(text, "alpha  gamma")
        self.assertEqual(cursor, len("alpha "))

    def test_state_change_word_enters_insert_mode(self):
        state = FileEditorState("alpha beta")

        text, cursor = state.change_word(0)

        self.assertEqual(text, " beta")
        self.assertEqual(cursor, 0)
        self.assertEqual(state.mode, EditingMode.INSERT)


if __name__ == "__main__":
    unittest.main()
