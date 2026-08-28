# KB-060: Exporter Footnote Rendering (HTML & PDF)

**Status:** ✅ Complete  
**Date:** 2026-08-18  
**Branch:** `feature/v5.0-rendering`

---

## Overview

Implemented footnote reference and definition rendering in the HTML and PDF exporters (KB-060). Completes Phase 2a of the v5.0 rendering plan (parser: KB-057/058, renderer: KB-059, exporters: KB-060).

---

## Implementation Details

### HTML Exporter (`mdutil/export/html.py`)

#### 1. Footnote Reference Rendering
- **Input:** `<fnref id="N">` tags in paragraph `content` field
- **Output:** `<sup><a href="#fn-N" id="fnref-N">N</a></sup>`
- **Implementation:** `_process_fnref_tags()` regex substitution in `_render_paragraph()`
- **Also:** `footnote_ref` span type handled in `_render_spans()` for fallback rendering

#### 2. Footnote Definition Rendering
- **Token Type:** `footnote_definition`
- **Output:** `<div class="footnotes"><ol><li id="fn-N"><a href="#fnref-N">↩</a> content</li></ol></div>`
- **Implementation:** New `_render_footnote_definition()` method
- **Integration:** Added to `_render_tokens()` dispatch

#### 3. CSS
- `.footnotes` — bordered top, muted color, smaller font
- `.footnotes a` — link-colored back-reference arrows

### PDF Exporter (`mdutil/export/pdf.py`)

#### 1. Footnote Reference Rendering
- **Input:** `<fnref id="N">` tags in paragraph/list content
- **Output:** Unicode superscript characters via `_superscript()` helper
- **Implementation:** Pre-process content with regex before `_render_inline_html()` / list rendering

#### 2. Footnote Definition Rendering
- **Token Type:** `footnote_definition`
- **Output:** Horizontal rule separator + indented text with superscript prefix
- **Implementation:** New `_render_footnote_definition()` method
- **Superscript helper:** `_superscript()` static method (reuses renderer mapping)

---

## Token Structure (from KB-057)

### Footnote Definition Token
```python
{
    "type": "footnote_definition",
    "id": "1",
    "content": "This is the footnote content.",
    "text": "This is the footnote content.",
}
```

### Footnote Reference Span
```python
{
    "type": "footnote_ref",
    "id": "1"
}
```

---

## HTML Output Example

**Input:**
```markdown
Text with a footnote[^1] and another[^2].

[^1]: This is the **first** footnote.
[^2]: This is the second footnote.
```

**HTML Output:**
```html
<p>Text with a footnote<sup><a href="#fn-1" id="fnref-1">1</a></sup> and another<sup><a href="#fn-2" id="fnref-2">2</a></sup>.</p>

<div class="footnotes">
<ol>
<li id="fn-1"><a href="#fnref-1">↩</a> This is the <strong>first</strong> footnote.</li>
<li id="fn-2"><a href="#fnref-2">↩</a> This is the second footnote.</li>
</ol>
</div>
```

---

## PDF Output Example

**Input:**
```markdown
Text with a footnote[^1].

[^1]: This is the footnote.
```

**PDF Rendering:**
```
Text with a footnote¹.

──────────────────────────────────
    ¹  This is the footnote.
```

(Superscript ¹ rendered via Unicode CID font glyph)

---

## Test Coverage

**File:** `tests/test_footnote_exporter.py`  
**Tests:** 12 passing

### HTML Exporter Tests (6)
- ✅ Footnote reference rendered as superscript anchor link
- ✅ Footnote definition rendered in `.footnotes` div
- ✅ Multiple footnote references and definitions
- ✅ Back-reference arrow link (↩) in footnote definition
- ✅ CSS classes included (`.footnotes`)
- ✅ Inline formatting preserved (bold, italic)

### PDF Exporter Tests (6)
- ✅ Footnote reference renders as Unicode superscript (¹)
- ✅ Footnote definition renders with superscript prefix
- ✅ Multiple footnotes produce different superscript CID codes
- ✅ `_superscript()` single-digit conversion
- ✅ `_superscript()` multi-digit conversion
- ✅ Footnote reference in list item renders as superscript

---

## Design Decisions

### 1. Bidirectional Anchor Links (HTML)
**Decision:** Footnote references link to `#fn-N` and footnote definitions link back via `↩` to `#fnref-N`.

**Rationale:** Standard web convention for footnotes; allows readers to jump back and forth.

### 2. CID Font Encoding (PDF)
**Decision:** Use Unicode superscript characters encoded as CID font glyphs.

**Rationale:** fpdf2 with CID/Identity-H fonts maps superscript codepoints to embedded DejaVu glyphs. The bfchar CMap handles the CID→Unicode mapping.

### 3. Superscript Helper Shared with Renderer
**Decision:** `_superscript()` is a `@staticmethod` on `PdfExporter`, duplicating the renderer's logic.

**Rationale:** Keeps the PDF exporter self-contained; the mapping is simple and unlikely to change.

### 4. Horizontal Rule Separator (PDF)
**Decision:** Draw a thin horizontal line above the footnote section in PDF.

**Rationale:** Visual separation between main content and footnotes, matching CommonMark conventions.

---

## Files Modified

- `mdutil/export/html.py` (added `_process_fnref_tags`, `_render_footnote_definition`, CSS, span handling)
- `mdutil/export/pdf.py` (added `_superscript`, `_render_footnote_definition`, `_render_footnote_ref`, paragraph/list preprocessing)
- `tests/test_footnote_exporter.py` (new file, 12 tests)

---

## Integration Summary — Phase 2a Complete

| Component | KB | Status |
|-----------|-----|--------|
| Parser: footnote definitions | KB-057 | ✅ Done |
| Parser: footnote references | KB-058 | ✅ Done |
| Renderer: footnote display | KB-059 | ✅ Done |
| **Exporter: HTML/PDF footnotes** | **KB-060** | **✅ Done** |

Phase 2a is complete. Next: KB-061 (Phase 2b: subscript/superscript syntax).

---

## Test Results

```
453 passed, 25 subtests passed in 46.36s
```

**New tests:** 12 (in `test_footnote_exporter.py`)  
**Total tests:** 453 (441 previous + 12 new)

---

*Implementation completed 2026-08-18 by AI Agent.*
