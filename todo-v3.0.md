# mdutil v3.0: PDF and HTML Export

**Created:** 2026-07-25  
**Status:** In Progress (Phases 1-3 complete, bugfix verified)  
**Version target:** 3.0.0

---

## Overview

v3.0 adds document export functionality to mdutil, enabling users to render Markdown files to PDF and/or HTML formats. The implementation uses `fpdf2` (pure Python) for PDF generation and direct HTML generation with embedded CSS — avoiding external program dependencies like Pandoc or wkhtmltopdf.

**Key decision:** Maintain cross-platform compatibility (Linux, macOS, Windows) with minimal dependencies.

---

## Dependencies

- **New dependency:** `fpdf2>=2.8.0` (pure Python PDF generation)
- **Optional (v4.0):** `pillow>=10.0` (for Mermaid diagram rendering)

---

## Work Breakdown

### Phase 1: Foundation & Setup (v3.0.0-alpha)
**Goal:** Project structure, dependencies, and basic export infrastructure
**Status:** ✅ Complete

- [x] **1.1** Create feature branch: `feature/v3.0-export`
- [x] **1.2** Add `fpdf2>=2.8.0` to `pyproject.toml` dependencies
- [x] **1.3** Run `python -m pip install -e .` to install new dependency
- [x] **1.4** Create module structure:
  - [x] `mdutil/export/__init__.py` — Export package
  - [x] `mdutil/export/base.py` — Base exporter interface
  - [x] `mdutil/export/pdf.py` — PDF exporter
  - [x] `mdutil/export/html.py` — HTML exporter
- [x] **1.5** Define `Exporter` base class with:
  - [x] `render(tokens, theme, options) -> str | bytes`
  - [x] `supports(format) -> bool`
- [x] **1.6** Run initial test suite to confirm baseline: `python -m pytest -q` (149 passed, 18 new export tests)
- [x] **1.7** Write unit tests for export module: `tests/test_export.py` (18 tests)

---

### Phase 2: PDF Export Core (v3.0.0)
**Goal:** Basic PDF export with headings, paragraphs, code blocks, tables
**Status:** ✅ Complete

- [x] **2.1** Implement `PdfExporter` class in `mdutil/export/pdf.py`
  - [x] Initialize with `fpdf2.FPDF()`
  - [x] Support A4/Letter paper sizes
  - [x] Apply built-in fonts (Helvetica, Courier)
- [x] **2.2** Implement token rendering for:
  - [x] Headings (h1-h6) — with appropriate sizing
  - [x] Paragraphs and text
  - [x] Code blocks (monospace, with background)
  - [x] Tables (basic borders)
  - [x] Horizontal rules
  - [x] Blockquotes
  - [x] Lists (ordered and unordered)
- [x] **2.3** Add CLI flag `--export pdf`
- [x] **2.4** Add CLI flag `--output` (PDF filename)
- [x] **2.5** Wire export through CLI parser:
  - [x] Load document
  - [x] Parse Markdown
  - [x] Select theme
  - [x] Call `PdfExporter.render(tokens, theme, options)`
  - [x] Write output file
- [x] **2.6** Write unit tests:
  - [x] `tests/test_export.py` — test PdfExporter (6 tests)
  - [x] `tests/test_cli.py` — verify CLI export integration (20 tests)
- [x] **2.7** Manual QA:
  - [x] Generate PDF from sample docs
  - [x] Verify output in browser (PDF renders correctly)
  - [x] Check headings, code blocks, tables render correctly

---

### Phase 3: HTML Export (v3.0.0)
**Goal:** HTML export with embedded CSS and syntax highlighting
**Status:** ✅ Complete

- [x] **3.1** Implement `HtmlExporter` class in `mdutil/export/html.py`
  - [x] Generate HTML document structure
  - [x] Embed CSS matching existing theme system
- [x] **3.2** Implement token rendering for:
  - [x] Headings (h1-h6)
  - [x] Paragraphs and text
  - [x] Code blocks (with syntax highlighting)
  - [x] Tables (with styling)
  - [x] Horizontal rules
  - [x] Blockquotes
  - [x] Lists (ordered and unordered)
  - [x] Links (clickable URLs)
- [x] **3.3** Add CLI flag `--export html`
- [x] **3.4** Add CLI flag `--output` (HTML filename)
- [x] **3.5** Wire export through CLI parser
- [x] **3.6** Write unit tests:
  - [x] `tests/test_export.py` — test each token type (18 tests)
  - [x] `tests/test_cli.py` — verify CLI export integration
- [x] **3.7** Manual QA:
  - [x] Generate HTML from sample docs
  - [x] Verify in browser
  - [x] Check syntax highlighting colors match terminal theme
  - [x] Verify links are clickable
- [x] **[BUGFIX]** `_handle_export` in `cli.py` — HtmlExporter returns `str` but code called `write_bytes()` unconditionally. Fixed with format-aware branching (`write_text` for HTML, `write_bytes` for PDF; `str.write` for HTML stdout, `buffer.write` for PDF stdout). 4 new CLI integration tests added.

---

### Phase 4: CLI & Configuration (v3.0.0)
**Goal:** Full CLI integration and user configuration

- [ ] **4.1** Add `--export pdf,html` flag (both formats)
- [ ] **4.2** Add `--output-dir` flag for directory output
- [ ] **4.3** Add `--theme` flag for export theming (reuse existing theme system)
- [ ] **4.4** Add `--quiet` flag to suppress progress output
- [ ] **4.5** Update `~/.mdutilcfg` with export configuration:
  ```ini
  [export]
  # Default export format: pdf, html, or both
  default_format = pdf
  
  # Default output directory
  output_dir = ./exports
  
  # PDF settings
  pdf_paper_size = A4
  pdf_margin_top = 20
  pdf_margin_bottom = 20
  pdf_margin_left = 20
  pdf_margin_right = 20
  
  # HTML settings
  html_embed_css = true
  html_theme = dracula
  ```
- [ ] **4.6** Update `config.py` to load export defaults
- [ ] **4.7** Write integration tests for full pipeline

---

### Phase 5: Advanced Features (v3.0.1)
**Goal:** Improve quality and add configuration options

- [ ] **5.1** Add page headers/footers to PDF export
- [ ] **5.2** Support custom paper sizes (A4, Letter, Legal)
- [ ] **5.3** Add configurable margins via config or CLI flags
- [ ] **5.4** Improve table rendering (bordered tables, alignment)
- [ ] **5.5** Add PDF bookmarks for headings
- [ ] **5.6** Add custom CSS support for HTML export
- [ ] **5.7** Add error handling for:
  - [ ] Invalid theme names
  - [ ] Missing output directories
  - [ ] Write permission errors
  - [ ] File conflicts

---

### Phase 6: Testing & Documentation (v3.0.0)
**Goal:** Comprehensive testing and user documentation

- [ ] **6.1** Run test suite: `python -m pytest -q` (target: 90%+ coverage on new modules)
- [ ] **6.2** Update `README.md`:
  - [ ] Document `--export` flag
  - [ ] Document `--output` flag
  - [ ] Document supported formats (PDF, HTML)
  - [ ] Add export examples
- [ ] **6.3** Update `mdutil-specification.md`:
  - [ ] Add "Export" functional requirement
  - [ ] Document CLI flags
  - [ ] Document configuration options
  - [ ] Update architecture diagram
- [ ] **6.4** Update `todo.md`:
  - [ ] Mark v3.0 as "In Progress"
  - [ ] Add v3.0 items to roadmap section
- [ ] **6.5** Manual QA across platforms:
  - [ ] Linux (Ubuntu, Fedora)
  - [ ] macOS (Intel, Apple Silicon)
  - [ ] Windows 10/11
  - [ ] Python 3.11+
- [ ] **6.6** Test with:
  - [ ] Short documents (10-50 lines)
  - [ ] Medium documents (100-500 lines)
  - [ ] Long documents (1000+ lines)
  - [ ] Unicode text (CJK, emojis)
  - [ ] Complex Markdown (nested lists, mixed emphasis, tables)

---

### Phase 7: Release Preparation (v3.0.0)
**Goal:** Version bump and release

- [ ] **7.1** Update `mdutil/version.py` to `3.0.0`
- [ ] **7.2** Update `pyproject.toml` version
- [ ] **7.3** Run full verification:
  - [ ] `python -m pytest -q`
  - [ ] `python -m unittest discover -v`
  - [ ] `python -m compileall -q mdutil tests`
  - [ ] `python setup.py check`
  - [ ] `python -m mdutil --version`
- [ ] **7.4** Commit changes with message: `feat(v3.0.0): add PDF and HTML export`
- [ ] **7.5** Push feature branch and open PR
- [ ] **7.6** Merge PR after approval

---

## Success Criteria

v3.0 is complete when:

1. ✓ `mdutil --export pdf` generates valid PDF files
2. ✓ `mdutil --export html` generates valid HTML files
3. ✓ Both formats include: headings, paragraphs, code blocks, tables, lists, blockquotes
4. ✓ Syntax highlighting works in both formats (using Pygments)
5. ✓ Themes are applied correctly to exports
6. ✓ Tests pass with ≥90% coverage on new modules
7. ✓ Documentation updated with export usage
8. ✓ Works on Linux, macOS, and Windows (Python 3.11+)
9. ✓ No external dependencies required (pure Python `fpdf2`)

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Foundation | 0.5 day | 0.5 day |
| Phase 2: PDF Export | 2 days | 2.5 days |
| Phase 3: HTML Export | 2 days | 4.5 days |
| Phase 4: CLI & Config | 1 day | 5.5 days |
| Phase 5: Advanced Features | 2 days | 7.5 days |
| Phase 6: Testing & Docs | 1 day | 8.5 days |
| Phase 7: Release | 0.5 day | 9 days |

**Total estimated effort:** ~9 days (2-3 weeks with review/QA)

---

## Notes

- v4.0 will add Mermaid diagram support (deferred from v3.0)
- HTML export can serve as a bridge to Mermaid (via embedded JavaScript)
- PDF export skips Mermaid for now (v4.0 will handle this)
- Keep core dependencies minimal; `fpdf2` is the only required dependency

---

**Author:** Jan Henkins  
**Last Updated:** 2026-07-27
