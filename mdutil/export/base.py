"""Base exporter interface for v3.0 export functionality."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union


class Exporter(ABC):
    """Abstract base class for all exporters.

    Subclasses implement export to specific formats (PDF, HTML, etc.).
    """

    @abstractmethod
    def render(self, tokens: list, theme: dict, options: dict) -> Union[str, bytes]:
        """Render tokens to the target format.

        Args:
            tokens: Parsed markdown tokens
            theme: Current theme configuration
            options: Export-specific options

        Returns:
            Rendered content as string (HTML) or bytes (PDF)
        """
        ...

    @abstractmethod
    def supports(self, format: str) -> bool:
        """Check if this exporter supports the given format.

        Args:
            format: Format string (e.g., 'pdf', 'html')

        Returns:
            True if format is supported
        """
        ...
