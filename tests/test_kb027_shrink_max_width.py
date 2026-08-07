"""Tests for KB-027: Shrink mermaid diagram max-width by 40-50% in HTML export.

Verifies that _shrink_max_width_in_svg() correctly constrains the inline
max-width to a fraction of the diagram's natural viewBox width.
"""

from __future__ import annotations

import pytest

from mdutil.export.merman_renderer import _shrink_max_width_in_svg


class TestShrinkMaxWidth:
    """Tests for _shrink_max_width_in_svg()."""

    def test_shrinks_inline_max_width_to_50_percent(self):
        """Default factor 0.5 shrinks 864px diagram to 432px."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 864 435" '
            'style="max-width: 864px; overflow: visible;">'
            '<rect width="100" height="100"/>'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg)
        assert 'max-width: 432px' in result
        assert '864px' not in result or '864 435' in result  # viewBox stays intact
        assert '435' in result  # viewBox height stays intact

    def test_shrinks_inline_max_width_to_40_percent(self):
        """With factor=0.4, 481px diagram should be shrunk to 192px."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 481 508" '
            'style="max-width: 481px;">'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg, factor=0.4)
        assert 'max-width: 192px' in result

    def test_preserves_viewBox_coordinates(self):
        """viewBox should remain unchanged after shrinking max-width."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="10 20 252 668" '
            'style="max-width: 252px; overflow: visible;">'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg)
        assert 'viewBox="10 20 252 668"' in result
        assert 'max-width: 126px' in result

    def test_no_viewBox_falls_back_to_width_attr(self):
        """When viewBox is absent, fall back to explicit width attribute."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'width="500px" '
            'style="max-width: 500px;">'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg, factor=0.5)
        assert 'max-width: 250px' in result

    def test_no_dimensions_returns_unchanged(self):
        """SVG without viewBox or width should be returned unchanged."""
        svg = '<svg xmlns="http://www.w3.org/2000/svg" style="max-width: 100px;">'
        result = _shrink_max_width_in_svg(svg)
        assert result == svg

    def test_non_numeric_max_width_unchanged(self):
        """Non-numeric max-width value should be left untouched."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 300 200" '
            'style="max-width: auto;">'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg)
        # max-width:auto should not match numeric pattern, so should be unchanged
        assert 'max-width: auto' in result

    def test_empty_svg_returns_empty(self):
        """Empty SVG should be returned unchanged."""
        svg = ''
        result = _shrink_max_width_in_svg(svg)
        assert result == ''

    def test_default_factor_is_05(self):
        """Default factor of 0.5 should halve the width."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 1000 500" '
            'style="max-width: 1000px;">'
            '</svg>'
        )
        result = _shrink_max_width_in_svg(svg)
        assert 'max-width: 500px' in result

    def test_full_html_export_pipeline(self):
        """End-to-end: SVG with inline max-width gets shrunk by postprocess."""
        from mdutil.export.merman_renderer import _postprocess_svg

        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 864 435" '
            'style="max-width: 864px; overflow: visible;">'
            '<foreignObject width="100" height="50"></foreignObject>'
            '</svg>'
        )
        result = _postprocess_svg(svg)
        # Should have shrunk max-width to 432px (864 * 0.5)
        assert 'max-width: 432px' in result
        # foreignObject width should be widened by 15%
        assert 'width="115"' in result or 'width="115.' in result
