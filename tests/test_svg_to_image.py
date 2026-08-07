"""Unit tests for svg_to_image — shared SVG→PNG conversion layer."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mdutil.export.svg_to_image import (
    SvgToImageError,
    SvgToImageRenderer,
    _parse_dimension,
    extract_svg_height,
    extract_svg_width,
    get_renderer,
    get_svg_dimensions,
)


def _fake_png_bytes():
    """Create a minimal valid 1x1 RGBA PNG."""
    import struct, zlib
    raw = b'\x00' + b'\x00\x00\x00\x00'
    compressed = zlib.compress(raw)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data
    ihdr += struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed
    idat += struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
    return sig + ihdr + idat + iend


def _fake_merman_cli_with_png(tmp_path: Path) -> Path:
    """Create a fake merman-cli that writes a valid 1x1 PNG to the output dir.

    The fake finds the -o argument and writes a PNG file there.
    """
    fake_script = '''#!/usr/bin/env python3
import sys, os, struct, zlib

args = sys.argv[1:]
o_idx = args.index("-o")
out_dir = args[o_idx + 1]

raw = b'\\x00' + b'\\x00\\x00\\x00\\x00'
compressed = zlib.compress(raw)
sig = b'\\x89PNG\\r\\n\\x1a\\n'
ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data
ihdr += struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed
idat += struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
png = sig + ihdr + idat + iend

with open(os.path.join(out_dir, 'test.png'), 'wb') as f:
    f.write(png)
'''
    fake_bin = tmp_path / "merman-cli"
    fake_bin.write_text(fake_script)
    fake_bin.chmod(0o755)
    return fake_bin


# ---------------------------------------------------------------------------
# _parse_dimension
# ---------------------------------------------------------------------------

class TestParseDimension:
    """Tests for ``_parse_dimension()``."""

    def test_plain_number_returns_float(self):
        assert _parse_dimension("480") == 480.0

    def test_decimal_number(self):
        assert _parse_dimension("320.5") == 320.5

    def test_px_suffix(self):
        assert _parse_dimension("100px") == 100.0

    def test_pt_suffix_converted_to_px(self):
        assert _parse_dimension("72pt") == pytest.approx(96.0)

    def test_cm_suffix(self):
        result = _parse_dimension("5cm")
        assert result == pytest.approx(188.9764, rel=0.01)

    def test_mm_suffix(self):
        result = _parse_dimension("50mm")
        assert result == pytest.approx(188.9764, rel=0.01)

    def test_in_suffix(self):
        assert _parse_dimension("2in") == 192.0

    def test_percentage_returns_none(self):
        assert _parse_dimension("50%") is None

    def test_em_suffix(self):
        assert _parse_dimension("12em") == 12.0

    def test_empty_string(self):
        assert _parse_dimension("") is None

    def test_whitespace(self):
        assert _parse_dimension("  ") is None

    def test_unrecognized_unit_returns_none(self):
        # Unknown unit: returns None
        assert _parse_dimension("100xyz") is None


# ---------------------------------------------------------------------------
# get_svg_dimensions
# ---------------------------------------------------------------------------

class TestGetSvgDimensions:
    """Tests for ``get_svg_dimensions()``."""

    def test_explicit_width_height(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 480.0
        assert h == 320.0

    def test_width_height_with_px_suffix(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="480px" height="320px"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 480.0
        assert h == 320.0

    def test_width_height_with_pt_suffix(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="360pt" height="240pt"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == pytest.approx(480.0)
        assert h == pytest.approx(320.0)

    def test_percentage_width_raises_valueerror(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="320"><g></g></svg>'
        with pytest.raises(ValueError, match="percentage"):
            get_svg_dimensions(svg)

    def test_viewbox_fallback(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 320"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 480.0
        assert h == 320.0

    def test_only_width(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="480"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 480.0
        assert h == 0.0

    def test_only_height(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="320"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 0.0
        assert h == 320.0

    def test_empty_svg_raises_valueerror(self):
        with pytest.raises(ValueError, match="Empty SVG"):
            get_svg_dimensions("")

    def test_whitespace_svg_raises_valueerror(self):
        with pytest.raises(ValueError, match="Empty SVG"):
            get_svg_dimensions("   ")

    def test_no_dimensions_raises_valueerror(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><g></g></svg>'
        with pytest.raises(ValueError):
            get_svg_dimensions(svg)

    def test_width_and_height_swapped_attributes(self):
        """Width can appear after height in the tag."""
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="320" width="480"><g></g></svg>'
        w, h = get_svg_dimensions(svg)
        assert w == 480.0
        assert h == 320.0


# ---------------------------------------------------------------------------
# extract_svg_width / extract_svg_height
# ---------------------------------------------------------------------------

class TestExtractDimensions:
    """Tests for convenience extractors."""

    def test_extract_width(self):
        svg = '<svg width="480" height="320"><g></g></svg>'
        assert extract_svg_width(svg) == 480.0

    def test_extract_height(self):
        svg = '<svg width="480" height="320"><g></g></svg>'
        assert extract_svg_height(svg) == 320.0

    def test_extract_width_returns_none_on_error(self):
        assert extract_svg_width("") is None

    def test_extract_height_returns_none_on_error(self):
        assert extract_svg_height("") is None


# ---------------------------------------------------------------------------
# SvgToImageRenderer
# ---------------------------------------------------------------------------

class TestSvgToImageRenderer:
    """Tests for ``SvgToImageRenderer``."""

    def test_available_is_bool(self):
        renderer = SvgToImageRenderer()
        assert isinstance(renderer.available, bool)

    def test_unavailable_binary_raises_error(self):
        """Rendering without a binary raises MermanBinaryNotFoundError."""
        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = None
        renderer._timeout = 1

        from mdutil.export.merman_renderer import MermanBinaryNotFoundError
        with pytest.raises(MermanBinaryNotFoundError):
            renderer.render_mermaid_png("graph TD; A-->B;")

    def test_invalid_theme_raises_error(self, tmp_path):
        """Rendering with invalid theme raises MermanRenderError."""
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_bytes(b"#!/bin/sh")

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 1

        from mdutil.export.merman_renderer import MermanRenderError
        with pytest.raises(MermanRenderError, match="Unsupported theme"):
            renderer.render_mermaid_png("graph TD; A-->B;", theme="invalid_theme")

    def test_render_success(self, tmp_path):
        """Successful render produces PNG bytes."""
        fake_bin = _fake_merman_cli_with_png(tmp_path)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        result = renderer.render_mermaid_png("graph TD; A-->B;", theme="default")
        assert isinstance(result, bytes)
        assert result[:4] == b'\x89PNG'

    def test_render_handles_missing_output(self, tmp_path):
        """merman-cli that produces no output raises SvgToImageError."""
        fake_script = '#!/bin/sh\nexit 0'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        with pytest.raises(SvgToImageError, match="no output"):
            renderer.render_mermaid_png("graph TD; A-->B;")

    def test_render_handles_empty_output(self, tmp_path):
        """merman-cli that writes empty file raises SvgToImageError."""
        fake_script = '''#!/usr/bin/env python3
import sys, os
args = sys.argv[1:]
o_idx = args.index("-o")
open(os.path.join(args[o_idx + 1], "test.png"), "wb").close()
'''
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        with pytest.raises(SvgToImageError, match="empty"):
            renderer.render_mermaid_png("graph TD; A-->B;")

    def test_render_timeout(self, tmp_path):
        """Timeout raises MermanRenderError."""
        fake_script = '#!/bin/sh\nsleep 100'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 1

        from mdutil.export.merman_renderer import MermanRenderError
        with pytest.raises(MermanRenderError, match="timed out"):
            renderer.render_mermaid_png("graph TD; A-->B;")

    def test_render_diagrams_batch(self, tmp_path):
        """render_diagrams processes multiple diagrams, returning bytes or None."""
        fake_bin = _fake_merman_cli_with_png(tmp_path)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        diagrams = [
            ("graph TD; A-->B;", 0),
            ("graph TD; C-->D;", 1),
        ]
        results = renderer.render_diagrams_png(diagrams, theme="default")
        assert len(results) == 2
        assert results[0][0] is not None
        assert results[0][0][:4] == b'\x89PNG'
        assert results[1][0] is not None
        assert results[1][1] == 1

    def test_render_diagrams_handles_failures(self, tmp_path):
        """render_diagrams returns None for failed renders."""
        fake_script = '#!/bin/sh\nexit 1'
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text(fake_script)
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        diagrams = [("graph TD; A-->B;", 0)]
        results = renderer.render_diagrams_png(diagrams, theme="default")
        assert len(results) == 1
        assert results[0][0] is None
        assert results[0][1] == 0

    def test_render_passes_fit_width(self, tmp_path):
        """fit_width is passed as --rasterFitWidth to merman-cli."""
        captured = {}

        def capture_cmd(cmd, **kwargs):
            captured['cmd'] = cmd
            # Write PNG to the output dir from the -o arg
            o_idx = cmd.index("-o")
            out_dir = cmd[o_idx + 1]
            png = _fake_png_bytes()
            with open(os.path.join(out_dir, 'test.png'), 'wb') as f:
                f.write(png)
            result = MagicMock()
            result.returncode = 0
            result.stdout = b''
            result.stderr = b''
            return result

        import os
        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text("#!/bin/sh\necho ok")
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        with patch("subprocess.run", side_effect=capture_cmd):
            result = renderer.render_mermaid_png("graph TD; A-->B;", fit_width=800)
            assert isinstance(result, bytes)
            assert "--rasterFitWidth" in captured['cmd']
            assert "800" in captured['cmd']

    def test_render_passes_scale(self, tmp_path):
        """Custom scale is passed as --rasterScaleFactor."""
        captured = {}

        def capture_cmd(cmd, **kwargs):
            captured['cmd'] = cmd
            o_idx = cmd.index("-o")
            out_dir = cmd[o_idx + 1]
            png = _fake_png_bytes()
            with open(os.path.join(out_dir, 'test.png'), 'wb') as f:
                f.write(png)
            result = MagicMock()
            result.returncode = 0
            result.stdout = b''
            result.stderr = b''
            return result

        fake_bin = tmp_path / "merman-cli"
        fake_bin.write_text("#!/bin/sh\necho ok")
        fake_bin.chmod(0o755)

        renderer = SvgToImageRenderer.__new__(SvgToImageRenderer)
        renderer._binary_path = fake_bin
        renderer._timeout = 5

        with patch("subprocess.run", side_effect=capture_cmd):
            result = renderer.render_mermaid_png("graph TD; A-->B;", scale=3.0)
            assert isinstance(result, bytes)
            assert "--rasterScaleFactor" in captured['cmd']
            assert "3.0" in captured['cmd']


# ---------------------------------------------------------------------------
# get_renderer (singleton)
# ---------------------------------------------------------------------------

class TestGetRenderer:
    """Tests for ``get_renderer()`` singleton."""

    def test_returns_same_instance(self, monkeypatch):
        """Subsequent calls return the same instance."""
        monkeypatch.setattr("mdutil.export.svg_to_image._renderer", None)
        r1 = get_renderer()
        r2 = get_renderer()
        assert r1 is r2

    def test_returns_svg_to_image_renderer(self, monkeypatch):
        monkeypatch.setattr("mdutil.export.svg_to_image._renderer", None)
        renderer = get_renderer()
        assert isinstance(renderer, SvgToImageRenderer)
