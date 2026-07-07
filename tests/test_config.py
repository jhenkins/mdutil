import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mdutil.config import DEFAULTS, default_config_path, ensure_config_file, load_config


class ConfigTests(unittest.TestCase):
    def test_default_config_path_uses_dotfile_in_home_on_linux_and_macos(self):
        with patch("mdutil.config.platform.system", return_value="Linux"):
            self.assertEqual(default_config_path(Path("/home/alice")), Path("/home/alice/.mdutilcfg"))

        with patch("mdutil.config.platform.system", return_value="Darwin"):
            self.assertEqual(default_config_path(Path("/Users/alice")), Path("/Users/alice/.mdutilcfg"))

    def test_default_config_path_uses_ini_in_home_on_windows(self):
        with patch("mdutil.config.platform.system", return_value="Windows"):
            self.assertEqual(default_config_path(Path("C:/Users/Alice")), Path("C:/Users/Alice/mdutil.ini"))

    def test_missing_config_file_is_created_with_defaults_and_helpful_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / ".mdutilcfg"

            created = ensure_config_file(path)

            self.assertTrue(created)
            text = path.read_text(encoding="utf-8")
            self.assertIn("# mdutil configuration file", text)
            self.assertIn("# Available built-in themes:", text)
            self.assertIn("theme = colored", text)
            self.assertIn("line_numbers = false", text)
            self.assertIn("status_bar_normal =", text)
            self.assertIn("status_bar_insert =", text)
            self.assertEqual(load_config(path), DEFAULTS)

    def test_existing_config_file_is_not_overwritten_and_values_are_loaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / ".mdutilcfg"
            path.write_text(
                "[mdutil]\n"
                "theme = dracula\n"
                "theme_file = /tmp/theme.json\n"
                "line_numbers = true\n"
                "quiet = true\n"
                "status_bar_normal = fg:#010203 bg:#040506\n"
                "status_bar_insert = fg:#111111 bg:#222222\n",
                encoding="utf-8",
            )

            created = ensure_config_file(path)
            loaded = load_config(path)

            self.assertFalse(created)
            self.assertEqual(loaded["theme"], "dracula")
            self.assertEqual(loaded["theme_file"], "/tmp/theme.json")
            self.assertTrue(loaded["line_numbers"])
            self.assertTrue(loaded["quiet"])
            self.assertEqual(loaded["status_bar_normal"], "fg:#010203 bg:#040506")
            self.assertEqual(loaded["status_bar_insert"], "fg:#111111 bg:#222222")


if __name__ == "__main__":
    unittest.main()
