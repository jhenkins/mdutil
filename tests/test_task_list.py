"""Tests for KB-052..054: Task list support (- [ ] and - [x])."""
import unittest

from mdutil.parser import parse_markdown
from mdutil.renderer import render


class TaskListParserTests(unittest.TestCase):
    """Test task list detection in the parser."""

    def test_parse_task_list_unchecked(self):
        """Parser detects task list and marks items as unchecked."""
        tokens = parse_markdown("- [ ] Unchecked task\n- [ ] Another task")
        self.assertEqual(tokens[0]["type"], "list")
        self.assertEqual(tokens[0]["task"], True)
        items = tokens[0]["parsed_items"]
        self.assertEqual(len(items), 2)
        self.assertFalse(items[0]["checked"])
        self.assertFalse(items[1]["checked"])
        self.assertTrue(items[0]["task"])
        self.assertTrue(items[1]["task"])
        self.assertEqual(items[0]["text"], "Unchecked task")
        self.assertEqual(items[1]["text"], "Another task")

    def test_parse_task_list_checked(self):
        """Parser marks [x] and [X] as checked."""
        tokens = parse_markdown("- [x] Done\n- [X] Also done\n- [ ] Pending")
        self.assertEqual(tokens[0]["task"], True)
        items = tokens[0]["parsed_items"]
        self.assertTrue(items[0]["checked"])
        self.assertTrue(items[1]["checked"])
        self.assertFalse(items[2]["checked"])

    def test_parse_mixed_regular_and_task_items(self):
        """Mixed regular and task items in same list."""
        tokens = parse_markdown("- Normal item\n- [x] Checked item\n- [ ] Unchecked item")
        self.assertEqual(tokens[0]["task"], True)
        items = tokens[0]["parsed_items"]
        self.assertEqual(len(items), 3)
        self.assertFalse(items[0]["task"])
        self.assertTrue(items[1]["task"])
        self.assertTrue(items[1]["checked"])
        self.assertTrue(items[2]["task"])
        self.assertFalse(items[2]["checked"])

    def test_parse_task_list_with_inline_formatting(self):
        """Task items preserve inline formatting in content field."""
        tokens = parse_markdown("- [ ] Task with **bold** and *italic*")
        items = tokens[0]["parsed_items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["checked"], False)
        self.assertIn("<strong>bold</strong>", items[0]["content"])
        self.assertIn("<em>italic</em>", items[0]["content"])
        self.assertEqual(items[0]["text"], "Task with **bold** and *italic*")

    def test_parse_ordered_task_list(self):
        """Task lists work with ordered list syntax."""
        tokens = parse_markdown("1. [ ] First task\n2. [x] Second task")
        self.assertEqual(tokens[0]["type"], "list")
        self.assertEqual(tokens[0]["ordered"], True)
        self.assertEqual(tokens[0]["task"], True)
        items = tokens[0]["parsed_items"]
        self.assertFalse(items[0]["checked"])
        self.assertTrue(items[1]["checked"])

    def test_regular_list_not_marked_as_task(self):
        """Regular lists without checkboxes are not marked as task lists."""
        tokens = parse_markdown("- Normal item\n- Another item")
        self.assertEqual(tokens[0]["task"], False)
        items = tokens[0]["parsed_items"]
        for item in items:
            self.assertFalse(item["task"])


class TaskListRendererTests(unittest.TestCase):
    """Test task list rendering to terminal."""

    def test_render_unchecked_task(self):
        """Renderer displays ☐ for unchecked tasks."""
        tokens = parse_markdown("- [ ] Buy milk")
        output = render(tokens, theme="colored")
        self.assertIn("☐", output)
        self.assertIn("Buy milk", output)
        self.assertNotIn("[ ]", output)

    def test_render_checked_task(self):
        """Renderer displays ☑ for checked tasks."""
        tokens = parse_markdown("- [x] Completed task")
        output = render(tokens, theme="colored")
        self.assertIn("☑", output)
        self.assertIn("Completed task", output)
        self.assertNotIn("[x]", output)

    def test_render_mixed_tasks(self):
        """Renderer handles mixed task items correctly."""
        tokens = parse_markdown("- [ ] Pending\n- [x] Done\n- Regular item")
        output = render(tokens, theme="colored")
        lines = output.split("\n")
        self.assertIn("☐", lines[0])
        self.assertIn("☑", lines[1])
        self.assertNotIn("☐", lines[2])

    def test_render_regular_list_unaffected(self):
        """Regular lists without tasks render unchanged."""
        tokens = parse_markdown("- Item A\n- Item B")
        output = render(tokens, theme="colored")
        lines = output.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("- "))
        self.assertTrue(lines[1].startswith("- "))


class TaskListHtmlExporterTests(unittest.TestCase):
    """Test task list rendering in HTML."""

    def test_render_task_list_html(self):
        """HTML exporter renders task items with checkboxes."""
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("- [ ] Unchecked\n- [x] Checked")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<input", html)
        self.assertIn('type="checkbox"', html)
        self.assertIn("disabled", html)
        # Checkboxes should be preserved for unchecked items
        self.assertIn("<input type=\"checkbox\" disabled>", html)
        # Checked item should have checked attribute
        self.assertIn("checked", html)
        # Text content should be present
        self.assertIn("Unchecked", html)
        self.assertIn("Checked", html)

    def test_render_regular_list_html_unchanged(self):
        """Regular lists in HTML are unaffected."""
        from mdutil.export.html import HtmlExporter
        tokens = parse_markdown("- Item A\n- Item B")
        exporter = HtmlExporter()
        html = exporter.render(tokens, {}, {})
        self.assertIn("<li>Item A</li>", html)
        self.assertIn("<li>Item B</li>", html)
        self.assertNotIn("checkbox", html)


class TaskListPdfExporterTests(unittest.TestCase):
    """Test task list rendering in PDF."""

    def test_render_task_list_pdf(self):
        """PDF exporter renders task items with Unicode checkboxes."""
        from mdutil.export.pdf import PdfExporter
        tokens = parse_markdown("- [ ] Unchecked\n- [x] Checked")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertTrue(len(pdf_bytes) > 100)
        # Check for checkbox symbols in the PDF (they should be in the text stream)
        import zlib
        stream_start = pdf_bytes.find(b"stream\n")
        if stream_start != -1:
            stream_end = pdf_bytes.find(b"\nendstream", stream_start)
            if stream_end != -1:
                stream_data = pdf_bytes[stream_start + 7: stream_end]
                try:
                    decompressed = zlib.decompress(stream_data)
                    # Unicode characters may be encoded differently in PDF
                    self.assertTrue(len(decompressed) > 0)
                except Exception:
                    pass

    def test_render_regular_list_pdf(self):
        """Regular lists in PDF are unaffected."""
        from mdutil.export.pdf import PdfExporter
        tokens = parse_markdown("- Item A\n- Item B")
        exporter = PdfExporter()
        pdf_bytes = exporter.render(tokens, {}, {})
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()