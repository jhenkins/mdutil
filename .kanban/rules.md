# mdutil Kanban Rules

## State Mapping

| Kanban State | Description |
|-------------|-------------|
| `backlog` | Planned but not yet ready for work |
| `ready` | Approved, dependencies met, ready to start |
| `in-progress` | Actively being worked on |
| `blocked` | Cannot proceed — has unmet blockers |
| `review` | Work complete, awaiting review/merge |
| `done` | Merged and verified |

## WIP Limits
- **in-progress**: 2
- **review**: 3

## GitHub Issues Policy

Normal development work (feature requests, bug fixes, refactors, KB cards) is **not** tracked via GitHub issues. The Kanban board (`board.md` + `rules.md`) and `todo-v5.0.md` are the single source of truth for what to work on.

GitHub issues are only worth looking at if someone externally logs one for us to triage — and even then it is a case-by-case decision, not how we work as a rule. Do not spend time searching GitHub issues for normal task tracking; the answers live in the board.

## Policies
- Move to `review` when implementation is complete and all tests pass.
- Only one card per developer in `in-progress` at a time.
- `blocked` cards must have a `depends_on` field populated.
- Move to `done` only after PR is merged and verified.
- **MANDATORY:** Run `./bin/verify-phase` before any `done` transition. Zero failures required.
- **MANDATORY:** Each KB is its own commit. No monolithic commits.

## References
- Kanban board (source of truth for task state): this file + `board.md`
- Implementation plan (active work): `todo-v5.0.md`
- Full workflow reference: `docs/internal/workflow-reference.md`
- Archived plans: `docs/archive/`
- GitHub issue: [#50](https://github.com/jhenkins/mdutil/issues/50)
