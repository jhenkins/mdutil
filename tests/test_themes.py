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

    def test_load_toml_custom_theme_merges_over_default_theme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "theme.toml"
            path.write_text(
                '[markdown]\nh1 = "#0a0b0c"\n\n[code]\nkeyword = "#0d0e0f"\n',
                encoding="utf-8",
            )

            theme = load_theme(DEFAULT_THEME, str(path))

        self.assertEqual(theme["markdown"]["h1"], "#0a0b0c")
        self.assertEqual(theme["code"]["keyword"], "#0d0e0f")
        self.assertIn("h2", theme["markdown"])
        self.assertIn("string", theme["code"])


if __name__ == "__main__":
    unittest.main()
