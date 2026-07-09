import re
import subprocess
import sys
import unittest
from pathlib import Path

import tomllib

from mdutil import __version__


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


class ProjectMetadataTests(unittest.TestCase):
    def test_prompt_toolkit_is_a_runtime_dependency(self):
        metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        dependencies = metadata["project"]["dependencies"]
        self.assertTrue(any(dep.startswith("prompt-toolkit") for dep in dependencies))

    def test_spec_documents_prompt_toolkit_decision_and_textual_alternative(self):
        spec = Path("mdutil-specification.md").read_text(encoding="utf-8").lower()

        self.assertIn("prompt-toolkit", spec)
        self.assertIn("textual", spec)
        self.assertIn("heavier alternative", spec)

    def test_package_version_is_semver(self):
        self.assertRegex(__version__, SEMVER_RE)

    def test_package_version_is_current_release(self):
        self.assertEqual(__version__, "2.3.1")

    def test_pyproject_uses_package_version_as_single_source_of_truth(self):
        metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        self.assertNotIn("version", metadata["project"])
        self.assertIn("version", metadata["project"]["dynamic"])
        self.assertEqual(
            metadata["tool"]["setuptools"]["dynamic"]["version"],
            {"attr": "mdutil.version.__version__"},
        )

    def test_cli_version_uses_package_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "mdutil", "--version"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"mdutil {__version__}\n")

    def test_readme_documents_semver_release_strategy(self):
        readme = Path("README.md").read_text(encoding="utf-8").lower()

        self.assertIn("semantic versioning", readme)
        self.assertIn("major", readme)
        self.assertIn("minor", readme)
        self.assertIn("patch", readme)
        self.assertIn("0.y.z", readme)
        self.assertIn("v{version}", readme)


if __name__ == "__main__":
    unittest.main()
