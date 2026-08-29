# Internal Documentation

This folder holds the **development and agent-internal** records for mdutil. It is **not** user-facing.

## Audience

These documents are for people working on the project (and the agents that assist it) — not for end users.
User-facing documentation lives in the repository root:

- `README.md` — what end users read (installation, usage, features)
- `CHANGELOG.md` — release history
- `mdutil-specification.md` — program specification (the top sections are user-relevant; deeper
  architecture sections are for maintainers)

If you are looking for how to *use* mdutil, stop here and open `README.md`.

## Contents

| File | What it is |
|------|-----------|
| `workflow-reference.md` | How the project is developed (kanban rules, branching, test-gated workflow) |
| `user-docs-plan.md` | Plan for building the user-facing documentation system |
| `phase-1a-audit-report.md`, `phase-1a-audit.py` | Parser coverage audit (v5.0 kickoff) and its reusable script |
| `phase-1-continuation.md`, `phase-0-completion.md` | Early v5.0 phase notes |
| `kb-057-footnote-parser.md`, `kb-058-059-footnote-renderer.md`, `kb-060-footnote-exporter.md` | Per-KB footnote implementation notes |
| `KB-014b-design.md`, `KB-014-trace-annotation.*` | v3.1 export-highlighting design + trace annotations |
| `KB-026-v4.1-planning.md` | v4.1 PDF-mermaid planning |
| `postmortem-phase-1c-missing-implementation.md`, `postmortem-reply.md` | Post-mortem of a committed-but-unimplemented feature |
| `task-list-remedial-plan.md` | Remedial plan for the task-list detection gap |
| `debug-plan-html-diagram-sizing.md`, `debug-plan-pdf-diagram-sizing.md` | Mermaid diagram sizing debug plans |
| `mermaid-research.md` | Mermaid rendering research |
| `manual-qa.md` (+ `.pdf`) | Manual QA notes and rendered report |

## Historical plans

Completed version plans (v3.0, v3.1, v4.0) live in [`../archive/`](../archive/). They are kept for
reference but are no longer active. The single source of truth for current work is:

- `.kanban/board.md` — task tracking (kanban board with card state, dependencies, WIP limits)
- `todo-v5.0.md` — implementation plan for active development
