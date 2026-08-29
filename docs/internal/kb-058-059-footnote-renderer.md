# KB-058 & KB-059: Footnote Reference Display in Renderer

**Status:** ✅ Complete  
**Date:** 2026-08-18  
**Branch:** `feature/v5.0-rendering`

---

## Overview

Implemented footnote reference and definition display in the ANSI terminal renderer (KB-058, KB-059).

## Implementation Details

### KB-058: Parser Footnote References
**Status:** Completed as part of KB-057

The inline footnote reference detection (`[^1]` → `<fnref id="1">`) was implemented in the parser during KB-057. The renderer now consumes these tags.

### KB-059: Renderer Footnotes Display

#### 1. Footnote Reference Rendering
- **Input:** `<fnref id="n">` tags in parsed content
- **Output:** Unicode superscript characters (¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹)
- **Implementation:** Lambda function in `_strip_inline_tags()` that converts footnote refs to styled superscript

#### 2. Footnote Definition Rendering
- **Token Type:** `footnote_definition`
- **Output:** Indented text with superscript prefix (e.g., `    ¹  Footnote text...`)
- **Implementation:** New `_render_footnote_definition()` function

#### 3. Superscript Conversion
- **Function:** `_superscript(n: str) -> str`
- **Mapping:** Converts digit strings to Unicode superscript characters
  - `1` → `¹` (U+00B9)
  - `2` → `²` (U+00B2)
  - `3` → `³` (U+00B3)
  - `10` → `¹⁰`
  - `123` → `¹²³`

---

## Renderer Changes (`mdutil/renderer.py`)

### New Function: `_superscript()`
```python
def _superscript(n: str) -> str:
    """Convert a number string to Unicode superscript characters."""
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    }
    return "".join(superscript_map.get(c, c) for c in n)
```

### New Function: `_render_footnote_definition()`
```python
def _render_footnote_definition(token: dict[str, Any], theme: dict[str, Any]) -> list[str]:
    """Render a footnote definition token as indented text."""
    fn_id = token.get("id", "")
    content = token.get("content", "")
    # Strip inline tags for terminal display
    text = _strip_inline_tags(content, theme)
    # Format as "    ¹  Footnote text..." with indentation
    superscript = _superscript(fn_id)
    rendered = f"    {superscript}  {text}"
    return [rendered]
```

### Updated Function: `_strip_inline_tags()`
Added footnote reference rendering:
```python
text = re.sub(
    r"<fnref\s+id=\"(\d+)\">",
    lambda m: _style(_superscript(m.group(1)), theme or {}, "footnote_ref"),
    text,
)
```

### Updated Function: `_render_token()`
Added `footnote_definition` token handling:
```python
if ttype == "footnote_definition":
    return _render_footnote_definition(token, theme)
```

---

## Test Coverage

**File:** `tests/test_footnote_renderer.py`  
**Tests:** 14 passing

### Renderer Tests
- ✅ Footnote reference rendered as superscript (¹ ² ³)
- ✅ Multiple footnote references
- ✅ Footnote reference with surrounding text
- ✅ Footnote definition rendered with indentation
- ✅ Multiple footnote definitions
- ✅ Footnote definition with inline formatting (tags stripped)
- ✅ Footnote reference in list items
- ✅ Superscript function for single/multi-digit numbers

### Edge Cases
- ✅ Footnote reference without definition (still renders superscript)
- ✅ Footnote definition without reference (still rendered)
- ✅ Footnote reference with bold text
- ✅ Footnote reference with link

---

## Rendered Output Examples

### Basic Footnote Reference
**Input:**
```markdown
Text with a footnote[^1].

[^1]: This is the footnote.
```

**Renderer Output:**
```
Text with a footnote¹.

    ¹  This is the footnote.
```

### Multiple Footnotes
**Input:**
```markdown
See here[^1] and there[^2].

[^1]: First footnote.
[^2]: Second footnote.
```

**Renderer Output:**
```
See here¹ and there².

    ¹  First footnote.
    ²  Second footnote.
```

### With Inline Formatting
**Input:**
```markdown
Text[^1].

[^1]: A **bold** footnote with *emphasis*.
```

**Renderer Output:**
```
Text¹.

    ¹  A bold footnote with emphasis.
```

---

## Unicode Superscript Characters

| Digit | Superscript | Unicode |
|-------|-------------|---------|
| 0 | ⁰ | U+00B0 |
| 1 | ¹ | U+00B9 |
| 2 | ² | U+00B2 |
| 3 | ³ | U+00B3 |
| 4 | ⁴ | U+2074 |
| 5 | ⁵ | U+2075 |
| 6 | ⁶ | U+2076 |
| 7 | ⁷ | U+2077 |
| 8 | ⁸ | U+2078 |
| 9 | ⁹ | U+2079 |

---

## Integration Points

### Parser (KB-057) ✅
- Emits `<fnref id="n">` tags for inline references
- Emits `footnote_definition` tokens at document end

### Renderer (KB-059) ✅
- Converts `<fnref>` tags to Unicode superscript
- Renders `footnote_definition` tokens as indented text

### HTML Exporter (KB-060) ⏳
- Will emit `<sup><a href="#fn-n">n</a></sup>` for references
- Will emit `<div class="footnotes"><ol>...</ol></div>` for definitions

### PDF Exporter (KB-060) ⏳
- Will render superscript numbers
- Will render footnote section at document end

---

## Design Decisions

### 1. Unicode Superscript vs ANSI Styling
**Decision:** Use Unicode superscript characters (¹ ² ³) instead of ANSI styling.

**Rationale:**
- ANSI terminals don't support true superscript
- Unicode superscript is universally supported in modern terminals
- Cleaner output without ANSI escape codes
- Better copy-paste behavior

### 2. Indentation for Definitions
**Decision:** Use 4-space indentation for footnote definitions.

**Rationale:**
- Visual separation from main content
- Matches CommonMark convention
- Works well in typical terminal widths (80-120 cols)

### 3. Inline Formatting Stripping
**Decision:** Strip inline tags (bold, italic, links) from footnote definition text in terminal renderer.

**Rationale:**
- Terminal has limited styling capabilities
- Keeps output clean and readable
- HTML/PDF exporters will preserve inline formatting

---

## Test Results

```
441 passed, 25 subtests passed in 38.17s
```

**New tests:** 14 (in `test_footnote_renderer.py`)  
**Total tests:** 441 (427 previous + 14 new)

---

## Files Modified

- `mdutil/renderer.py` (added `_superscript`, `_render_footnote_definition`, updated `_strip_inline_tags` and `_render_token`)
- `tests/test_footnote_renderer.py` (new file, 14 tests)

---

## Next Steps

**KB-060**: HTML and PDF exporter footnote rendering
- HTML: `<sup><a href="#fn-n">n</a></sup>` + `<div class="footnotes">`
- PDF: Superscript numbers + footnote section at document end

---

*Implementation completed 2026-08-18 by AI Agent.*
