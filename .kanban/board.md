# mdutil Kanban Board

## Meta
project_id: mdutil
board_version: 4.3
updated: 2026-08-24 12:00
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
| KB-071 | v5.0 Phase 4a: Parser link title attribute | done | P1 | jan | - | KB-050 | 2026-08-21 |
| KB-072 | v5.0 Phase 4a: Exporter link title rendering | done | P1 | jan | - | KB-071 | 2026-08-21 |
| KB-073 | v5.0 Phase 5a: Parser nested list structure preservation | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-074 | v5.0 Phase 5a: Tests for nested list nesting | done | P1 | jan | - | KB-073 | 2026-08-22 |
| KB-075 | v5.0 Phase 6a: Theme support for new inline styles | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-076 | v5.0 Phase 6a: Config support for new features | done | P1 | jan | - | KB-075 | 2026-08-22 |
| KB-077 | v5.0 Phase 7a: Parser tests for new syntax | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-078 | v5.0 Phase 7a: Renderer tests for new features | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-079 | v5.0 Phase 7a: Exporter tests for new features | done | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-080 | v5.0 Phase 7a: CLI integration tests | done | P1 | jan | - | KB-050 | 2026-08-17 |
| KB-081 | v5.0 Phase 7b: README documentation update | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-082 | v5.0 Phase 7b: Specification documentation update | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-083 | v5.0 Phase 7b: Changelog documentation update | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-084 | v5.0 Phase 7b: Fixture and golden file updates | done | P1 | jan | - | KB-050 | 2026-08-22 |
| KB-085 | v5.0 Phase 8a: Full test suite verification | done | P1 | jan | - | KB-077, KB-078, KB-079, KB-080 | 2026-08-22 |
| KB-086 | v5.0 Phase 8a: Manual QA with real documents | done | P1 | jan | - | KB-085 | 2026-08-23 |
| KB-087 | v5.0 Phase 8a: Performance testing | done | P1 | jan | - | KB-085 | 2026-08-23 |
| KB-088 | v5.0 Phase 8b: Version bump to 5.0.0 | done | P1 | jan | - | KB-086, KB-087 | 2026-08-23 |
| KB-089 | v5.0 Phase 8b: Release PR creation | in-progress | P1 | jan | - | KB-088 | 2026-08-23 |
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
| KB-090 | Terminal: differentiate heading levels h1–h6 (colour + bold weight) | done | P1 | jan | - | - | 2026-08-24 |
| KB-091 | Terminal: differentiate callout blockquotes from regular blockquotes | backlog | P2 | - | - | - | 2026-08-23 |
| KB-092 | Terminal: strikethrough font (not just darker colour) | dropped | P2 | - | - | KB-103 | 2026-08-24 |
| KB-093 | Terminal: inline code visual styling (mono font, background) | done | P1 | jan | - | - | 2026-08-24 |
| KB-094 | PDF: ***bold and italic*** renders raw markdown instead of bold+italic | backlog | P1 | - | - | - | 2026-08-23 |
| KB-095 | Docs: fix "Math" → "maths" (UK English) | done | P3 | jan | - | - | 2026-08-23 |
| KB-096 | PDF: superscript ² not rendered in table cells | backlog | P1 | - | - | - | 2026-08-23 |
| KB-097 | PDF: definition list alignment (Def. 1.2 not aligning with Def. 1.1) | backlog | P2 | - | - | - | 2026-08-23 |
| KB-098 | PDF: subscript/superscript not rendered (H2O, E=mc2) | backlog | P1 | - | - | - | 2026-08-23 |
| KB-099 | PDF: math notation renders as raw LaTeX instead of formatted | backlog | P1 | - | - | - | 2026-08-23 |
| KB-100 | HTML: syntax highlighting colours do not match PDF/markdown | backlog | P2 | - | - | - | 2026-08-23 |
| KB-101 | HTML: math notation disappears entirely | backlog | P1 | - | - | - | 2026-08-23 |
| KB-102 | Parser: ***bold-italic*** leaves trailing asterisk (only 2 of 3 consumed) | done | P1 | jan | - | - | 2026-08-24 |
| KB-103 | Terminal: strikethrough should use ANSI \\033[9m (actual strikethrough), not just colour | done | P1 | jan | - | - | 2026-08-24 |

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

- **KB-071 complete** (Phase 4a parser): Parser now extracts link title attributes from `[text](url "title")` syntax. `_parse_link_attributes()` helper extracts title from double/single-quoted strings. Link span tokens include `title` field. Inline HTML output includes `title` attribute with HTML-escaped values. 20 new tests. Full suite: 665 passed.

- **KB-072 complete** (Phase 4a exporters): HTML exporter renders `title` attribute on `<a>` tags. PDF exporter's `_InlineHTMLParser` extracts `title` from `<a>` tags and stores in segments. `_render_inline_html` uses `pdf.link()` with `title` parameter for annotations with titles. 13 new tests. Full suite: 665 passed.

- **KB-073 complete** (Phase 5a parser): Nested list support implemented end-to-end. Parser `_extract_list` now detects nested items by indentation level (up to 8 spaces), recursively parses sub-lists, and attaches them to parent items via `sub_list` field. Supports mixed ordered/unordered nesting at any depth. Renderer, HTML exporter, and PDF exporter all updated to recurse into `sub_list` with proper indentation. 20 new tests. Full suite: 685 passed.

- **KB-074 complete** (Phase 5a tests): 20 tests covering 1-3 levels of nesting, mixed ordered/unordered nesting, nested lists with inline formatting (bold, italic, code), nested task lists, and blank-line separation between separate list groups. All 685 tests pass.

- **KB-075 complete** (Phase 6a themes): Extended theme system with 3 new inline-style keys: `strikethrough`, `task_list_checked`, `task_list_unchecked` added to `MARKDOWN_COLORS`. All 4 built-in themes (colored, dracula, high-contrast, one-dark) now have values for all 8 inline-style keys (`strikethrough`, `subscript`, `superscript`, `highlight`, `task_list_checked`, `task_list_unchecked`, `definition_term`, `definition_definition`). Renderer: `<del>` tags styled with strikethrough color; checkbox symbols (`☐`/`☑`) colored via theme keys. PDF exporter: `_render_definition` uses `definition_term`/`definition_definition` theme colors. HTML exporter: CSS for `mark`, `dl dt`, `dl dd`, and `del/s` now theme-driven. 685 tests passing.

- **KB-076 complete** (Phase 6a config): Added `--math-fallback` (bool) and `--footnote-style` (`numbered`|`bracketed`) CLI flags and matching `math_fallback`/`footnote_style` INI config keys. Renderer: `math_fallback=True` preserves `$...$` delimiters around math; `footnote_style=bracketed` renders `[^1]` as `[1]` instead of superscript. All options thread from CLI → config → `render()`. 15 new tests (config, renderer, CLI). 700 tests passing.

- **KB-077 complete** (Phase 7a parser tests): 41 tests across 10 test classes covering all new syntax: strikethrough (4), math (4), footnote (3), sub/superscript (5), highlight (4), definition list (3), image (2), task list (2), nested list (2), link title (4), cross-feature (3), parser interactions (5). Added `tests/test_parser_comprehensive.py`. 779 tests passing.

- **KB-078 complete** (Phase 7a renderer tests): 38 tests across 9 test classes covering theme colors (7), math fallback (3), footnote styles (3), cross-feature rendering (6), images (3), definition lists (2), complex documents (7), fallback behaviors (4), unicode (3). Also fixed a bug in `_strip_inline_tags()` where the `<a>` tag regex didn't handle `title` attributes after `href`. Added `tests/test_renderer_comprehensive.py`. 779 tests passing.
- **KB-079 complete** (Phase 7a exporter tests): 83 tests across 14 test classes covering HTML and PDF exporters for all v5.0 features: strikethrough (`<del>`), task lists (checkboxes), math (`<math>`), footnotes (ref + definition), subscript (`<sub>`), superscript (`<sup>`), highlight (`<mark>`), definition lists (`<dl>/<dt>/<dd>`), images (`<img>` with dimensions), nested lists (recursive), link titles (`title` attr), PDF `_InlineHTMLParser` span handling, and cross-format consistency. Added `tests/test_export_v5_features.py`. 862 tests passing.
- **KB-080 complete** (Phase 7a CLI integration tests): 32 tests across 5 test classes covering CLI-to-exporter pipeline with v5.0 features: `--math-fallback` flag behavior (terminal + export), `--footnote-style` flag (numbered/bracketed), multi-format export with new features, config file integration (`math_fallback`/`footnote_style`), and end-to-end document rendering. Added `tests/test_cli_v5_integration.py`. 894 tests passing.
- **KB-086 complete** (Phase 8a manual QA): Tested with 5 real-world documents across 4 themes (colored, dracula, high-contrast, one-dark) and 4 terminal widths (80, 120, 160, 200). All v5.0 features render correctly. Found and fixed 3 bugs: (1) footnote ID regex only matched digits — fixed in renderer, HTML/PDF exporters; (2) consecutive footnote definitions merged into single paragraph — fixed in parser; (3) PDF `_superscript` had incorrect Unicode mappings — fixed by delegating to renderer. Added regression tests. Full report at `tests/qa/qa-report-v5.0.md`. 896 tests passing.

- **KB-087 complete** (Phase 8a performance): 24 performance tests in `tests/test_performance.py` across 5 test classes. Baselines established: parse 0.86ms–40ms (5K–250K, linear scaling confirmed), terminal render 0.23ms–15ms, HTML export 0.81ms–31ms, PDF export 220ms–657ms (5K–50K). V5-specific tests: many footnotes (50 refs), many task items (100), dense inline formatting (200 lines), deep nesting (10 levels). 3 cProfile-based profiling tests available for regression investigation. 920 tests passing.

### Rendering Quality (KB-090 to KB-101)

- **KB-090 complete** (Phase rendering): Terminal headings now have level-appropriate visual hierarchy. h1 renders with bold + colour + `═` underline, h2 with bold + colour + `─` underline, h3–h6 with bold + colour only. All 4 themes (colored, dracula, high-contrast, one-dark) now have distinct colours per heading level (6 unique colours each). 34 new tests in `tests/test_heading_differentiation.py`. 973 tests passing. Commit: 16c9d92 (9 files, 463 insertions).
- **KB-091**: Terminal callout blockquote — no visual difference between `>` and `> [!NOTE]`. Consider prefix or border.
- **KB-092**: Terminal strikethrough — currently only darker colour, no combining macron or similar.
- **KB-093 complete**: Added `inline_code` theme key (#e8e8e8 default) with background styling via ANSI `48;2;R;G;B`. All 4 themes updated. 19 new tests in `tests/test_inline_code.py`. 939 tests passing.
- **KB-094**: PDF `***bold and italic***` renders raw `***` markdown.
- **KB-095**: Typo "Math" → "maths" (UK English).
- **KB-096**: PDF superscript `²` not rendered in table cells.
- **KB-097**: PDF definition list alignment — "Definition 1.2" not aligned with "Definition 1.1".
- **KB-098**: PDF subscript/superscript not rendered (H~2~O shows as H2O, mc^2^ shows as mc2).
- **KB-099**: PDF math notation renders as raw LaTeX instead of formatted.
- **KB-100**: HTML syntax highlighting colours do not match PDF/markdown output.
- **KB-101**: HTML math notation disappears entirely (empty).
- **KB-102 complete** (bold-italic parser): Parser now checks `***` before `**`, so `***text***` renders as `<strong><em>text</em></strong>` without trailing `*`. Also handles `___text___` underscore variant. 14 new tests. Commit: 0708cb1.
- **KB-103 complete** (strikethrough ANSI): Terminal renderer now wraps `~~text~~` with ANSI `\033[9m` (STANDOUT ON) and `\033[29m` (STANDOUT OFF) escape sequences, producing actual visual strikethrough in terminals that support it (VIM, iTerm2, GNOME Terminal, etc.). Colour + strikethrough applied together. Replaces KB-092 (which was the backlog card for the same problem). 13 strikethrough tests + 1000 total passing. Commits: `705a947` (renderer fix) + `794fa04` (fixture restore).
