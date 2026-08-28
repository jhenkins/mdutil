# mdutil Kanban Log

| timestamp | action | card_id | from_state | to_state | actor | note |
|-----------|--------|---------|------------|----------|-------|------|
| 2026-07-14 10:00 | create | KB-001 | - | backlog | agent | v2.4 theme cycle from todo.md |
| 2026-07-25 00:00 | remove | KB-001 | backlog | done | user | v2.4 syntax theme cycling removed from roadmap (too tricky) |
| 2026-07-14 10:00 | create | KB-002 | - | backlog | agent | v3.0 PDF/HTML export from todo.md |
| 2026-07-14 10:00 | create | KB-006 | - | backlog | agent | v4.0 Mermaid rendering from todo.md |
| 2026-07-14 10:00 | create | KB-005 | - | ready | agent | Housekeeping branch merge/PR |
| 2026-07-14 10:00 | init | - | - | - | agent | Board skeleton created from board-template.md |
| 2026-07-25 00:00 | create | KB-007 | - | backlog | agent | v3.0 Phase 1: Foundation & Setup (fpdf2, module structure) |
| 2026-07-25 00:00 | create | KB-008 | - | backlog | agent | v3.0 Phase 2: PDF Export Core (PdfExporter, CLI flags) |
| 2026-07-25 00:00 | create | KB-009 | - | backlog | agent | v3.0 Phase 3: HTML Export (HtmlExporter, embedded CSS) |
| 2026-07-25 00:00 | create | KB-010 | - | backlog | agent | v3.0 Phase 4: CLI & Configuration (multi-format, config defaults) |
| 2026-07-25 00:00 | create | KB-011 | - | backlog | agent | v3.0 Phase 5: Advanced Features (headers, bookmarks, custom CSS) |
| 2026-07-25 00:00 | create | KB-012 | - | backlog | agent | v3.0 Phase 6: Testing & Documentation (coverage, README, spec) |
| 2026-07-25 00:00 | create | KB-013 | - | backlog | agent | v3.0 Phase 7: Release Preparation (version bump, PR, merge) |
| 2026-07-25 00:00 | remove | KB-002 | backlog | done | agent | Replaced by KB-007 through KB-013 (phased breakdown) |
| 2026-07-25 00:00 | update | KB-002 | backlog | backlog | agent | KB-002 title updated to match todo.md: "Render document to PDF and/or HTML" |
| 2026-07-15 00:00 | update | KB-005 | ready | done | agent | Done — housekeeping branch merged via PR #33 |
| 2026-07-14 10:30 | create | KB-006 | - | backlog | agent | v4.0 Mermaid diagram rendering added to roadmap in todo.md |
|| 2026-07-26 12:00 | update | KB-007 | in-progress | done | jan | Phase 1 complete: fpdf2 dependency added, export module structure created (base.py, pdf.py, html.py), 18 new tests pass, full suite: 149 passed |
|| 2026-07-26 14:00 | update | KB-008 | in-progress | done | jan | Phase 2 complete: PdfExporter implemented, CLI flags wired, 16 CLI tests added, full suite: 149+ passed |
||| 2026-07-27 00:00 | update | KB-009 | in-progress | done | jan | Phase 3 complete: HtmlExporter with embedded CSS and all token types, CLI integration, 18 export tests + CLI tests, full suite: 161 passed |
||| 2026-07-27 02:00 | update | KB-009 | done | done | jan | Bugfix: write_bytes vs write_text branching in _handle_export (HtmlExporter returns str, not bytes). 4 new CLI export tests added. Full suite: 165 passed |
||| 2026-07-27 12:00 | update | KB-010 | backlog | done | jan | Phase 4 complete: multi-format --export pdf,html, --output-dir, export config section, theme passthrough, auto-name fallback to cwd. 8 new tests (3 config + 5 CLI). Full suite: 173 passed |
|||| 2026-07-27 12:00 | update | KB-010 | done | done | jan | Bugfix: removed stdout export path (security risk — binary/HTML to terminal). Export now always writes a file, defaulting to cwd when neither --output nor --output-dir is set. Docs and tests updated. |
||| 2026-07-27 14:00 | update | KB-011 | in-progress | done | jan | Phase 5 complete: PDF headers/footers, custom paper sizes (A4/Letter/Legal), configurable margins, PDF bookmarks for h1-h3, HTML custom CSS via --custom-css, improved table rendering (borders, alternating rows), PermissionError/OSError handling. 12 new tests (7 export tests + 5 CLI tests). Full suite: 185 passed |
|||| 2026-07-27 15:00 | update | KB-012 | backlog | done | jan | Phase 6 complete: coverage 93% on export modules (target 90%+), README/specification updated with all CLI flags, architecture diagram with export branch, manual QA on complex Markdown + Unicode + tables, 7 new PDF exporter tests. Fixes: PDF list/blockquote width, table None-align, Unicode TTF fallback. Full suite: 192 passed |
| 2026-07-27 16:00 | update | KB-013 | backlog | done | jan | Phase 7 complete: version bumped to 3.0.0, pyproject.toml updated to Beta status, version test updated, full verification passed (192 tests, compileall, setup.py check), commit c63ed9a "feat(v3.0.0): add PDF and HTML export", 15 files staged. Remaining: push and open PR. |
| 2026-07-27 17:00 | update | KB-013 | done | done | jan | Manual push/PR/merge steps marked complete per maintainer. PDF rendering bugfixes complete: scaled headings, separate metadata header lines, inline formatting/link annotations, wrapped table cells, blockquote blocks. HTML metadata header fix also documented. Full suite verified: 198 passed, 18 subtests. |
| 2026-07-27 17:30 | create | KB-014 | - | backlog | jan | Created v3.1 bridge card between v3.0 and v4.0 for missing v3.0 export features; initial requested scope is syntax highlighting. |
| 2026-07-27 17:45 | update | KB-014 | backlog | backlog | jan | Scoped v3.1 into Phase 1: shared export syntax highlighting plumbing; detailed checklist added in todo-v3.1.md. |
| 2026-07-27 17:45 | create | KB-015 | - | backlog | jan | v3.1 Phase 2: PDF syntax highlighting track. |
| 2026-07-27 17:45 | create | KB-016 | - | backlog | jan | v3.1 Phase 3: HTML syntax highlighting track. |
| 2026-07-27 17:45 | create | KB-017 | - | backlog | jan | v3.1 Phase 4: verification, documentation, and release prep; v4.0 now depends on this card. |
| 2026-08-06 12:00 | update | KB-019 | backlog | done | jan | Phase 1b complete: MermanRenderer class with platform detection (Linux/macOS/Windows), binary discovery, render_mermaid_svg() with theme support, batch render_diagrams(), _download_binaries.py build script. 22 new unit tests pass. Full suite: 266 passed. Commit: 5bd3e88. |
| 2026-08-06 12:30 | update | KB-020 | backlog | done | jan | Phase 1c complete: Core merman rendering integration verified — MermanRenderer.render_mermaid_svg() implements subprocess execution with timeout (30s), error handling (MermanBinaryNotFoundError, MermanRenderError), theme configuration (default/forest/dark/neutral), batch rendering, and graceful fallback on binary absence. 22 unit tests pass covering all code paths. Full suite: 266 passed. Binary download pending (real release URL needed). |
| 2026-08-06 12:35 | update | KB-021 | backlog | ready | jan | KB-020 complete — parser mermaid block detection (tag mermaid blocks with new token type) can proceed. |
| 2026-08-06 12:35 | update | KB-022 | backlog | ready | jan | KB-020 complete — HTML exporter mermaid integration (consume token + render SVG) can proceed in parallel with KB-021. KB-022 depends on both KB-020 and KB-021. |
| 2026-08-06 13:00 | update | KB-021 | in-progress | done | jan | Parser: `is_mermaid_block()` helper + mermaid token type in `parse_markdown()`. Handles case-insensitive language, tilde fences, info strings (e.g. `mermaid: title`). 18 new tests. |
| 2026-08-06 13:00 | update | KB-022 | in-progress | done | jan | HtmlExporter: batch mermaid rendering via MermanRenderer, inline SVG in `<div class="mermaid">`, graceful fallback to code block when binary unavailable or `--no-mermaid`. Theme passthrough via `--mermaid-theme`. `.mermaid` CSS added. 9 new tests. Full suite: 293 passed. |
| 2026-08-06 14:00 | update | KB-023 | in-progress | done | jan | Comprehensive testing complete: 89 new tests across 4 test files (diagram types, CLI integration, air-gapped, regression). Covers all 10 mermaid diagram types, all 7 CLI integration requirements, air-gapped operation verification, and regression tests for all existing HTML export features. Full suite: 382 passed (293 + 89). |
| 2026-08-06 19:00 | update | KB-023 | done | done | jan | merman-cli v0.7.0 binaries downloaded and installed (Linux x86_64, macOS ARM64, macOS x64, Windows x64). Fixed MermanRenderer subprocess invocation (uses `-t`/`-i`/`-o` flags). Updated _download_binaries.py with correct asset names and extraction logic. Updated mermaid-research.md with actual GitHub URL. Full suite: 382 passed. |
| 2026-08-06 19:30 | update | KB-023 | done | done | jan | Added SHA256 verification to binary installation: _download_binaries.py now verifies checksums after download and on re-run (skips verified binaries). Created _verify_binaries.py utility for standalone checksum verification. sha256sums file incorporated. All 4 binaries verified. |

## KB-024 Completed (2026-08-07)
- Documentation updated: README.md, mdutil-specification.md
- Added Mermaid export section with CLI flags (--mermaid, --no-mermaid, --mermaid-theme)
- Documented air-gapped operation and bundled merman-cli binary
- Added troubleshooting section for mermaid rendering issues
- Updated specification with mermaid architecture details (MermanRenderer, HtmlExporter integration)
- Git branching policy added to AGENTS.md
- Committed as a088746 on feature/v4.0-docs-finalization

## KB-025 Verification Complete (2026-08-07)
- Version: 4.0.1 confirmed
- CLI flags working: --mermaid, --no-mermaid, --mermaid-theme (default/forest/dark/neutral)
- Multi-format export: PDF+HTML working
- SVG rendering: 4 diagrams rendered in default mode
- --no-mermaid: 0 SVGs (correct fallback to code blocks)
- Air-gapped: No network calls, only subprocess execution of bundled merman-cli binary
- Binary bundled: mdutil/export/_merman_binaries/merman-cli (33MB)
- Test suite: 389 passed, 25 subtests passed
- CHANGELOG.md created with v4.0.1 release notes
- Ready for PR to main
## 2026-08-17

KB-050 (parser coverage audit) and KB-051 (strikethrough) complete. Audit documented in `docs/phase-1a-audit-report.md` and `docs/phase-1-continuation.md`. 12 new strikethrough tests added (6 parser + 4 renderer + 2 exporter). Full test suite: 401 passed (389 + 12). Phase 1a complete. — Phase 0 Complete

| 2026-08-17 12:00 | update | - | - | - | agent | Phase 0 complete: all 6 Copilot review findings addressed. 389 tests pass. See docs/phase-0-completion.md for details. Minor gaps: missing multi-line unclosed-fence regression test, no --debug flag test, partial type coercion, HTML exporter logger imported but no debug calls. Ready for v5.0 Phase 1. |

## 2026-08-08
- Added KB-026a/v4.1 Phase 1 (SVG→PNG conversion layer) — ready
- Added KB-026b/v4.1 Phase 2 (PDF Mermaid rendering) — ready, depends on KB-026a
- Added KB-026c/v4.1 Phase 3 (Verification/docs/release) — ready, depends on KB-026b
- Created `docs/KB-026-v4.1-planning.md` with full plan
- Started on `feature/pdf-mermaid-export` branch
- **KB-026b complete** (Phase 2): PdfExporter extended to consume `"mermaid"` tokens. Batch-renders via `SvgToImageRenderer`, embeds PNGs in PDF. Page-break handling, aspect-ratio preservation, error fallback. 7 new PDF mermaid tests. Full suite: 437 passed.
- **KB-026c complete** (Phase 3): All 437 tests pass. PDF smoke test: 3 diagrams → 47KB PDF with 2 embedded PNGs. README/spec/CHANGELOG updated. Version bumped to 4.1.0.

## 2026-08-07
| 2026-08-07 13:36 | create | KB-027 | - | ready | agent | HTML diagram sizing bug: diagrams too big, need 40-50% shrink. Debug plan at docs/debug-plan-html-diagram-sizing.md |
| 2026-08-07 13:36 | create | KB-028 | - | ready | agent | PDF diagram sizing bug: tall diagrams overflow A4 pages. Debug plan at docs/debug-plan-pdf-diagram-sizing.md |
| 2026-08-08 12:00 | move | KB-027 | review | done | agent | PR #52 merged to bugfix/v4.1.0. Shrink factor finalised at 0.5 (50%). |
| 2026-08-18 12:00 | update | KB-061 | backlog | done | jan | Sub/superscript parser support (~sub~, ^super^) |
| 2026-08-18 12:00 | update | KB-062 | backlog | done | jan | Sub/superscript renderer with Unicode subscripts/superscripts, 34 tests |
| 2026-08-19 10:00 | update | KB-065 | backlog | done | jan | KB-065 complete: Parser detects `Term\n:   Definition` syntax. 22 new tests in test_definition_list.py. |
| 2026-08-19 10:00 | update | KB-066 | backlog | done | jan | KB-066 complete: Renderer displays definition lists in terminal/HTML/PDF. Theme keys definition_term, definition_definition added. |
