# mdutil Kanban Board

## Meta
project_id: mdutil
board_version: 4.2
updated: 2026-08-21 04:15
lane_model: basic

## Lanes
- backlog
- ready
- in-progress
- blocked
- review
- done

## Cards
| id | title | state | priority | owner | due | depends_on | updated |
|----|-------|-------|----------|-------|-----|------------|---------|
| KB-050 | v5.0 Phase 1a: Research & analysis (parser coverage audit) | done | P1 | jan | - | - | 2026-08-17 |
| KB-051 | v5.0 Phase 1b: Parser strikethrough support (~~text~~) | done | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-052 | v5.0 Phase 1c: Parser task list detection (- [x] syntax) | done | P1 | jan | - | KB-050 | 2026-08-21 |
| KB-053 | v5.0 Phase 1c: Renderer task list display (checkboxes) | done | P1 | jan | - | KB-052 | 2026-08-21 |
| KB-054 | v5.0 Phase 1c: Exporter task list rendering (HTML/PDF) | done | P1 | jan | - | KB-053 | 2026-08-21 |
| KB-055 | v5.0 Phase 1d: Parser math notation detection ($...$) | done | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-056 | v5.0 Phase 1d: Renderer math notation display | done | P1 | jan | - | KB-055 | 2026-08-17 |
| KB-057 | v5.0 Phase 2a: Parser footnote definitions ([^1]: text) | done | P1 | jan | - | KB-050 | 2026-08-18 |
| KB-058 | v5.0 Phase 2a: Parser footnote references ([^1]) | done | P1 | jan | - | KB-057 | 2026-08-18 |
| KB-059 | v5.0 Phase 2a: Renderer footnotes display | done | P1 | jan | - | KB-058 | 2026-08-18 |
| KB-060 | v5.0 Phase 2a: Exporter footnotes rendering | done | P1 | jan | - | KB-059 | 2026-08-18 |
| KB-061 | v5.0 Phase 2b: Parser subscript/superscript syntax | done | P1 | jan | - | KB-050 | 2026-08-18 |
| KB-062 | v5.0 Phase 2b: Renderer sub/superscript display | done | P1 | jan | - | KB-061 | 2026-08-18 |
| KB-063 | v5.0 Phase 2c: Parser highlight syntax (==text==) | done | P1 | jan | - | KB-050 | 2026-08-19 |
| KB-064 | v5.0 Phase 2c: Renderer highlight display | done | P1 | jan | - | KB-063 | 2026-08-19 |
| KB-065 | v5.0 Phase 3a: Parser definition lists syntax | done | P1 | jan | - | KB-050 | 2026-08-19 |
| KB-066 | v5.0 Phase 3a: Renderer definition lists display | done | P1 | jan | - | KB-065 | 2026-08-19 |
| KB-067 | v5.0 Phase 3b: Parser image syntax (![alt](url)) | done | P1 | jan | - | KB-050 | 2026-08-19 |
| KB-068 | v5.0 Phase 3b: Renderer image placeholder display | done | P1 | jan | - | KB-067 | 2026-08-19 |
| KB-069 | v5.0 Phase 3b: HTML exporter image rendering | done | P1 | jan | - | KB-068 | 2026-08-21 |
| KB-070 | v5.0 Phase 3b: PDF exporter image rendering | done | P1 | jan | - | KB-069 | 2026-08-21 |
| KB-071 | v5.0 Phase 4a: Parser link title attribute | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-072 | v5.0 Phase 4a: Exporter link title rendering | backlog | P1 | jan | - | KB-071 | 2026-08-17 |
| KB-073 | v5.0 Phase 5a: Parser nested list structure preservation | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-074 | v5.0 Phase 5a: Tests for nested list nesting | backlog | P1 | jan | - | KB-073 | 2026-08-17 |
| KB-075 | v5.0 Phase 6a: Theme support for new inline styles | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-076 | v5.0 Phase 6a: Config support for new features | backlog | P1 | jan | - | KB-075 | 2026-08-17 |
| KB-077 | v5.0 Phase 7a: Parser tests for new syntax | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-078 | v5.0 Phase 7a: Renderer tests for new features | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-079 | v5.0 Phase 7a: Exporter tests for new features | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-080 | v5.0 Phase 7a: CLI integration tests | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-081 | v5.0 Phase 7b: README documentation update | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-082 | v5.0 Phase 7b: Specification documentation update | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-083 | v5.0 Phase 7b: Changelog documentation update | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-084 | v5.0 Phase 7b: Fixture and golden file updates | backlog | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-085 | v5.0 Phase 8a: Full test suite verification | backlog | P1 | jan | - | KB-077, KB-078, KB-079, KB-080 | 2026-08-17 |
| KB-086 | v5.0 Phase 8a: Manual QA with real documents | backlog | P1 | jan | - | KB-085 | 2026-08-17 |
| KB-087 | v5.0 Phase 8a: Performance testing | backlog | P1 | jan | - | KB-085 | 2026-08-17 |
| KB-088 | v5.0 Phase 8b: Version bump to 5.0.0 | backlog | P1 | jan | - | KB-086, KB-087 | 2026-08-17 |
| KB-089 | v5.0 Phase 8b: Release PR creation | backlog | P1 | jan | - | KB-088 | 2026-08-17 |
| KB-007 | v3.0 Phase 1: Foundation & Setup (fpdf2, module structure) | done | P2 | jan | - | - | 2026-07-26 |
| KB-008 | v3.0 Phase 2: PDF Export Core (PdfExporter, CLI flags) | done | P2 | jan | - | KB-007 | 2026-07-26 |
| KB-009 | v3.0 Phase 3: HTML Export (HtmlExporter, embedded CSS) | done | P2 | jan | - | KB-008 | 2026-07-26 |
| KB-010 | v3.0 Phase 4: CLI & Configuration (multi-format, config defaults) | done | P2 | jan | - | KB-008, KB-009 | 2026-07-27 |
| KB-011 | v3.0 Phase 5: Advanced Features (headers, bookmarks, custom CSS) | done | P2 | jan | - | KB-010 | 2026-07-27 |
| KB-012 | v3.0 Phase 6: Testing & Documentation (coverage, README, spec) | done | P2 | jan | - | KB-011 | 2026-07-27 |
| KB-013 | v3.0 Phase 7: Release Preparation (version bump, PR, merge) | done | P2 | jan | - | KB-012 | 2026-07-27 |
| KB-014 | v3.1 Phase 1: Shared export syntax highlighting plumbing | dropped | P2 | jan | - | KB-013 | 2026-08-01 |
| KB-014a | v3.1 Phase 1a: Trace terminal highlighting pipeline | done | P2 | jan | - | KB-014 (dropped) | 2026-08-01 |
| KB-014b | v3.1 Phase 1b: Design export theme mapping | done | P2 | jan | - | KB-014a | 2026-08-01 |
| KB-014c | v3.1 Phase 1c: Build tokenizer helpers for exporters | done | P2 | jan | - | KB-014b | 2026-08-01 |
| KB-014d | v3.1 Phase 1d: Add regression test fixtures | done | P2 | jan | - | KB-014c | 2026-08-01 |
| KB-015 | v3.1 Phase 2: PDF syntax highlighting track | done | P2 | jan | - | KB-014d | 2026-08-01 |
| KB-016 | v3.1 Phase 3: HTML syntax highlighting track | done | P2 | jan | - | KB-014d | 2026-08-01 |
| KB-017 | v3.1 Phase 4: Verification, documentation, release prep | **done** | P2 | jan | - | KB-015, KB-016 | 2026-08-01 |
| KB-018 | v4.0 Phase 1a: Document mermaid rendering research (KB-001) | done | P2 | jan | - | KB-017 | 2026-08-05 |
| KB-019 | v4.0 Phase 1b: Bundle infrastructure & MermanRenderer (KB-002) | done | P2 | jan | - | KB-018 | 2026-08-06 |
| KB-020 | v4.0 Phase 1c: Core merman rendering integration (KB-003) | done | P2 | jan | - | KB-019 | 2026-08-06 |
| KB-021 | v4.0 Phase 2a: Markdown parser mermaid block detection (KB-005) | done | P2 | jan | - | KB-020 | 2026-08-06 |
| KB-022 | v4.0 Phase 2b: HTML exporter mermaid integration (KB-004) | done | P2 | jan | - | KB-020, KB-021 | 2026-08-06 |
| KB-023 | v4.0 Phase 3a: Comprehensive testing (KB-006) | **done** | P2 | jan | - | KB-022 | 2026-08-06 |
| KB-024 | v4.0 Phase 3b: Documentation (KB-007) | done | P2 | jan | - | KB-023 | 2026-08-07 |
| KB-025 | v4.0 Phase 4: Verification & release prep (KB-008) | done | P3 | jan | - | KB-024 | 2026-08-07 |
| KB-006 | v4.0: Add Mermaid diagram rendering (superseded by KB-018..025) | dropped | P3 | unassigned | - | KB-017 | 2026-07-25 |
| KB-005 | Housekeeping branch: 22 commits ahead of main, ready for merge/PR | done | P2 | unassigned | - | - | 2026-07-15 |
| KB-026a | v4.1 Phase 1: Shared SVG→PNG conversion layer (KB-026a) | done | P1 | jan | - | - | 2026-08-08 |
| KB-026b | v4.1 Phase 2: PDF Mermaid diagram rendering (KB-026b) | done | P1 | jan | KB-026a | - | 2026-08-08 |
| KB-026c | v4.1 Phase 3: Verification, docs, release prep (KB-026c) | done | P2 | jan | KB-026b | - | 2026-08-08 |
| KB-027 | HTML: shrink mermaid diagram max-width by 40-50% | done | P1 | jan | - | - | 2026-08-08 |
| KB-028 | PDF: fit diagrams within A4 page boundaries | done | P1 | jan | KB-027 | - | 2026-08-08 |

## WIP Limits
- in-progress: 2
- review: 3

## Rules Snapshot
- Use `rules.md` as source of truth for state mapping and custom policies.
- v5.0 implementation plan: `todo-v5.0.md`
- Historical plans archived in `docs/archive/`

## Notes
- Board initialized from `todo.md` roadmap (2026-07-14); `todo.md` removed, kanban board is now the single source of truth for task state.
- Housekeeping branch has 22 ahead-of-main commits awaiting merge.
- v3.0 work split into 7 phases (KB-007 to KB-013) with dependencies.
- Detailed v3.0 task checklists archived in `docs/archive/todo-v3.0.md`.
- Phase 7 manual PR/push/merge steps and PDF/HTML rendering bugfixes are complete as of 2026-07-27.
- v3.1 work split into KB-014 (Phase 1 shared plumbing, now dropped and replaced by KB-014a/014b/014c/014d), KB-015 (PDF track), KB-016 (HTML track), KB-017 (verification/docs/release prep). KB-014 was too large for context windows and has been decomposed.
- All Phase 1 chunks (KB-014a/014b/014c/014d) are now complete and verified. Moving into Phase 2 (PDF) and Phase 3 (HTML) implementation.
- Phase 2 (KB-015 PDF) and Phase 3 (KB-016 HTML) are now complete.
- Phase 4 (KB-017) verification, documentation, and release prep is complete. All 224 tests pass. Bug fix applied to highlight_code_pdf() grouping logic.
- v3.1 release is ready for finalization.
- v4.0 monolithic card KB-006 superseded by KB-018..KB-025 breakdown (mermaid HTML export). See `docs/archive/todo-4.0.md` for details.
- **Parallelization**: KB-021 (parser: tag mermaid blocks with new token type) and KB-022 (HTML exporter: consume that token + render SVG) can run in parallel once KB-020 (core rendering integration) and the parser contract are agreed. KB-022 depends on both KB-020 and KB-021.
- v4.1 (PDF mermaid) not yet planned; see v4.0 todo for high-level description.
- **KB-019 complete** (Phase 1b): MermanRenderer + bundle infrastructure landed. Real merman-cli binary still needs to be downloaded (see `_download_binaries.py`).
- **KB-020 complete** (Phase 1c): Core merman rendering integration verified. MermanRenderer.render_mermaid_svg() implements subprocess execution with timeout, error handling, theme configuration, batch rendering, and graceful fallback. 22 unit tests pass. Full suite: 266 passed. Next: download real merman-cli binary → KB-021 + KB-022 in parallel.
- **KB-021 complete** (Phase 2a): Parser detects ` ```mermaid ` blocks and tags them as `"mermaid"` type tokens. Case-insensitive, supports tilde fences and info strings. 18 new tests pass.
- **KB-022 complete** (Phase 2b): HtmlExporter consumes "mermaid" tokens, renders via MermanRenderer (batched), embeds inline SVG in `<div class="mermaid">`. Falls back to code block when binary unavailable or `--no-mermaid`. Theme passthrough via `--mermaid-theme`. CSS added for `.mermaid`. 9 new tests pass. Full suite: 293 passed.
- **KB-021 + KB-022 ready**: Parser (tag mermaid blocks with new token type) and HTML exporter (consume token + render SVG) can run in parallel once the parser contract is agreed and KB-020 is complete.
- **KB-023 complete** (Phase 3a): Comprehensive testing landed — 89 new tests across 4 files: test_mermaid_diagram_types.py (10 diagram types, theme passthrough, invalid syntax), test_mermaid_cli_integration.py (7 CLI integration requirements), test_mermaid_airgapped.py (6 air-gapped checks + 2 subprocess tests), test_mermaid_regression.py (heading/paragraph/code/table/list/blockquote/hr regression + full document + edge cases). Full suite: 382 passed. Next: KB-024 documentation.
- **KB-026a complete** (Phase 1): Shared SVG→PNG conversion layer landed in `mdutil/export/svg_to_image.py`. Includes `SvgToImageRenderer` (wraps merman-cli `--outputFormat png`), `get_svg_dimensions()`, and convenience extractors. 40 new tests. Full suite: 429 passed. Ready for KB-026b (PDF mermaid integration).
- **KB-026b complete** (Phase 2): PdfExporter extended to consume `"mermaid"` tokens. Batch-renders diagrams via `SvgToImageRenderer`, embeds PNGs in PDF. Page-break handling, aspect-ratio preservation, error fallback to code block. 7 new PDF mermaid tests in `test_export.py`. Full suite: 437 passed.
- **KB-026c complete** (Phase 3): Verification passed (437 tests green, PDF smoke test with 3 diagrams produces valid 47KB PDF with 2 embedded images). README/spec/CHANGELOG updated with PDF mermaid export docs. Version bumped to 4.1.0. Ready for PR to main.
- **KB-050 complete** (Phase 1a): Parser coverage audit done. 17 features audited: 19 parser gaps found (11 block elements, 8 inline elements supported; 3 block + 6 inline gaps identified). Key finding: inline parser only handles bold/italic/code, 14 features need implementation. Audit report at `docs/phase-1a-audit-report.md`, reusable script at `docs/phase-1a-audit.py`.
- **KB-051 complete** (Phase 1b): Strikethrough `~~text~~` implemented end-to-end. Parser emits `<del>` spans, renderer strips tags for terminal, HTML passes through naturally, PDF uses strikethrough font. 12 tests passing in `test_strikethrough.py`. Commit: 8eedd5a (14 files, 935 insertions). Also fixed: unclosed code fences now treated as code (not paragraph), mermaid block detection reorganized, `--debug` CLI flag added, mermaid config option added.
- **KB-052/053/054 complete** (Phase 1c, remedial): Task list feature fully implemented after discovery that code was never committed despite kanban marking. Parser: `_extract_list` detects `- [ ]`/`- [x]` markers via `_TASK_CHECK_RE`, adds `task`/`checked`/`text` fields to `parsed_items`, sets `task: True` on list token. Renderer: `_render_list` replaces `[ ]`→`☐`, `[x]`/`[X]`→`☑` for task items (mixed lists show checkbox only on task items). HTML: `<input type="checkbox" disabled>` / `checked` for task items. PDF: `☐`/`☑` prefix. 14 new tests in `tests/test_task_list.py`. Full suite: 624 passed.
- **KB-055 complete** (Phase 1d): Parser math notation detection implemented. `$...$` syntax detected in `_parse_inline_segment()`, emits `<math>` tags and `math` span type. Handles escaped `$`, inline code shielding, multiple expressions. 10 tests in `test_math.py`.
- **KB-056 complete** (Phase 1d): Renderer math notation display implemented. Terminal strips `<math>` tags (plain text), HTML uses `<span class="math">` with monospace italic styling, PDF uses mono font. Full suite: 437 passed.
- **KB-057 complete** (Phase 2a): Parser footnote definitions and references implemented. Parser detects `[^n]: text` at document end and emits `footnote_definition` tokens. Inline `[^n]` references emit `<fnref>` tags and `footnote_ref` spans. 16 tests in `test_footnote_parser.py`. Full suite: 427 passed.
- **KB-058 complete** (Phase 2a): Parser footnote references ([^1]) — completed as part of KB-057 (inline ref detection in `_parse_inline_segment`).
- **KB-059 complete** (Phase 2a): Renderer footnotes display implemented. Footnote references rendered as Unicode superscript (¹ ² ³). Footnote definitions rendered as indented text with superscript prefix. 14 tests in `test_footnote_renderer.py`. Full suite: 441 passed. Next: KB-060 (HTML/PDF exporter).
- **KB-060 complete** (Phase 2a): HTML/PDF exporter footnotes implemented. HTML: `<sup><a href="#fn-N">N</a></sup>` refs + `<div class="footnotes">` definitions with back-links. PDF: superscript CID glyphs + horizontal rule separator. 12 tests in `test_footnote_exporter.py`. Full suite: 453 passed. Phase 2a complete. Next: KB-061 (Phase 2b: subscript/superscript syntax).

- **KB-061 complete** (Phase 2b parser): Parser detects `~sub~` and `^super^` syntax in `_parse_inline_segment()`. Emits `<sub>text</sub>` and `<sup>text</sup>` tags with corresponding span types. Escaped `\~` and `\^` are treated as literals. Single delimiters without matching close are treated as literals. 14 parser tests pass.
- **KB-062 complete** (Phase 2b renderer): Renderer converts `<sub>`/`</sub>` tags to Unicode subscript characters (₀-₉, ₐ-ₛ, etc.) and `<sup>`/`</sup>` to Unicode superscript characters (⁰-⁹, ᵃ-ᶻ, etc.). Nested `<strong>`/`<em>`/`<del>`/`<code>`/`<math>` tags within sub/sup are stripped before conversion. Theme keys `subscript` and `superscript` added (`#555555` default). HTML exporter passes `<sub>`/`<sup>` tags through. PDF exporter renders text segments with subscript/superscript chars. Full test file: `tests/test_subscript_superscript.py` (34 tests).
- **KB-063 complete** (Phase 2c parser): Parser detects `==text==` highlight syntax in `_parse_inline_segment()`. Emits `<mark>text</mark>` tags and `highlight` span type. Handles nested inline formatting (bold, em, code, sub, sup), escaped `\==`, unclosed delimiters as literals, and multiple highlights per line. 14 parser tests in `tests/test_highlight.py`.
- **KB-064 complete** (Phase 2c renderer): Terminal renderer uses yellow background (48;2;255;255;0m) via `_highlight_text()` helper in `_strip_inline_tags()`. Theme key `highlight` added to MARKDOWN_COLORS (`#ffff00`). HTML exporter: `<mark>` span type handled in `_render_spans()` + CSS rule added (yellow background, padding, border-radius). PDF: `<mark>` tags stripped (text renders normally). 16 tests in `tests/test_highlight.py`.
- **KB-065 complete** (Phase 3a parser): Parser detects `Term\n:   Definition` syntax via `_extract_definition_list()`. Emits `{"type": "definition", "terms": [...], "definitions": [...]}` tokens. Supports multiple terms sharing a definition, inline formatting in definitions (**bold**, *italic*, `code`, links). 22 new tests in `tests/test_definition_list.py`. Full suite: 616 passed.
- **KB-066 complete** (Phase 3a renderer): Terminal renderer displays definition list with styled term (bold, blue via `definition_term` theme key) and indented definition (via `definition_definition` theme key). HTML exporter renders `<dl>/<dt>/<dd>` with CSS. PDF exporter renders bold term followed by indented definitions with `—` prefix. Full suite: 616 passed.
- **Phase 3a complete.** Next: KB-067 (Phase 3b: image rendering).
- **KB-067 complete** (Phase 3b parser): Parser detects `![alt](url)` image syntax in `_parse_inline_segment()`. Emits `<img src="..." alt="...">` tags and `image` span type with `text` (alt) and `src` fields. Handles escaped `\!`, nested inline formatting in alt text, unclosed delimiters as literals. 11 tests in `tests/test_image.py`. Full suite: 614 passed.
- **KB-068 complete** (Phase 3b renderer): Terminal renderer displays `[image: alt text]` placeholder via `_strip_inline_tags()`. Falls back to `[image: url]` when alt is empty. HTML exporter passes through `<img>` tags. PDF exporter emits `[image: alt text]` placeholder via `_InlineHTMLParser`. HTML exporter `_render_spans` handles `image` span type with `<img>` output. 20 tests in `tests/test_image.py`. Full suite: 614 passed.
- **KB-069 complete** (Phase 3b HTML): HTML exporter emits `<img src="..." alt="...">` with optional `width`/`height` attributes from GFM `=WxH` dimension syntax. CSS rule: `img { max-width: 100%; box-sizing: border-box; }`. 8 new tests. Full suite: 632 passed.
- **KB-070 complete** (Phase 3b PDF): PdfExporter now embeds local images via fpdf2 `pdf.image()` with aspect-ratio preservation. Dimension hints `=WxH` used for scaling. Remote URLs and missing files fall back to `[image: alt]` placeholder text. 2 new tests. Full suite: 632 passed.
