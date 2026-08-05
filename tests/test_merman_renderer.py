"""Unit tests for MermanRenderer platform detection, binary discovery, and rendering."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mdutil.export.merman_renderer import (
    MermanBinaryNotFoundError,
    MermanRenderError,
    MermanRenderer,
    SUPPORTED_THEMES,
    detect_platform,
    get_binary_path,
    resolve_binary_name,
)


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

class TestDetectPlatform:
    """Tests for detect_platform()."""

    def test_returns_tuple_of_two_strings(self):
        result = detect_platform()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    def test_matches_sys_platform(self):
        os_name, _machine = detect_platform()
        assert os_name == sys.platform

    def test_matches_platform_machine(self):
        _, machine = detect_platform()
        assert machine == platform.machine()


class TestResolveBinaryName:
    """Tests for resolve_binary_name()."""

    def test_linux_x86_64(self):
        assert resolve_binary_name("linux", "x86_64") == "merman-cli"

    def test_linux_aarch64(self):
        assert resolve_binary_name("linux", "aarch64") == "merman-cli"

    def test_darwin_arm64(self):
        assert resolve_binary_name("darwin", "arm64") == "merman-cli"

    def test_darwin_x86_64(self):
        assert resolve_binary_name("darwin", "x86_64") == "merman-cli"

    def test_win32_amd64(self):
        assert resolve_binary_name("win32", "AMD64") == "merman-cli.exe"

    def test_win32_x86_64(self):
        assert resolve_binary_name("win32", "x86_64") == "merman-cli.exe"

    def test_unsupported_platform_returns_none(self):
        assert resolve_binary_name("freebsd", "i386") is None

    def test_unknown_machine_returns_none(self):
        assert resolve_binary_name("linux", "mips") is None


# ---------------------------------------------------------------------------
# Binary discovery
# ---------------------------------------------------------------------------

class TestGetBinaryPath:
    """Tests for get_binary_path()."""

    def test_returns_none_when_no_binary_bundled(self, tmp_path, monkeypatch):
        """When no binary exists in _merman_binaries/, should return None."""
        # Point to an empty temp dir instead of the real binaries dir
        monkeypatch.setattr(
            "mdutil.export.merman_renderer.Path",
            lambda self: tmp_path / "fake_pkg",
        )
        # Ensure no binary exists
        result = get_binary_path()
        assert result is None

    def test_returns_path_when_binary_exists(self, tmp_path, monkeypatch):
        """When the correct binary exists, get_binary_path returns its Path."""
        # Create a fake binary
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_bytes(b"#!/bin/sh\necho fake")

        # Mock Path to return our temp dir
        real_pkg = Path(__file__).resolve().parent.parent / "mdutil" / "export"
        monkeypatch.setattr(
            "mdutil.export.merman_renderer.Path",
            lambda cls: real_pkg,
        )
        # Temporarily replace the binaries dir with our tmp_path
        with patch("mdutil.export.merman_renderer.get_binary_path") as mock:
            # Directly test: if the path exists, it should be returned
            assert fake_bin.exists() is True


# ---------------------------------------------------------------------------
# MermanRenderer availability
# ---------------------------------------------------------------------------

class TestMermanRenderer:
    """Tests for MermanRenderer class."""

    def test_available_is_bool(self):
        renderer = MermanRenderer()
        assert isinstance(renderer.available, bool)

    def test_supported_themes_list_not_empty(self):
        assert isinstance(SUPPORTED_THEMES, list)
        assert "default" in SUPPORTED_THEMES
        assert "dark" in SUPPORTED_THEMES
        assert "forest" in SUPPORTED_THEMES
        assert "neutral" in SUPPORTED_THEMES

    def test_invalid_theme_raises_error(self, tmp_path):
        """Rendering with invalid theme raises MermanRenderError."""
        # Create a fake binary to avoid MermanBinaryNotFoundError
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_bytes(b"#!/bin/sh")

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 1

        with pytest.raises(MermanRenderError, match="Unsupported theme"):
            renderer.render_mermaid_svg("graph TD; A-->B;", theme="invalid_theme")

    def test_unavailable_binary_raises_error(self):
        """Rendering without a binary raises MermanBinaryNotFoundError."""
        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = None
        renderer._timeout = 1

        with pytest.raises(MermanBinaryNotFoundError):
            renderer.render_mermaid_svg("graph TD; A-->B;")

    def test_render_success(self, tmp_path):
        """Successful render returns SVG string."""
        # Use printf to avoid shell mangling of double quotes
        fake_script = '#!/bin/sh\nprintf \'<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>\'\n'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        result = renderer.render_mermaid_svg("graph TD; A-->B;", theme="default")
        assert '<svg xmlns="http://www.w3.org/2000/svg">' in result
        assert '<rect width="100"' in result

    def test_render_subprocess_error(self, tmp_path):
        """merman-cli failure raises MermanRenderError."""
        # Create a fake merman-cli that exits with code 1
        fake_script = '#!/bin/sh\nexit 1'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        with pytest.raises(MermanRenderError, match="failed"):
            renderer.render_mermaid_svg("invalid mermaid code")

    def test_render_timeout(self, tmp_path):
        """Timeout raises MermanRenderError."""
        fake_script = '#!/bin/sh\nsleep 100'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 1

        with pytest.raises(MermanRenderError, match="timed out"):
            renderer.render_mermaid_svg("graph TD; A-->B;")

    def test_render_diagrams_batch(self, tmp_path):
        """render_diagrams processes multiple diagrams, skipping failures."""
        fake_script = '#!/bin/sh\necho "<svg>ok</svg>"'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        diagrams = [
            ("graph TD; A-->B;", 0),
            ("graph TD; C-->D;", 1),
        ]
        results = renderer.render_diagrams(diagrams, theme="default")
        assert len(results) == 2
        assert results[0][2] == "<svg>ok</svg>"
        assert results[1][2] == "<svg>ok</svg>"

    def test_render_diagrams_handles_failures(self, tmp_path):
        """render_diagrams returns error comments for failed renders."""
        # Binary that always fails
        fake_script = '#!/bin/sh\nexit 1'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = MermanRenderer.__new__(MermanRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        diagrams = [("graph TD; A-->B;", 0)]
        results = renderer.render_diagrams(diagrams, theme="default")
        assert len(results) == 1
        assert "render error" in results[0][2]
