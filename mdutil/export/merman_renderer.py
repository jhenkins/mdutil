"""MermanRenderer: Bundle infrastructure for offline Mermaid SVG rendering.

Bundles merman-cli binary for air-gapped Mermaid diagram rendering in HTML export.
Detects platform at runtime and invokes the appropriate pre-built binary.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Platform → generic merman-cli binary filename
# The build step (setup.py) copies the matching platform binary to this generic name.
_PLATFORM_BINARY_MAP = {
    ("linux", "x86_64"): "merman-cli",
    ("linux", "aarch64"): "merman-cli",
    ("darwin", "arm64"): "merman-cli",
    ("darwin", "x86_64"): "merman-cli",
    ("win32", "AMD64"): "merman-cli.exe",
    ("win32", "x86_64"): "merman-cli.exe",
}

# Default Mermaid themes supported by merman-cli
SUPPORTED_THEMES = ["default", "forest", "dark", "neutral"]

# Timeout for merman-cli subprocess (seconds)
RENDER_TIMEOUT = 30

# Padding factor for foreignObject widths to prevent text clipping.
# merman-cli measures text narrower than browsers render it, so we add padding.
_FOREIGN_OBJECT_PADDING_FACTOR = 1.15  # 15% extra width


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
    """Resolve the generic merman-cli binary filename for the platform.

    The build step (setup.py) copies the matching platform binary to a generic
    name (merman-cli or merman-cli.exe), so the runtime only needs to know the
    generic name — not the platform-specific source name.

    Args:
        os_name: Operating system name (sys.platform value).
        machine: Machine architecture (platform.machine() value).

    Returns:
        Generic binary filename if supported, None otherwise.
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
        svg_output = svg_output.strip()
        svg_output = _postprocess_svg(svg_output)
        return svg_output

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


def _shrink_max_width_in_svg(svg: str, factor: float = 0.3) -> str:
    """Shrink the inline ``max-width`` on the root <svg> element.

    Replaces the existing ``max-width`` value with ``factor`` times the
    diagram's natural viewBox width.  This constrains the rendered size
    of the diagram without affecting the viewBox coordinates themselves.

    Args:
        svg: SVG string from merman-cli (or any SVG with an inline
             ``style="max-width: ...px"`` on the root element).
        factor: Shrink factor applied to the natural width.  0.3 shrinks
                by 70 % (diagram renders at 30 % of natural width).

    Returns:
        Modified SVG string.
    """
    # Extract the natural width from viewBox="x y w h"
    vb_match = re.search(
        r'<svg[^>]*\bviewBox="[^"]*\s+([\d.]+)\s+([\d.]+)"',
        svg, re.IGNORECASE | re.DOTALL,
    )
    natural_width: Optional[float]
    if vb_match:
        natural_width = float(vb_match.group(1))
    else:
        # Fallback: try explicit width attribute (numeric px value)
        w_match = re.search(
            r'<svg[^>]*\bwidth="([\d.]+)\s*(?:px|)"',
            svg, re.IGNORECASE | re.DOTALL,
        )
        if w_match:
            try:
                natural_width = float(w_match.group(1))
            except ValueError:
                return svg  # non-numeric width, leave untouched
        else:
            return svg  # no dimension info — leave untouched

    constrained_width = natural_width * factor

    # Now find the inline style on the root <svg> element and replace
    # the max-width value.
    # Match: <svg ... style="...max-width: <val>px..." ...>
    pattern = re.compile(
        r'(<svg\s[^>]*style="[^"]*?)'
        r'max-width\s*:\s*([\d.]+)\s*(?:px)?'
        r'([^"]*")'
        r'(>)',
        re.IGNORECASE,
    )

    def _replace(match: re.Match) -> str:
        before = match.group(1)
        old_val = match.group(2)
        after = match.group(3)
        closing = match.group(4)
        # Check that the old value was a numeric px value we can replace
        try:
            float(old_val)
        except ValueError:
            return match.group(0)  # not a numeric value, leave it
        # Build the new style: replace max-width value
        before_stripped = before.rstrip()
        combined = before_stripped + f'max-width: {constrained_width:.0f}px' + after
        # Clean up: remove leftover separator (e.g. "; ") around the replaced value
        combined = re.sub(r'\s*;\s*max-width', ' max-width', combined)
        combined = re.sub(r'max-width\s*;\s*', 'max-width:', combined)
        # Collapse multiple spaces
        combined = re.sub(r'  +', ' ', combined)
        # If style attribute is empty (only whitespace left), remove it
        style_empty = re.search(r'style="\s*"', combined)
        if style_empty:
            combined = combined[: style_empty.start()] + combined[style_empty.end():]
            combined = re.sub(r'\s+>', '>', combined)
        return combined + closing

    return pattern.sub(_replace, svg)


def _postprocess_svg(svg: str) -> str:
    """Post-process merman-cli SVG output to fix rendering issues.

    Fixes applied:
    1. Shrink inline ``max-width`` on the root <svg> element to 30 % of
       the diagram's natural viewBox width so the diagram renders at 30 %
       of its natural width in the document layout.
    2. Widen ``<foreignObject>`` widths for node/cluster labels so text
       produced by the browser does not get clipped by the foreignObject
       bounds (merman-cli measures text narrower than browsers render it).
    """
    if not svg.strip():
        return svg

    # 1. Shrink inline ``max-width`` on the root <svg> element to 30 % of
    #    the diagram's natural viewBox width.  The inline value beats the
    #    CSS ``.mermaid svg { max-width: 100%; }`` rule so the diagram
    #    renders at 30 % of its natural width, preventing oversized diagrams
    #    from dominating the document layout.
    svg = _shrink_max_width_in_svg(svg, factor=0.3)

    # 2. Widen foreignObject widths for node/cluster label content.
    #    We target foreignObjects inside .label groups (node labels) but
    #    skip edge labels (which have width="0" and are intentionally empty).
    def _widen_foreign_object(match: re.Match) -> str:
        full = match.group(0)
        w_match = re.search(r'width="([^"]+)"', full)
        if not w_match:
            return full
        width_str = w_match.group(1)
        try:
            width_val = float(width_str)
        except ValueError:
            return full
        # Skip zero-width foreignObjects (edge labels)
        if width_val <= 0:
            return full
        new_width = width_val * _FOREIGN_OBJECT_PADDING_FACTOR
        return full.replace(f'width="{width_str}"', f'width="{new_width:.4f}"')

    svg = re.sub(r'<foreignObject[^>]*>', _widen_foreign_object, svg)

    return svg
