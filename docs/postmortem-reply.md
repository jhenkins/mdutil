# Postmortem: Comments by user

**Date:** 2026-08-21
**Affected:** KB-052, KB-053, KB-054 (Phase 1c: Task Lists)
**Duration of failure:** ~3 days (Aug 18 – Aug 21, 2026)

---

## Root Cause Analysis

### 1. Monolithic "finish everything" commit

Commit `6487760` attempted to deliver Phase 1c through Phase 2a in a single commit (15 files, 1638 insertions). The commit message claimed completion of everything, but the actual work only covered footnotes and math. Phase 1c (task lists) was silently skipped.

**Why this is dangerous:** Large commits are hard to review, easy to have gaps in, and create a false sense of completeness. A commit message saying "finished all" is not verifiable — you have to read every line of every file to confirm.

User comment: This is a good assessment.

### 2. No CI/CD pipeline

There is **zero** automated test execution. No GitHub Actions workflow, no pre-commit hook, no post-merge validation. The test suite (`pytest`) runs only when a human manually invokes it.

**Impact:** After commit `6487760`, nobody ran `pytest tests/test_task_list.py`. The 10 failing tests went undetected for 3 days. If a CI pipeline had run the full suite on every push, the red CI badge would have been visible within minutes.

User comment: If this was a large project that involved many people, this would have been a very valid point. However, since this is a small utility (mdutil) project that involves a single human with an AI assistant, a CI/CD pipeline would be complete overkill. Having said that, the sentiment is good because there is no automated safety-net that would have been given by a CI/CD pipeline.

### 3. Kanban state has no verification gate

The kanban board (`.kanban/board.md`) and `todo-v5.0.md` are plain markdown files. "Done" is whatever the human writes — there is no enforcement that:
- Tests exist for the claimed feature
- Tests pass
- Implementation code exists
- The feature works end-to-end

**Impact:** A human could check "done" on a kanban card without actually verifying the work was complete. The kanban became a planning document, not a source of truth.

User comment: Again, this is a small project, having this level of oversight would be massive overkill. The "human" component in this partnership would not check "done" if there was any doubt.

### 4. No test-gated completion workflow

There is no process that links "KB-052 is done" to "run `pytest tests/test_task_list.py` and verify all pass." The tests were written and committed, but no completion check ever ran them.

**Impact:** Writing tests is easy. Running them as part of the completion gate is what separates "I wrote tests" from "the feature works."

User comment: This looks like useful comment, we should have a closer look at this because for a small project like this, tests will help. A great many tests have been written and is being run often by the AI assistant, but the process can be enhanced to have this done more often. This needs closer scrutiny, because at this point we can potentially catch a lot of what went wrong.


### 5. Downstream work compounded the error

KB-055 through KB-068 were implemented in subsequent commits (Aug 18–20). Each commit added more code on top of the broken foundation without running `pytest -q` against the full suite. The 10 silent failures were further masked by:
- More passing tests from later KBs
- No regression check against earlier phases
- No full-suite run to surface the gap

User comment: This is very closely related to point 4, see user comment.


---

## Impact

| Metric | Value |
|--------|-------|
| Duration of undetected failure | ~3 days |
| Number of silently failing tests | 10 of 14 |
| Downstream KBs built on broken foundation | KB-055 through KB-068 (14 KBs) |
| Remedial work required | 4 files modified, 14 tests verified |


---

## Preventive Measures

### Tier 1: Highest leverage (implement first)

#### 1. Add a CI pipeline

A GitHub Actions workflow that runs the full test suite on every push to `feature/v5.0-rendering` and `main`.

**Impact:** Would have caught this failure within minutes of commit `6487760`. The red CI badge is impossible to ignore and requires no human process change.

**Effort:** ~30 minutes to set up `.github/workflows/test.yml`.

**Recommended configuration:**
```yaml
name: Tests
on:
  push:
    branches: [main, 'feature/**']
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: python -m pytest -q
```

User comment: While it would be interesting to get CI/CD going for this project from a technical perspective, it would in fact be massive over-engineering. This project is a small utility, not a framework for a large corporate SaaS framework - therefore this is not needed. An alternative, more proportional approach is needed.

#### 2. Replace monolithic commits with per-KB commits

Each KB should land as its own commit, with its tests passing. This makes it impossible to claim "finished all" while skipping half of it.

**Example:**
- Commit 1: `KB-052: Parser task list detection` — parser changes + `test_parse_task_list_*` tests passing
- Commit 2: `KB-053: Renderer task list display` — renderer changes + `test_render_task_*` tests passing
- Commit 3: `KB-054: Exporter task list rendering` — HTML/PDF changes + exporter tests passing

**Impact:** Each commit is verifiable in isolation. A failing commit immediately identifies which KB is broken.

User comment: This seems like a generally good idea, because the GIT log is genuinely useful in the case of troubleshooting.


### Tier 2: Process improvements

#### 3. Test-gated kanban transitions

When moving a card from `in-progress` to `done`, the relevant tests must pass. This can be:
- **Manual:** A checklist item in the kanban rules ("verify `pytest tests/test_task_list.py` passes before moving to done")
- **Automated:** A script that reads the kanban board and runs tests for all `done` cards, reporting failures

User comment: I agree with this, it is at this point where the most work-flow value can be created. 

#### 4. Feature coverage verification script

A script that reads `todo-v5.0.md` (or the kanban) and verifies:
- For each "done" KB, does the corresponding test file exist?
- Do those tests pass?
- Is there a test file without corresponding implementation?

Run this before declaring a phase complete.

User comment: This is a TDD cornerstone, let's make it part of work-flow.

#### 5. Phase completion checklist

Before marking a phase as complete, verify:
- All KBs in the phase have passing tests
- Full test suite passes (no regressions from earlier phases)
- No test file exists without corresponding implementation code
- No test is silently skipped or marked `xfail`

User comment: Same as previous point.

### Tier 3: Cultural changes

#### 6. "Test first, commit second" discipline

Write tests before implementation. If tests exist but fail, the gap is visible. If implementation exists but tests don't, the feature is unverified. Both states are better than the current state (tests exist, implementation missing, nobody checking).

#### 7. Commit message verification

Commit messages should reference specific KB numbers, not vague "finished all" claims. A commit message like "KB-052: Parser task list detection" is verifiable. "Finished all up to KB-060" is not.

---

## Recommendations

1. **Implement CI pipeline immediately** — highest leverage, lowest effort, catches everything.

User comment: No - overkill for this project.

2. **Adopt per-KB commits** — makes each commit verifiable and prevents monolithic gaps.

User comment: Yes.

3. **Add a phase completion script** — run before declaring any phase done: verify all KBs have passing tests.

User comment: Yes.

4. **Update kanban rules** — add "tests must pass" as a requirement for moving to `done`.

User comment: Yes.

---

Further user comments:

The documentation and task-tracking effort for this project is not good. There are too many documents that needs to be kept up to date, which distracts from the code. Each update spawns multiple processes for updating the Kanban board as well as multiple Todo documents. This not only wastes precious context window tokens, but creates multiple areas where our task-tracking can go wrong. Add to this the Understory MCP server that is underperforming, we are sitting with a situation that can be called a "perfect storm in the making". Therefore the following points needs careful consideration:

* We need to remove the need for multiple Todo documents, and transform the task-tracking burden to either just the Kanban board, or the Kanban board supported by at most one other document. Having the todo.md as well as the todo-v5.0.md (or similar) is clumsy, and slows down the process considerably. It also increases the probability of another task-slip by an order of magnitude.
* We should disable the Understory MCP server at this point, because it adds no value. In it's place, we need to simply rely on the following on proper AGENT.md entries that points to the relevant Kanban and todo resources. Too much time and tokens are spent on rediscovering the proper resources.
* We need to consider how to kick off automated tests locally without having to rely on CI/CD. This is where the biggest win will be.

