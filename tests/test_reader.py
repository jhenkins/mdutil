import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mdutil.reader import read_input, read_markdown_file, read_stdin


class ReaderTests(unittest.TestCase):
    def test_read_input_reads_path_argument_as_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "doc.md"
            path.write_text("# From file\n", encoding="utf-8")

            content = read_input(path)

        self.assertEqual(content, "# From file\n")

    def test_read_input_reads_dash_from_stdin(self):
        with patch("sys.stdin", io.StringIO("# From dash\n")):
            content = read_input("-")

        self.assertEqual(content, "# From dash\n")

    def test_read_input_reads_none_from_stdin(self):
        with patch("sys.stdin", io.StringIO("# From stdin\n")):
            content = read_input(None)

        self.assertEqual(content, "# From stdin\n")

    def test_read_stdin_reads_sys_stdin_without_printing_or_exiting(self):
        with patch("sys.stdin", io.StringIO("stdin text")), patch("sys.exit") as sys_exit:
            content = read_stdin()

        self.assertEqual(content, "stdin text")
        sys_exit.assert_not_called()

    def test_missing_file_raises_file_not_found_without_printing_or_exiting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.md"
            stderr = io.StringIO()
            with patch("sys.stderr", stderr), patch("sys.exit") as sys_exit:
                with self.assertRaises(FileNotFoundError) as raised:
                    read_markdown_file(path)

        self.assertIn("File not found", str(raised.exception))
        self.assertEqual(stderr.getvalue(), "")
        sys_exit.assert_not_called()

    def test_directory_path_raises_is_a_directory_without_printing_or_exiting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stderr = io.StringIO()
            with patch("sys.stderr", stderr), patch("sys.exit") as sys_exit:
                with self.assertRaises(IsADirectoryError) as raised:
                    read_input(Path(tmpdir))

        self.assertIn("Path is a directory", str(raised.exception))
        self.assertEqual(stderr.getvalue(), "")
        sys_exit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
