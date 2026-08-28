# KB-050: Parser Coverage Audit Report

> **Date:** 2026-08-17
> **Branch:** `feature/v5.0-rendering`
> **Purpose:** Document current parser gaps against CommonMark/GFM spec before adding new features.

---

## Audit Results

### ✅ Currently Supported (Block Elements)

| Feature | Token Type | Notes |
|---------|-----------|-------|
| Headings h1-h6 | `heading` | Full level support |
| Horizontal rules | `horizontal_rule` | `---`, `***`, `___` all work |
| Blockquotes | `blockquote` | Nested supported |
| Ordered lists | `list` | `1. 2. 3.` |
| Unordered lists | `list` | `-`, `+`, `*` all work |
| Code fences (backtick) | `code` | Language detection works |
| Code fences (tilde) | `code` | Language detection works |
| Tables (basic) | `table` | Header + separator + rows |
| Fenced code (bare) | `code` | No language → `None` |
| Fenced code (info string) | `mermaid` | `mermaid: title` recognized |
| Multi-line paragraphs | `paragraph` | Soft breaks joined with space |

### ✅ Currently Supported (Inline Elements)

| Feature | Output | Notes |
|---------|--------|-------|
| Bold `**text**` | `<strong>text</strong>` | Spans: `{"type": "strong"}` |
| Italic `*text*` | `<em>text</em>` | Spans: `{"type": "emphasis"}` |
| Italic `_text_` | `<em>text</em>` | Same as above |
| Inline code `` `code` `` | `<code>code</code>` | Spans: `{"type": "inline_code"}` |
| Links `[text](url)` | `<a href="url">text</a>` | Spans: `{"type": "link", "href": "url"}` |
| Autolinks `<url>` | `<a href="url">url</a>` | Spans: `{"type": "link"}` |
| Escaped chars `\*` | `*not italic*` | Escaping works |
| Soft breaks | space-joined | Multi-line paragraphs work |

### ❌ NOT Currently Supported (GFM/CommonMark)

| Feature | Current Behavior | Required Parser Change |
|---------|-----------------|----------------------|
| Strikethrough `~~text~~` | Paragraph (literal `~~`) | Add `~~` detection in `_parse_inline_segment` |
| Task lists `- [ ]` | List item (no checked field) | Extend `_extract_list` to detect `[x]`/`[ ]` |
| Math inline `$E=mc^2$` | Paragraph (literal `$`) | Add `$` detection in `_parse_inline_segment` |
| Math display `$$...$$` | Paragraph (literal `$$`) | Add block-level `$$` detection |
| Footnote ref `[^1]` | Paragraph (literal `[^1]`) | Add `\[` detection in `_parse_inline_segment` |
| Footnote def `[^1]: text` | Two separate paragraphs | Add document-level footnote pass |
| Subscript `H~2~O` | Paragraph (literal `~`) | Add `~` detection (but conflicts with strikethrough) |
| Superscript `e^2^` | Paragraph (literal `^`) | Add `^` detection in `_parse_inline_segment` |
| Highlight `==text==` | Paragraph (literal `==`) | Add `==` detection in `_parse_inline_segment` |
| Definition lists | Paragraph (literal `:\n`) | Add block-level definition detection |
| Images `![alt](url)` | Treated as link (broken) | Add `!` prefix detection for image syntax |
| Image with title | Broken link | Fix image parsing |
| Link with title | Title not preserved | Add `"title"` extraction in link parsing |
| Nested lists (indent) | **BROKEN** — splits at indent | Fix `_extract_list` to handle indentation |

### ⚠️ Known Bugs

1. **Nested lists break at indentation** — `- item 1` → `- item 2` works, but indented items create a new paragraph break. This is KB-073/074 scope.
2. **Table alignment rows fail** — `|:--|:-:|--:|` not detected as separator (align feature). Likely a regex issue in `_is_table_separator`.
3. **Escaped backslash fails** — `\"` produces `\` then `"` instead of just `"`.

---

## Design Decisions for Phase 1

### Strikethrough `~~text~~` (KB-051)
- **Scope:** Inline syntax only
- **Parser:** Add `~~` detection in `_parse_inline_segment` → `<del>text</del>`
- **Renderer:** Strip `<del>` tags (terminal has no strikethrough ANSI)
- **Exporter:** HTML uses `<del>`, PDF uses strikethrough font style

### Task Lists `- [x]` (KB-052..054)
- **Scope:** Block-level list item modifier
- **Parser:** Extend `_extract_list` to detect `[ ]`/`[x]`/`[X]` markers → add `checked` field to items
- **Renderer:** Display `☒` (unchecked) / `☑` (checked) before list items
- **Exporter:** HTML uses Unicode symbols, PDF embeds symbols

### Math Notation (KB-055..056)
- **Scope:** Inline `$...$` and display `$$...$$`
- **Parser:** Add inline `$` detection (careful: `$` is valid in URLs/strings); add block-level `$$` detection
- **Renderer:** Render LaTeX as readable text fallback (e.g., `E = mc²`)
- **Exporter:** HTML uses MathJax/KaTeX (future), PDF uses Unicode approximations

### Footnotes (KB-057..060)
- **Scope:** Block-level `[^1]: text` + inline `[^1]`
- **Parser:** Two passes — collect definitions at document end, replace refs inline
- **Renderer:** Display `[^1]` as superscript number
- **Exporter:** HTML uses anchor links, PDF uses superscript + footnote section

### Subscript/Superscript (KB-061..062)
- **Scope:** Inline `~sub~` and `^super^`
- **⚠️ CONFLICT:** `~` already used for strikethrough and tilde fences
- **Resolution:** Subscript requires different delimiter (e.g., `<sub>text</sub>` HTML-only) OR use `^text^` for superscript (unambiguous)

### Highlight `==text==` (KB-063..064)
- **Scope:** Inline syntax
- **Parser:** Add `==` detection → `<mark>text</mark>`
- **Renderer:** Reverse-video or bright color highlighting
- **Exporter:** HTML uses `<mark>`, PDF uses highlight color

### Definition Lists (KB-065..066)
- **Scope:** Block-level `Term\n:   Definition`
- **Parser:** Detect `Term` followed by `:   text` on next line → `{"type": "definition", "term": ..., "definition": ...}`
- **Renderer:** Indent definition with `→` prefix
- **Exporter:** HTML uses `<dl>/<dt>/<dd>`, PDF uses indentation

### Images (KB-067..070)
- **Scope:** Inline `![alt](url)`
- **Parser:** Detect `!` prefix → `{"type": "image", "alt": ..., "src": ...}`
- **Renderer:** Display `[image: alt text]` placeholder
- **Exporter:** HTML uses `<img>`, PDF embeds PNG/JPEG

### Link with Title (KB-071..072)
- **Scope:** Inline `[text](url "title")`
- **Parser:** Extract `"title"` from link href string → add `title` field
- **Exporter:** HTML uses `title` attribute on `<a>`, PDF uses link annotation

---

## Implementation Order (Recommended)

1. **KB-051** — Strikethrough (simplest inline feature)
2. **KB-052..054** — Task lists (block-level modifier)
3. **KB-063..064** — Highlight (simple inline)
4. **KB-061..062** — Subscript/Superscript (⚠️ resolve `~` conflict first)
5. **KB-071..072** — Link with title (minor parser extension)
6. **KB-067..070** — Images (block + inline)
7. **KB-055..056** — Math notation (complex, LaTeX rendering)
8. **KB-057..060** — Footnotes (two-pass parser)
9. **KB-065..066** — Definition lists (block-level)

---

## Test Strategy

- Add regression tests for each new feature to `tests/test_parser.py`
- Add renderer tests to `tests/test_renderer.py`
- Add exporter tests to `tests/test_export.py`
- Run full suite after each KB to catch regressions

---

*Audit completed 2026-08-17 by Hermes Agent.*
