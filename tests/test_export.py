"""Tests for the mdutil export module (v3.0 Phase 1)."""

import unittest
from unittest.mock import MagicMock

from mdutil.export import Exporter
from mdutil.export.base import Exporter as BaseExporter
from mdutil.export.pdf import PdfExporter
from mdutil.export.html import HtmlExporter


class BaseExporterTests(unittest.TestCase):
    """Test the abstract Exporter base class."""

    def test_exporter_is_abstract(self):
        """Exporter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            Exporter()

    def test_exporter_is_abstract_class(self):
        """Exporter is the base class, not a concrete implementation."""
        self.assertTrue(issubclass(Exporter, BaseExporter))

    def test_subclass_must_implement_render(self):
        """A subclass that omits render() raises TypeError on instantiation."""

        class IncompleteExporter(Exporter):
            def supports(self, format: str) -> bool:
                return False

        with self.assertRaises(TypeError):
            IncompleteExporter()

    def test_subclass_must_implement_supports(self):
        """A subclass that omits supports() raises TypeError on instantiation."""

        class IncompleteExporter(Exporter):
            def render(self, tokens, theme, options):
                return b""

        with self.assertRaises(TypeError):
            IncompleteExporter()


class PdfExporterTests(unittest.TestCase):
    """Test PdfExporter functionality."""

    def setUp(self):
        self.exporter = PdfExporter()

    def test_supports_pdf(self):
        self.assertTrue(self.exporter.supports("pdf"))

    def test_does_not_support_html(self):
        self.assertFalse(self.exporter.supports("html"))

    def test_does_not_support_unknown_format(self):
        self.assertFalse(self.exporter.supports("txt"))
        self.assertFalse(self.exporter.supports(""))

    def test_render_returns_bytes(self):
        tokens = [{"type": "heading", "text": "Test"}]
        theme = {}
        options = {}

        result = self.exporter.render(tokens, theme, options)
        self.assertIsInstance(result, bytes)

    def test_render_returns_pdf_header_bytes(self):
        """Stub should return a valid PDF header to indicate PDF format."""
        result = self.exporter.render([], {}, {})
        self.assertTrue(result.startswith(b"%PDF"))

    def test_is_exporter_instance(self):
        """PdfExporter is a proper Exporter subclass."""
        self.assertIsInstance(self.exporter, Exporter)
        self.assertIsInstance(self.exporter, BaseExporter)


class HtmlExporterTests(unittest.TestCase):
    """Test HtmlExporter functionality."""

    def setUp(self):
        self.exporter = HtmlExporter()

    def test_supports_html(self):
        self.assertTrue(self.exporter.supports("html"))

    def test_does_not_support_pdf(self):
        self.assertFalse(self.exporter.supports("pdf"))

    def test_does_not_support_unknown_format(self):
        self.assertFalse(self.exporter.supports("txt"))
        self.assertFalse(self.exporter.supports(""))

    def test_render_returns_string(self):
        tokens = [{"type": "heading", "text": "Test"}]
        theme = {}
        options = {}

        result = self.exporter.render(tokens, theme, options)
        self.assertIsInstance(result, str)

    def test_render_returns_html_document(self):
        """Stub should return a minimal HTML document."""
        result = self.exporter.render([], {}, {})
        self.assertIn("<html>", result)
        self.assertIn("</html>", result)
        self.assertIn("<body>", result)
        self.assertIn("</body>", result)

    def test_is_exporter_instance(self):
        """HtmlExporter is a proper Exporter subclass."""
        self.assertIsInstance(self.exporter, Exporter)
        self.assertIsInstance(self.exporter, BaseExporter)


class PackageImportTests(unittest.TestCase):
    """Test package imports and re-exports."""

    def test_export_package_re_exports_exporter(self):
        """The export package re-exports the Exporter base class."""
        from mdutil import export

        self.assertEqual(export.Exporter, Exporter)

    def test_exporter_in_all(self):
        """Exporter is listed in __all__."""
        from mdutil.export import __all__

        self.assertIn("Exporter", __all__)


if __name__ == "__main__":
    unittest.main()
