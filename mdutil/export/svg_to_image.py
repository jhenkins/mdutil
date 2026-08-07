"""Shared SVG → PNG conversion layer for mdutil export.

Wraps merman-cli's native ``--outputFormat png`` capability to produce PNG bytes
directly from Mermaid source code. This module centralizes image rendering logic
shared between PDF and HTML exporters.

Why merman-cli PNG instead of cairosvg?
---------------------------------------
- merman-cli uses Chromium for rendering, producing identical output to HTML export.
- No system dependency on ``libcairo.so.2``.
- Full theme passthrough (default, forest, dark, neutral).
- Bundled binary enables air-gapped operation.

Design decisions
----------------
- **No cairosvg dependency.** merman-cli supports ``--outputFormat png`` natively.
- **Scale factor:** 2.0 for HiDPI output. fpdf2 can scale back down to fit the page.
- **Fit width:** PDF exporter passes available page width to keep diagrams fitting.
- **Timeout:** 30s per render (matches MermanRenderer.RENDER_TIMEOUT).
"""

from __future__ import annotations

import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from mdutil.export.merman_renderer import (
    MermanBinaryNotFoundError,
    MermanRenderError,
    RENDER_TIMEOUT,
    SUPPORTED_THEMES,
    get_binary_path,
    resolve_binary_name,
)


# Default raster scale for HiDPI PNG output
_DEFAULT_SCALE = 2.0

# Default background for PNG rendering
_DEFAULT_BACKGROUND = "transparent"


class SvgToImageError(RuntimeError):
    """Raised when SVG-to-PNG conversion fails."""


def _get_svg_to_image_binary() -> Optional[Path]:
    """Locate the merman-cli binary for svg_to_image operations.

    Returns:
        Path to the merman-cli binary, or None if unavailable.
    """
    return get_binary_path()


class SvgToImageRenderer:
    """Wraps merman-cli to render Mermaid diagrams to PNG bytes.

    Usage:
        renderer = SvgToImageRenderer()
        png_bytes = renderer.render_mermaid_png("graph TD; A-->B;")

    If the binary is unavailable, ``render_mermaid_png()`` raises
    ``MermanBinaryNotFoundError``.
    """

    def __init__(self, timeout: int = RENDER_TIMEOUT):
        self._timeout = timeout
        self._binary_path: Optional[Path] = _get_svg_to_image_binary()

    @property
    def available(self) -> bool:
        """Return True if a merman-cli binary is available on this platform."""
        return self._binary_path is not None

    def render_mermaid_png(
        self,
        mermaid_code: str,
        *,
        theme: str = "default",
        background: str = _DEFAULT_BACKGROUND,
        scale: float = _DEFAULT_SCALE,
        fit_width: Optional[float] = None,
    ) -> bytes:
        """Render Mermaid source code to PNG bytes via merman-cli.

        Uses merman-cli's native ``--outputFormat png`` option for direct
        SVG→PNG conversion with Chromium rendering.

        Args:
            mermaid_code: Mermaid diagram source code.
            theme: Mermaid theme name (default, forest, dark, neutral).
            background: Background color hex (default ``transparent``).
            scale: Raster scale factor. 2.0 produces HiDPI PNGs.
            fit_width: CSS-pixel width to fit the diagram to before scaling.

        Returns:
            PNG byte array.

        Raises:
            MermanBinaryNotFoundError: If no binary is bundled for this platform.
            MermanRenderError: If merman-cli exits with a non-zero status.
            SvgToImageError: If the conversion produces unexpected output.
        """
        if self._binary_path is None:
            raise MermanBinaryNotFoundError(
                f"merman-cli binary not found for {sys.platform}/{platform.machine()}. "
                f"Supported: {list(set(resolve_binary_name(o, m) for o, m in [
                    ('linux', 'x86_64'), ('linux', 'aarch64'),
                    ('darwin', 'arm64'), ('darwin', 'x86_64'),
                    ('win32', 'AMD64'), ('win32', 'x86_64'),
                ]))}"
            )

        if theme not in SUPPORTED_THEMES:
            raise MermanRenderError(
                f"Unsupported theme '{theme}'. Supported: {SUPPORTED_THEMES}"
            )

        # Build merman-cli command for PNG output.
        # merman-cli supports: --outputFormat png, --outputDir, --outputName,
        # and for raster options: --rasterScaleFactor, --rasterFitWidth,
        # --rasterBackground (hex color or transparent).
        cmd = [
            str(self._binary_path),
            "-t", theme,
            "--outputFormat", "png",
            "-i", "-",
        ]

        if fit_width is not None:
            cmd.extend(["--rasterFitWidth", str(int(fit_width))])

        if scale != _DEFAULT_SCALE:
            cmd.extend(["--rasterScaleFactor", str(scale)])

        if background and background != _DEFAULT_BACKGROUND:
            cmd.extend(["--rasterBackground", background])

        # merman-cli requires -o to be a file path (not a directory).
        # We write to a temp file and read it back.
        with tempfile.TemporaryDirectory(prefix="mdutil_svg2png_") as tmpdir:
            output_file = Path(tmpdir) / "output.png"
            cmd.extend(["-o", str(output_file)])

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

            if not output_file.exists():
                raise SvgToImageError(
                    f"merman-cli produced no output file at {output_file}"
                )

            png_data = output_file.read_bytes()
            if not png_data:
                raise SvgToImageError("merman-cli produced empty PNG output")

            return png_data

    def render_diagrams_png(
        self,
        diagrams: list[tuple[str, int]],
        *,
        theme: str = "default",
        background: str = _DEFAULT_BACKGROUND,
        scale: float = _DEFAULT_SCALE,
        fit_width: Optional[float] = None,
    ) -> list[tuple[bytes | None, int]]:
        """Render multiple Mermaid diagrams to PNG bytes.

        Args:
            diagrams: List of (mermaid_code, index) tuples.
            theme: Mermaid theme name.
            background: Background color hex.
            scale: Raster scale factor.
            fit_width: CSS-pixel width to fit the diagram to.

        Returns:
            List of (png_bytes_or_None, index) tuples.
            Failed renders produce (None, index).
        """
        results: list[tuple[Optional[bytes], int]] = []
        for code, idx in diagrams:
            try:
                png = self.render_mermaid_png(
                    code, theme=theme, background=background,
                    scale=scale, fit_width=fit_width,
                )
                results.append((png, idx))
            except (
                MermanBinaryNotFoundError,
                MermanRenderError,
                SvgToImageError,
            ):
                results.append((None, idx))
        return results


def get_svg_dimensions(svg: str) -> Tuple[float, float]:
    """Extract width and height (in px or pt) from an SVG string.

    Parses the root ``<svg>`` element's ``width`` and ``height`` attributes.
    Falls back to ``viewBox`` dimensions when explicit dimensions are absent.

    Args:
        svg: SVG string.

    Returns:
        Tuple of (width, height) in pixels/points.

    Raises:
        ValueError: If the SVG cannot be parsed for dimensions.
    """
    svg = svg.strip()
    if not svg:
        raise ValueError("Empty SVG string")

    # Try explicit width/height attributes first (numeric or percentage)
    dim_match = re.search(
        r'<svg[^>]*\bwidth="([^"]+)"[^>]*\bheight="([^"]+)"',
        svg, re.IGNORECASE | re.DOTALL,
    )
    if dim_match:
        w = _parse_dimension(dim_match.group(1))
        h = _parse_dimension(dim_match.group(2))
        if w is not None and h is not None:
            return (w, h)

    # Fallback: width or height individually
    w_match = re.search(r'<svg[^>]*\bwidth="([^"]+)"', svg, re.IGNORECASE | re.DOTALL)
    h_match = re.search(r'<svg[^>]*\bheight="([^"]+)"', svg, re.IGNORECASE | re.DOTALL)
    if w_match or h_match:
        w = _parse_dimension(w_match.group(1)) if w_match else None
        h = _parse_dimension(h_match.group(1)) if h_match else None
        # Percentages are not extractable as pixel dimensions
        if w is None and w_match:
            raise ValueError(
                f"SVG dimension is a percentage value, cannot extract pixels: "
                f"width={_dim_attr_value(w_match)}"
            )
        if h is None and h_match:
            raise ValueError(
                f"SVG dimension is a percentage value, cannot extract pixels: "
                f"height={_dim_attr_value(h_match)}"
            )
        if w is not None and h is not None:
            return (w, h)
        if w is not None:
            return (w, 0.0)
        if h is not None:
            return (0.0, h)

    # Fallback: viewBox="minX minY width height"
    vb_match = re.search(
        r'<svg[^>]*\bviewBox="[^"]*\s+([\d.]+)\s+([\d.]+)"',
        svg, re.IGNORECASE | re.DOTALL,
    )
    if vb_match:
        return (float(vb_match.group(1)), float(vb_match.group(2)))

    raise ValueError(f"Cannot extract dimensions from SVG: {svg[:80]}...")


def _dim_attr_value(match) -> str:
    """Return the raw attribute value from a width/height regex match."""
    if match is None:
        return "N/A"
    return match.group(1) or "N/A"


def _parse_dimension(value: str) -> Optional[float]:
    """Parse an SVG dimension value (number, number+unit, or percentage).

    Supports: numeric (px assumed), px, pt, em, %, vw, vh.
    Returns None for percentage values (caller must resolve against container).

    Args:
        value: Dimension string from SVG attribute.

    Returns:
        Numeric width/height, or None for percentage values.
    """
    value = value.strip()
    if not value:
        return None

    # Pure number (assumed px)
    if re.match(r'^[\d.]+$', value):
        return float(value)

    # Number with unit
    match = re.match(r'^([\d.]+)\s*(px|pt|em|vw|vh|cm|mm|in)?$', value, re.IGNORECASE)
    if match:
        num = float(match.group(1))
        unit = (match.group(2) or "px").lower()
        if unit == "px":
            return num
        elif unit == "pt":
            return num * (4 / 3)  # 1pt = 4/3px
        elif unit == "cm":
            return num * 37.795275591  # 1cm ≈ 37.8px
        elif unit == "mm":
            return num * 3.7795275591
        elif unit == "in":
            return num * 96.0  # 1in = 96px
        elif unit in ("em", "vw", "vh"):
            return num  # Relative; caller handles context
        return num

    # Percentage
    if value.endswith("%"):
        return None  # Callers must resolve against container width

    return None


def extract_svg_width(svg: str) -> Optional[float]:
    """Extract just the width from an SVG string.

    Convenience wrapper around ``get_svg_dimensions()`` that returns only width.

    Args:
        svg: SVG string.

    Returns:
        Width in pixels, or None if extraction fails.
    """
    try:
        w, _ = get_svg_dimensions(svg)
        return w
    except (ValueError, TypeError):
        return None


def extract_svg_height(svg: str) -> Optional[float]:
    """Extract just the height from an SVG string.

    Convenience wrapper around ``get_svg_dimensions()`` that returns only height.

    Args:
        svg: SVG string.

    Returns:
        Height in pixels, or None if extraction fails.
    """
    try:
        _, h = get_svg_dimensions(svg)
        return h
    except (ValueError, TypeError):
        return None


# Module-level convenience instance
_renderer: Optional[SvgToImageRenderer] = None


def get_renderer() -> SvgToImageRenderer:
    """Return a lazily-created SvgToImageRenderer instance.

    Caches the instance so multiple render calls don't re-discover the binary.
    """
    global _renderer
    if _renderer is None:
        _renderer = SvgToImageRenderer()
    return _renderer
