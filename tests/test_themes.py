import tempfile
import unittest
from pathlib import Path

from mdutil.themes import DEFAULT_THEME, load_theme


class ThemeTests(unittest.TestCase):
    def test_unknown_theme_name_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown theme 'missing'"):
            load_theme("missing")

    def test_load_json_custom_theme_merges_over_default_theme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "theme.json"
            path.write_text(
                '{"markdown": {"h1": "#010203"}, "code": {"string": "#040506"}}',
                encoding="utf-8",
            )

            theme = load_theme(DEFAULT_THEME, str(path))

        self.assertEqual(theme["markdown"]["h1"], "#010203")
        self.assertEqual(theme["code"]["string"], "#040506")
        self.assertIn("h2", theme["markdown"])
        self.assertIn("keyword", theme["code"])
        self.assertIn("normal", theme["status_bar"])
        self.assertIn("insert", theme["status_bar"])

    def test_load_toml_custom_theme_merges_over_default_theme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "theme.toml"
            path.write_text(
                '[markdown]\nh1 = "#0a0b0c"\n\n[code]\nkeyword = "#0d0e0f"\n\n[status_bar]\ninsert = "fg:#101010 bg:#eeeeee"\n',
                encoding="utf-8",
            )

            theme = load_theme(DEFAULT_THEME, str(path))

        self.assertEqual(theme["markdown"]["h1"], "#0a0b0c")
        self.assertEqual(theme["code"]["keyword"], "#0d0e0f")
        self.assertEqual(theme["status_bar"]["insert"], "fg:#101010 bg:#eeeeee")
        self.assertIn("h2", theme["markdown"])
        self.assertIn("string", theme["code"])
        self.assertIn("normal", theme["status_bar"])


if __name__ == "__main__":
    unittest.main()
