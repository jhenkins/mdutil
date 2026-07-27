# mdutil v3.1: Export Syntax Highlighting

## Overview

v3.1 is the bridge release between v3.0 export support and v4.0 Mermaid rendering. It captures export features that did not make v3.0, starting with syntax highlighting for exported code blocks.

## Goal

Rendered PDF and HTML exports should preserve Markdown code-block language information and apply syntax highlighting consistently with mdutil's existing Pygments-based terminal rendering.

## Phase 1: Shared Syntax Highlighting Plumbing (v3.1.0)
**Kanban:** KB-014  
**Goal:** Define and expose a shared export-safe syntax highlighting path.

- [ ] Trace existing terminal syntax highlighting pipeline and theme selection.
- [ ] Decide how export syntax themes map to existing `--syntax-theme` / config behavior.
- [ ] Add reusable helpers for tokenizing highlighted code output for exporters.
- [ ] Add regression fixtures covering known languages and unknown-language fallback.

## Phase 2: PDF Syntax Highlighting Track (v3.1.0)
**Kanban:** KB-015  
**Goal:** Render highlighted code blocks in PDF exports.

- [ ] Preserve code-block language labels from parser tokens.
- [ ] Render Pygments token colors/styles into fpdf text segments where practical.
- [ ] Keep PDF output readable when fonts/styles are unavailable.
- [ ] Verify highlighted PDF code blocks do not break wrapping, page breaks, or Unicode fallback.

## Phase 3: HTML Syntax Highlighting Track (v3.1.0)
**Kanban:** KB-016  
**Goal:** Render highlighted code blocks in HTML exports.

- [ ] Emit Pygments-highlighted HTML for fenced code blocks with known languages.
- [ ] Include required CSS in exported HTML without requiring external assets.
- [ ] Preserve existing custom CSS behavior and allow custom CSS to override base highlighting styles.
- [ ] Preserve safe fallback behavior for unknown languages and plain code fences.

## Phase 4: Verification, Documentation, and Release Prep (v3.1.0)
**Kanban:** KB-017  
**Goal:** Prove both tracks work and document the feature.

- [ ] Add focused exporter tests for PDF and HTML syntax highlighting.
- [ ] Add CLI integration tests for syntax-highlighted exports.
- [ ] Update README, specification, and manual QA with syntax-highlighted export behavior.
- [ ] Run full verification: pytest, compileall, setup.py check, version check.

## Success Criteria

v3.1 is complete when:

1. [ ] `mdutil --export html` produces highlighted code blocks for known languages.
2. [ ] `mdutil --export pdf` produces visibly highlighted code blocks for known languages.
3. [ ] Unknown-language code fences still render as readable plain code in both formats.
4. [ ] Existing custom CSS and syntax-theme behavior remains documented and tested.
5. [ ] Full test suite passes.
