# mdutil v3.1: Export Syntax Highlighting

## Overview

v3.1 is the bridge release between v3.0 export support and v4.0 Mermaid rendering. It captures export features that did not make v3.0, starting with syntax highlighting for exported code blocks.

## Goal

Rendered PDF and HTML exports should preserve Markdown code-block language information and apply syntax highlighting consistently with mdutil's existing Pygments-based terminal rendering.

## Phase 1: Shared Export Syntax Highlighting Plumbing (v3.1.0)
**Kanban:** KB-014a, KB-014b, KB-014c, KB-014d (KB-014 dropped — too large, decomposed)
**Status:** ✅ Complete
**Chunked into:** 4 smaller tasks that each fit in a context window:
- KB-014a: Trace terminal syntax highlighting pipeline and theme selection ✅
- KB-014b: Design how export syntax themes map to existing `--syntax-theme` / config behavior ✅
- KB-014c: Add reusable helpers for tokenizing highlighted code output for exporters (`highlight_code_html`, `highlight_code_pdf`) ✅
- KB-014d: Add regression fixtures covering known languages and unknown-language fallback ✅

## Phase 2: PDF Syntax Highlighting Track (v3.1.0)
**Kanban:** KB-015  
**Status:** ✅ Complete

- [x] Preserve code-block language labels from parser tokens.
- [x] Render Pygments token colors/styles into fpdf text segments where practical.
- [x] Keep PDF output readable when fonts/styles are unavailable.
- [x] Verify highlighted PDF code blocks do not break wrapping, page breaks, or Unicode fallback.

## Phase 3: HTML Syntax Highlighting Track (v3.1.0)
**Kanban:** KB-016  
**Status:** ✅ Complete

- [x] Emit Pygments-highlighted HTML for fenced code blocks with known languages.
- [x] Include required CSS in exported HTML without requiring external assets.
- [x] Preserve existing custom CSS behavior and allow custom CSS to override base highlighting styles.
- [x] Preserve safe fallback behavior for unknown languages and plain code fences.

## Phase 4: Verification, Documentation, and Release Prep (v3.1.0)
**Kanban:** KB-017  
**Status:** ✅ Complete

- [x] Add focused exporter tests for PDF and HTML syntax highlighting.
- [x] Add CLI integration tests for syntax-highlighted exports.
- [x] Update README, specification, and manual QA with syntax-highlighted export behavior.
- [x] Run full verification: pytest, compileall, setup.py check, version check.

**Bug Fix:** Applied fix to `highlight_code_pdf()` grouping logic — transition from whitespace (no color) to keywords (has color) was merging consecutive segments.

**Test Results:** 224 tests pass (26 new unit tests + 8 new CLI integration tests).

## Success Criteria

v3.1 is complete when:

1. [ ] `mdutil --export html` produces highlighted code blocks for known languages.
2. [ ] `mdutil --export pdf` produces visibly highlighted code blocks for known languages.
3. [ ] Unknown-language code fences still render as readable plain code in both formats.
4. [ ] Existing custom CSS and syntax-theme behavior remains documented and tested.
5. [ ] Full test suite passes.
