"""MermanRenderer: Bundle infrastructure for offline Mermaid SVG rendering.

Bundles merman-cli binary for air-gapped Mermaid diagram rendering in HTML export.
Detects platform at runtime and invokes the appropriate pre-built binary.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Platform → merman-cli binary filename mapping
_PLATFORM_BINARY_MAP = {
    ("linux", "x86_64"): "merman-cli-linux-x86_64",
    ("linux", "aarch64"): "merman-cli-linux-aarch64",
    ("darwin", "arm64"): "merman-cli-darwin-arm64",
    ("darwin", "x86_64"): "merman-cli-darwin-x86_64",
    ("win32", "AMD64"): "merman-cli-windows-x64.exe",
    ("win32", "x86_64"): "merman-cli-windows-x64.exe",
}

# Default Mermaid themes supported by merman-cli
SUPPORTED_THEMES = ["default", "forest", "dark", "neutral"]

# Timeout for merman-cli subprocess (seconds)
RENDER_TIMEOUT = 30


class MermanBinaryNotFoundError(RuntimeError):
    """Raised when the merman-cli binary cannot be located for the current platform."""


class MermanRenderError(RuntimeError):
    """Raised when merman-cli fails to render the given Mermaid source."""


def detect_platform() -> tuple[str, str]:
    """Detect the current platform as (os, machine) tuple.

    Returns:
        Tuple of (os_name, machine_arch) — e.g. ('linux', 'x86_64').
    """
    os_name = sys.platform
    machine = platform.machine()
    return (os_name, machine)


def resolve_binary_name(os_name: str, machine: str) -> Optional[str]:
    """Resolve the correct merman-cli binary filename for the platform.

    Args:
        os_name: Operating system name (sys.platform value).
        machine: Machine architecture (platform.machine() value).

    Returns:
        Binary filename if supported, None otherwise.
    """
    return _PLATFORM_BINARY_MAP.get((os_name, machine))


def get_binary_path() -> Optional[Path]:
    """Find the bundled merman-cli binary for the current platform.

    Searches ``mdutil/export/_merman_binaries/`` relative to the package.

    Returns:
        Path to the binary, or None if not bundled / unsupported platform.
    """
    pkg_dir = Path(__file__).resolve().parent
    bin_dir = pkg_dir / "_merman_binaries"
    os_name, machine = detect_platform()
    binary_name = resolve_binary_name(os_name, machine)

    if binary_name is None:
        return None

    binary_path = bin_dir / binary_name
    return binary_path if binary_path.exists() else None


class MermanRenderer:
    """Wraps merman-cli binary to render Mermaid diagrams to SVG strings.

    Usage:
        renderer = MermanRenderer()
        svg = renderer.render_mermaid_svg("graph TD; A-->B;")

    If the binary is unavailable, render_mermaid_svg() raises
    MermanBinaryNotFoundError; callers should fall back to plain code blocks.
    """

    def __init__(self, timeout: int = RENDER_TIMEOUT):
        self._timeout = timeout
        self._binary_path: Optional[Path] = get_binary_path()

    @property
    def available(self) -> bool:
        """Return True if a merman-cli binary is available on this platform."""
        return self._binary_path is not None

    def render_mermaid_svg(self, mermaid_code: str, theme: str = "default") -> str:
        """Render Mermaid source code to an SVG string via merman-cli.

        Args:
            mermaid_code: Mermaid diagram source code.
            theme: Mermaid theme name (default, forest, dark, neutral).

        Returns:
            SVG string output by merman-cli.

        Raises:
            MermanBinaryNotFoundError: If no binary is bundled for this platform.
            MermanRenderError: If merman-cli exits with a non-zero status.
        """
        if self._binary_path is None:
            raise MermanBinaryNotFoundError(
                f"merman-cli binary not found for {sys.platform}/{platform.machine()}. "
                f"Supported: {list(_PLATFORM_BINARY_MAP.values())}"
            )

        if theme not in SUPPORTED_THEMES:
            raise MermanRenderError(
                f"Unsupported theme '{theme}'. Supported: {SUPPORTED_THEMES}"
            )

        cmd = [str(self._binary_path), "-t", theme, "-i", "-", "-o", "-"]
        try:
            result = subprocess.run(
                cmd,
                input=mermaid_code.encode("utf-8"),
                capture_output=True,
                timeout=self._timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise MermanRenderError(
                f"merman-cli timed out after {self._timeout}s"
            )
        except FileNotFoundError:
            raise MermanBinaryNotFoundError(
                f"merman-cli binary not found at {self._binary_path}"
            )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace").strip()
            raise MermanRenderError(
                f"merman-cli failed (exit {result.returncode}): {stderr}"
            )

        svg_output = result.stdout.decode("utf-8", errors="replace")
        return svg_output.strip()

    def render_diagrams(
        self, diagrams: list[tuple[str, int]], theme: str = "default"
    ) -> list[tuple[str, int, str]]:
        """Render multiple Mermaid diagrams at once.

        Args:
            diagrams: List of (mermaid_code, index) tuples.
            theme: Mermaid theme name.

        Returns:
            List of (mermaid_code, index, svg_string) tuples.
            Failed renders produce (mermaid_code, index, "<!-- render error -->")
        """
        results = []
        for code, idx in diagrams:
            try:
                svg = self.render_mermaid_svg(code, theme=theme)
                results.append((code, idx, svg))
            except (MermanBinaryNotFoundError, MermanRenderError) as e:
                results.append((code, idx, f"<!-- render error: {e} -->"))
        return results
