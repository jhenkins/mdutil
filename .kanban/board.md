# mdutil Kanban Board

## Meta
project_id: mdutil
board_version: 4.4
updated: 2026-08-28 21:40
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
| KB-089 | v5.0 Phase 8b: Release PR creation | done | P1 | jan | - | KB-088 | 2026-08-28 |
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
| KB-091 | Terminal: differentiate callout blockquotes from regular blockquotes | done | P2 | jan | - | - | 2026-08-26 |
| KB-092 | Terminal: strikethrough font (not just darker colour) | dropped | P2 | - | - | KB-103 | 2026-08-24 |
| KB-093 | Terminal: inline code visual styling (mono font, background) | done | P1 | jan | - | - | 2026-08-24 |
| KB-094 | PDF: ***bold and italic*** renders raw markdown instead of bold+italic | done | P1 | jan | - | - | 2026-08-24 |
| KB-095 | Docs: fix "Math" → "maths" (UK English) | done | P3 | jan | - | - | 2026-08-23 |
| KB-096 | PDF: superscript ² not rendered in table cells | done | P1 | jan | - | - | 2026-08-24 |
| KB-097 | PDF: definition list alignment (Def. 1.2 not aligning with Def. 1.1) | done | P2 | jan | - | - | 2026-08-26 |
| KB-098 | PDF: subscript/superscript not rendered (H2O, E=mc2) | duplicate | P1 | - | - | KB-096 | 2026-08-24 |
| KB-099 | PDF: math notation renders as raw LaTeX instead of formatted | done | P1 | jan | - | - | 2026-08-25 |
| KB-100 | HTML: syntax highlighting colours do not match PDF/markdown | done | P2 | jan | - | - | 2026-08-27 |
| KB-101 | HTML: math notation disappears entirely | done | P1 | jan | - | - | 2026-08-25 |
| KB-102 | Parser: ***bold-italic*** leaves trailing asterisk (only 2 of 3 consumed) | done | P1 | jan | - | - | 2026-08-24 |
| KB-103 | Terminal: strikethrough should use ANSI \\033[9m (actual strikethrough), not just colour | done | P1 | jan | - | - | 2026-08-24 |
| KB-104 | PDF/HTML: block-level math ($$...$$) leaks into inline parsing instead of rendering as a display block | done | P1 | jan | - | - | 2026-08-27 |
| KB-105 | Terminal: list items in Kanban board now render bold/italic/code | done | P1 | jan | - | - | 2026-08-28 |

## WIP Limits
- in-progress: 2
- review: 3

## Rules Snapshot
- Use `rules.md` as source of truth for state mapping and custom policies.
- **GitHub issues are NOT used for normal development work** (see `rules.md`). Work is tracked on this board + `todo-v5.0.md`. Only triage externally-logged issues on a case-by-case basis.
- v5.0 implementation plan: `todo-v5.0.md`
- Historical plans archived in `docs/archive/`

## Notes

- Board initialized from `todo.md` roadmap (2026-07-14); `todo.md` removed. The board is the single source of truth for task state (see `.kanban/rules.md`).
- Detailed per-KB completion history (commit hashes, per-card test counts, in-flight decisions) is archived in `.kanban/archive/board-history.md` — kept as an agent record, not shown on the live board.
- The same history is captured in the per-KB git commits (`KB-XXX: ...`).

## Completed phases (summary)

- **v3.0** (KB-007–KB-013): PDF + HTML export, CLI & configuration. Released 2026-07-27.
- **v3.1** (KB-014a–KB-017): Syntax highlighting in exports. Released.
- **v4.0** (KB-018–KB-025): Mermaid diagram export (HTML) with bundled air-gapped binary. Released 2026-08-06.
- **v4.1** (KB-026a–KB-028): Mermaid export to PDF, diagram sizing fixes. Released 2026-08-08.
- **v5.0** (KB-050–KB-088): GFM/CommonMark features — strikethrough, task lists, math, footnotes, subscript/superscript, highlight, definition lists, images, link titles, nested lists. Released 2026-08-22.
- **Rendering quality** (KB-090–KB-105): Heading hierarchy, GFM callouts, inline-code styling, block/display math, bold-italic, PDF math & superscript, HTML syntax-colour consistency. Complete.

The full test suite (~1060 tests) is green. All planned work is complete; remaining board items are future enhancements.
