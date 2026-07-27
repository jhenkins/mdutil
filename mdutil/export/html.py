"""HTML exporter for mdutil v3.0."""

from __future__ import annotations

from typing import Union

from mdutil.export.base import Exporter


class HtmlExporter(Exporter):
    """Export Markdown to HTML with embedded CSS."""

    def render(self, tokens: list, theme: dict, options: dict) -> str:
        """Render tokens to HTML format.

        Args:
            tokens: Parsed markdown tokens
            theme: Current theme configuration
            options: Export-specific options

        Returns:
            Rendered HTML as string
        """
        # TODO: Phase 3 - implement full HTML rendering
        return "<html><body><!-- TODO: implement HTML export --></body></html>"

    def supports(self, format: str) -> bool:
        """Check if this exporter supports the given format.

        Args:
            format: Format string (e.g., 'html')

        Returns:
            True if format is supported
        """
        return format == "html"
