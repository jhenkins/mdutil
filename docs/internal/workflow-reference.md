# mdutil Workflow Reference

**Purpose:** Single reference for how tasks flow from planning to completion in mdutil development.

---

## Sources of Truth (exactly 2 documents)

| Document | Purpose |
|----------|---------|
| `.kanban/board.md` | Kanban board — card state, dependencies, priorities, completion notes |
| `todo-v5.0.md` | Implementation plan — detailed per-KB task checklists for active work |

Historical plans (v3.0/v3.1/v4.0) are archived in `docs/archive/` and are **not** sources of truth. `todo.md` is removed.

**Before any task work:** Read `.kanban/board.md` to know what's in progress and what's done.

---

## Workflow: Backlog → Done

```
backlog → ready → in-progress → review → done
```

| State | What it means | What's required to move forward |
|-------|---------------|--------------------------------|
| **backlog** | Planned, not started | Move to `ready` when dependencies are met |
| **ready** | Approved, dependencies met, ready to start | Move to `in-progress` when you start work |
| **in-progress** | Actively being worked on | Move to `review` when implementation is complete and **all tests pass** |
| **review** | Work complete, awaiting review/merge | Move to `done` after PR is merged and verified |
| **done** | Merged and verified | — |

**WIP limits:** 2 cards in `in-progress` at a time, 3 in `review`.

---

## The Verification Gate

**`bin/verify-phase`** is the local safety net. It replaces CI/CD for this project size.

It runs before moving any KB from `in-progress` to `review` or `done`:

```bash
./bin/verify-phase
```

What it does:
1. Checks that `python3` and `pytest` are available (exit 2 if not)
2. Runs `python3 -m pytest -q` against the full test suite
3. Reports pass/fail with clear output

**Exit codes:**
- `0` — all tests pass → phase is verified, safe to move to `done`
- `1` — test failures detected → **do not** mark KB as done, fix first
- `2` — no Python/pytest environment → set up environment first

---

## Per-KB Commit Discipline

**Each KB lands as its own commit.** No monolithic commits.

Commit message format: `KB-XXX: <feature name>`

Examples:
```
KB-071: Parser link title attribute
KB-072: Exporter link title rendering
```

Never: "finish all", "add feature", "WIP", etc.

**Why:** The git log becomes a reliable troubleshooting resource. A failing commit immediately identifies which KB is broken.

---

## Kanban `done` Transition Rule

A card may only be moved to `done` when **all three** are true:

1. ✅ All implementation code for that KB is committed (own commit, per above)
2. ✅ `./bin/verify-phase` passes with zero failures
3. ✅ No test file exists without corresponding implementation

---

## Example: Finishing KB-071

```
1. Implement parser changes in mdutil/parser.py
2. Write/update tests for link title parsing
3. Run: ./bin/verify-phase  → must pass with 0 failures
4. Commit: git commit -m "KB-071: Parser link title attribute"
5. Move card from in-progress to review in .kanban/board.md
6. (Optionally) Move to done after PR merge + re-run verify-phase
```

---

## Quick Reference

```bash
# Before declaring any KB done:
./bin/verify-phase

# Commit discipline:
git commit -m "KB-XXX: <feature name>"

# Check what's next:
cat .kanban/board.md | grep -E "backlog|ready|in-progress"
```

---

## What Changed From Before

| Before | After |
|--------|-------|
| `todo.md` + `todo-v3.0.md` + `todo-v3.1.md` + `todo-4.0.md` + kanban board | Kanban board + `todo-v5.0.md` only |
| No automated test gate | `./bin/verify-phase` mandatory before `done` |
| Monolithic commits ("finished all") | One commit per KB |
| Understory MCP active | Disabled, no token waste |
| Vague commit messages | `KB-XXX: <feature name>` required |

---

## In Practice

When you start a new session:
1. Read `.kanban/board.md` to see what's in progress
2. Pick a card from `ready` (or move one from `backlog`)
3. Implement the KB per `todo-v5.0.md` checklist
4. Run `./bin/verify-phase` before committing
5. Commit with `KB-XXX: <feature name>` format
6. Move card to `review` (or `done` after merge)

That's the whole workflow.

---

**Document location:** `docs/internal/workflow-reference.md`  
**Kanban rules:** `.kanban/rules.md` (short version of this document)  
**AGENTS.md:** `/home/jan/.pi/agent/AGENTS.md` (global agent instructions referencing this workflow)
