# v5.0: Better Markdown Rendering - Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

## Relationship to Kanban Board

- **`.kanban/board.md`** is the source of truth for card state (backlog / ready / in-progress / done).
- **`todo-v5.0.md`** is the implementation companion — detailed per-KB task checklists.
- Do not maintain separate todo documents. If a card needs more detail, update its entry in `board.md` Notes or this file.
- Completed v3.0/v3.1/v4.0 plans are archived in `docs/archive/`.

**Goal:** Extend mdutil's Markdown rendering to support GFM/CommonMark features: strikethrough, task lists, math notation, footnotes, sub/superscript, highlight, definition lists, link titles, image rendering, and fix nested list nesting.

**Architecture:** 
- Extend parser.py to recognize new block/inline syntax
- Extend renderer.py to display new features in terminal ANSI
- Update HTML/PDF exporters to handle new token types
- Maintain backward compatibility with existing themes

**Tech Stack:** Python, prompt_toolkit, fpdf2, Pygments, CommonMark spec

---

## Phase 1: Foundation & Parser Extensions

### Phase 1a: Research & Analysis (0.5 day)

**Goal:** Document exact parser gaps and design extension points

**Tasks:**
- [x] KB-050: Audit current parser coverage against CommonMark/GFM spec
  - [ ] Map every parser regex to spec requirement
  - [ ] Document where inline/block parsing diverges from spec
  - [ ] Identify which features are inline vs block level
  - [ ] Review current `_parse_inline_segment` extension points

**Files:**
- Analyze: `mdutil/parser.py`, `mdutil/renderer.py`
- Reference: CommonMark spec, GFM spec

---

### Phase 1b: Strikethrough (GFM) (0.5 day)

**Goal:** Support `~~strikethrough~~` syntax

**Tasks:**
- [x] KB-051: Parser: detect `~~text~~` inline syntax
  - [ ] Add regex pattern for strikethrough markers
  - [ ] Extend `_parse_inline_segment` to handle `~~...~~`
  - [ ] Generate `<del>text</del>` output
  - [ ] Add span type `"del"` for semantic metadata
  - [ ] Write tests for: basic, nested, escaped, edge cases

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)
- Test: `tests/test_parser.py`

---

### Phase 1c: Task Lists (GFM) (0.5 day)

**Goal:** Render `- [x]` and `- [ ]` as checked/unchecked checkboxes

**Tasks:**
- [x] KB-052: Parser: detect task list items
  - [x] Extend `_extract_list` to recognize `[ ]` and `[x]` markers
  - [x] Add `checked` field to list items (True/False/None)
  - [x] Set `task` flag on list token when any item has checkboxes

**Files:**
- Modify: `mdutil/parser.py:267-335` (_extract_list)

- [x] KB-053: Renderer: display checkboxes in terminal
  - [x] Render `[ ]` as `☐` (U+2610) for unchecked tasks
  - [x] Render `[x]`/`[X]` as `☑` (U+2611) for checked tasks
  - [x] Support mixed checked/unchecked in same list
  - [x] Regular items in task lists render without checkbox symbols

**Files:**
- Modify: `mdutil/renderer.py:128-167` (_render_list)

- [x] KB-054: HTML/PDF exporter: render checkboxes
  - [x] HTML: emit `<input type="checkbox" disabled>` / `<input type="checkbox" checked disabled>`
  - [x] PDF: prefix task items with `☐` / `☑` Unicode symbols
  - [x] Regular lists unaffected in both exporters

**Files:**
- Modify: `mdutil/export/html.py:565-595` (_render_list)
- Modify: `mdutil/export/pdf.py:998-1045` (_render_list)

---

### Phase 1d: Math Notation (LaTeX) (1 day)

**Goal:** Render `$E=mc^2$` and `$$display$$` math

**Tasks:**
- [x] KB-055: Parser: detect inline math `$...$`
  - [ ] Add regex for `$...$` inline math
  - [ ] Add regex for `$$...$$` display math (optional)
  - [ ] Generate `<math>latex</math>` output
  - [ ] Escape special LaTeX characters in plain text

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-056: Renderer: display math in terminal
  - [ ] Render LaTeX as readable text fallback (e.g., "E = mc²")
  - [ ] Add monospace styling for math blocks
  - [ ] Support basic LaTeX to Unicode conversion
  - [ ] Option to show raw LaTeX in comments

**Files:**
- Modify: `mdutil/renderer.py:39-61` (_render_token)
- Create: `mdutil/math_renderer.py` (LaTeX→Unicode converter)

---

## Phase 2: Inline Extensions

### Phase 2a: Footnotes (GFM) (1 day)

**Goal:** Support `[^1]` references and `[^1]: text` definitions

**Tasks:**
- [x] KB-057: Parser: detect footnote definitions
  - [ ] Add regex for `[^label]: text` at document end
  - [ ] Store footnote definitions in token metadata
  - [ ] Generate `<sup>` markers for references

**Files:**
- Modify: `mdutil/parser.py` (add footnote collection pass)

- [x] KB-058: Parser: detect footnote references inline
  - [ ] Add regex for `[^label]` inline references
  - [ ] Replace with clickable/superscript marker
  - [ ] Link to footnote definitions

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-059: Renderer: display footnotes
  - [ ] Render `[^1]` as superscript in terminal
  - [ ] Add footnote section at document end
  - [ ] Support footnote navigation in interactive mode

**Files:**
- Modify: `mdutil/renderer.py`
- Modify: `mdutil/display.py` (interactive footnote handling)

- [x] KB-060: HTML/PDF exporter: render footnotes
  - [ ] HTML: anchor links + bottom-of-page footnotes
  - [ ] PDF: superscript markers + footnote section
  - [ ] Support footnote numbering and cross-references

**Files:**
- Modify: `mdutil/export/html.py`
- Modify: `mdutil/export/pdf.py`

---

### Phase 2b: Subscript & Superscript (GFM/CommonMark) (0.5 day)

**Goal:** Support `H~2~O` (subscript) and `e^2` (superscript)

- [x] KB-061: Parser: detect sub/superscript syntax
  - [x] Add regex for `~sub~` subscript
  - [x] Add regex for `^super^` superscript
  - [x] Generate `<sub>text</sub>` and `<sup>text</sup>`

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-062: Renderer: display sub/superscript
  - [x] Terminal: use Unicode sub/superscript characters
  - [x] Fallback: `[sub]` and `^sup^` notation
  - [x] Theme support for sub/superscript styling

**Files:**
- Modify: `mdutil/renderer.py:200-212` (_strip_inline_tags)

---

### Phase 2c: Highlight (GFM) (0.5 day)

**Goal:** Support `==highlight==` syntax

**Tasks:**
- [x] KB-063: Parser: detect highlight syntax
  - [x] Add regex for `==text==`
  - [x] Generate `<mark>text</mark>` output
  - [x] Add span type `"mark"` for metadata

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-064: Renderer: display highlights
  - [x] Terminal: yellow background highlighting (48;2;R;G;Bm)
  - [x] Theme support for highlight color
  - [x] HTML: `<mark>` tag with CSS

**Files:**
- Modify: `mdutil/renderer.py:174-184` (_style)
- Modify: `mdutil/themes.py`

---

## Phase 3: Block Extensions

### Phase 3a: Definition Lists (CommonMark) (0.5 day) ✅ **COMPLETE**

**Goal:** Support `Term\n:   Definition` syntax

**Tasks:**
- [x] KB-065: Parser: detect definition lists
  - [x] Add regex for `Term\n:   Definition`
  - [x] Generate `{"type": "definition", "terms": [...], "definitions": [...]}` token
  - [x] Support multiple terms with same definition
  - [x] Support multiple definitions per term
  - [x] Support inline formatting in definitions (**bold**, *italic*, `code`, links)

**Files:**
- Modify: `mdutil/parser.py` (add `_extract_definition_list()` function)

- [x] KB-066: Renderer: display definition lists
  - [x] Terminal: indent definition with "—" prefix, styled term
  - [x] Style term and definition differently (theme keys `definition_term`, `definition_definition`)
  - [x] Support multi-line definitions (each definition on its own line)
  - [x] HTML exporter: `<dl>/<dt>/<dd>` structure with CSS
  - [x] PDF exporter: bold term + indented definitions with "—" prefix

**Files:**
- Modify: `mdutil/renderer.py` (add `_render_definition()`)
- Modify: `mdutil/export/html.py` (add `_render_definition()` + CSS)
- Modify: `mdutil/export/pdf.py` (add `_render_definition()`)
- Modify: `mdutil/themes.py` (add `definition_term`, `definition_definition` theme keys)
- Add: `tests/test_definition_list.py` (22 tests)

---

### Phase 3b: Image Rendering (GFM) (1 day) ✅ **COMPLETE**

**Goal:** Render `![alt](url)` as image placeholders or URLs

**Tasks:**
- [x] KB-067: Parser: detect image syntax properly
  - [x] Fix `![alt](url)` parsing (currently parsed as link)
  - [x] Generate `{"type": "image", "alt": ..., "src": ...}` token
  - [x] Preserve alt text for accessibility

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-068: Renderer: display images in terminal
  - [x] Terminal: show `[image: alt text]` placeholder
  - [x] Option to show URL below placeholder
  - [x] Support file:// URLs with file metadata

**Files:**
- Modify: `mdutil/renderer.py:39-61` (_render_token)

- [x] KB-069: HTML exporter: render images
  - [x] HTML: `<img src="url" alt="alt">` (via `_render_spans` image span handler)
  - [x] HTML: CSS for images (`max-width: 100%; box-sizing: border-box;`)
  - [x] HTML: support width/height attributes from GFM `=WxH` dimension syntax

**Files:**
- Modify: `mdutil/export/html.py` (line 413-420: emit width/height on `<img>`)

- [x] KB-070: PDF exporter: render images
  - [x] PDF: embed local images via fpdf2 `pdf.image()` with aspect ratio preservation
  - [x] PDF: support local file paths (relative and absolute)
  - [x] PDF: remote URLs fall back to `[image: alt]` placeholder text
  - [x] PDF: dimension hints (`=WxH`) scaled to fit page width
  - [x] PDF: exception handling with fallback to placeholder

**Files:**
- Modify: `mdutil/export/pdf.py` (line 88-112: `_InlineHTMLParser` emits image segments; line 208-310: `_embed_image` method)

---

## Phase 4: Link Improvements

### Phase 4a: Link with Title (GFM) (0.5 day)

**Goal:** Support `[text](url "title")` with hover titles

**Tasks:**
- [x] KB-071: Parser: parse link title attribute
  - [x] Fix current parsing of `"title"` in link syntax
  - [x] Add `title` field to link tokens
  - [x] Preserve title in export tokens

**Files:**
- Modify: `mdutil/parser.py:378-461` (_parse_inline_segment)

- [x] KB-072: HTML/PDF exporter: render link titles
  - [x] HTML: add `title` attribute to `<a>` tags
  - [x] PDF: include title in link annotation

**Files:**
- Modify: `mdutil/export/html.py`
- Modify: `mdutil/export/pdf.py`

---

## Phase 5: Nested List Fix

### Phase 5a: Fix Nested List Nesting (Bug Fix) (0.5 day)

**Goal:** Fix nested list items being merged into single line

**Tasks:**
- [x] KB-073: Debug and fix nested list parsing
  - [x] Identify why nested items merge
  - [x] Fix list item extraction to preserve nesting structure
  - [x] Add proper indentation to nested items in output
  - [x] Update renderer, HTML exporter, PDF exporter for sub_list recursion

**Files:**
- Modify: `mdutil/parser.py` (_extract_list)
- Modify: `mdutil/renderer.py` (_render_list)
- Modify: `mdutil/export/html.py` (_render_list)
- Modify: `mdutil/export/pdf.py` (_render_list)

- [x] KB-074: Add tests for nested list nesting
  - [x] Test 1, 2, 3 levels of nesting
  - [x] Test mixed ordered/unordered lists
  - [x] Test nested lists with inline formatting
  - [x] Test nested task lists
  - [x] Test blank-line separation between separate list groups

**Files:**
- Test: `tests/test_nested_list.py` (20 tests)

---

## Phase 6: Theme & Configuration

### Phase 6a: Theme Support for New Features (0.5 day)

**Goal:** Add theme support for strikethrough, task lists, highlights, etc.

**Tasks:**
- [ ] KB-075: Extend theme system for new inline styles
  - [ ] Add `strikethrough`, `subscript`, `superscript`, `highlight` styles
  - [ ] Add `task_list_checked`, `task_list_unchecked` styles
  - [ ] Add `definition_term`, `definition_definition` styles
  - [ ] Update all built-in themes with new style values

**Files:**
- Modify: `mdutil/themes.py`
- Update: theme JSON files in `mdutil/themes/`

- [ ] KB-076: Config support for new features
  - [ ] Add `--math-fallback` flag (show raw LaTeX vs Unicode)
  - [ ] Add `--footnote-style` flag (numbered, bracketed, etc.)
  - [ ] Add config options for new feature toggles

**Files:**
- Modify: `mdutil/cli.py`
- Modify: `mdutil/config.py`

---

## Phase 7: Testing & Documentation

### Phase 7a: Comprehensive Testing (1 day)

**Goal:** Add tests for all new features

**Tasks:**
- [ ] KB-077: Parser tests for all new syntax
  - [ ] Strikethrough parsing
  - [ ] Task list parsing
  - [ ] Math notation parsing
  - [ ] Footnote parsing
  - [ ] Sub/superscript parsing
  - [ ] Highlight parsing
  - [ ] Definition list parsing
  - [ ] Image parsing
  - [ ] Link with title parsing
  - [ ] Nested list nesting

**Files:**
- Test: `tests/test_parser.py` (add new test classes)

- [ ] KB-078: Renderer tests for all new features
  - [ ] Terminal rendering of all new features
  - [ ] Theme color application
  - [ ] Fallback behavior for unsupported terminals

**Files:**
- Test: `tests/test_renderer.py`

- [x] KB-079: Exporter tests for HTML/PDF
  - [x] HTML export of all new features
  - [x] PDF export of all new features
  - [x] Cross-format consistency

**Files:**
- Test: `tests/test_export_v5_features.py` (83 tests)

- [x] KB-080: CLI integration tests
  - [x] Test all new CLI flags
  - [x] Test config file with new options
  - [x] Test multi-format export with new features

**Files:**
- Test: `tests/test_cli_v5_integration.py` (32 tests)

---

### Phase 7b: Documentation (0.5 day)

**Goal:** Update all documentation for new features

**Tasks:**
- [ ] KB-081: Update README.md
  - [ ] Add "New Features" section for v5.0
  - [ ] Add usage examples for new syntax
  - [ ] Document CLI flags and config options

- [ ] KB-082: Update mdutil-specification.md
  - [ ] Add new functional requirements
  - [ ] Update architecture diagram if needed
  - [ ] Add testing strategy for new features

- [ ] KB-083: Update CHANGELOG.md
  - [ ] Document all v5.0 features
  - [ ] Note breaking changes (if any)
  - [ ] List migration notes

- [ ] KB-084: Update inline-quality fixture
  - [ ] Add new inline syntax to test fixtures
  - [ ] Update golden files for new rendering

**Files:**
- Update: `README.md`, `mdutil-specification.md`, `CHANGELOG.md`, `tests/fixtures/`

---

## Phase 8: Verification & Release

### Phase 8a: Verification (0.5 day)

**Goal:** Verify all features work end-to-end

**Tasks:**
- [ ] KB-085: Run full test suite
  - [ ] Verify all existing tests still pass
  - [ ] Verify new tests pass
  - [ ] Check test coverage is ≥90%

- [x] KB-086: Manual QA with real documents
  - [x] Test with CommonMark test suite
  - [x] Test with GFM test suite
  - [x] Test with user-provided documents
  - [x] Verify rendering in different terminal sizes/themes

- [ ] KB-087: Performance testing
  - [ ] Verify no regressions in large document rendering
  - [ ] Test rendering performance with many new features
  - [ ] Profile if needed

---

### Phase 8b: Release Prep (0.5 day)

**Goal:** Prepare v5.0 release

**Tasks:**
- [ ] KB-088: Version bump
  - [ ] Update `mdutil/version.py` to `5.0.0`
  - [ ] Update semantic versioning rules if needed

- [ ] KB-089: Create release PR
  - [ ] Commit all changes
  - [ ] Create PR to main branch
  - [ ] Request review

---

## Success Criteria

v5.0 is complete when:

1. ✓ All GFM/CommonMark features parse correctly
2. ✓ Terminal rendering displays all new features
3. ✓ HTML export preserves all new features
4. ✓ PDF export preserves all new features
5. ✓ Theme system supports all new inline styles
6. ✓ All tests pass (existing + new)
7. ✓ Documentation is updated
8. ✓ No regressions in existing functionality

---

## Estimated Timeline

- **Phase 1 (Foundation):** 2 days
- **Phase 2 (Inline Extensions):** 2 days
- **Phase 3 (Block Extensions):** 2 days
- **Phase 4 (Link Improvements):** 1 day
- **Phase 5 (Nested List Fix):** 1 day
- **Phase 6 (Theme & Config):** 1 day
- **Phase 7 (Testing & Docs):** 2 days
- **Phase 8 (Verification & Release):** 1 day

**Total:** ~12 days (2.5 weeks at 5 days/week)

---

## Notes

- All features are backward compatible
- New features can be opted out via config flags
- Themes can override rendering of new features
- Documentation and tests are prioritized equally with implementation
