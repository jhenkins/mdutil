# Remedial Plan: Task List Feature (KB-052/053/054)

## Status

**✅ COMPLETED 2026-08-21.**

KB-052, KB-053, and KB-054 were marked done on the kanban board, but the actual implementation code was never committed. This plan remediated that gap.

All 14 tests in `tests/test_task_list.py` now pass. Full suite: 624 passed.

---

## What the tests expect

The tests define a clear contract. Here's the spec the code needs to implement:

### 1. Parser — `_extract_list` in `mdutil/parser.py`

A list token with task list items must have:
- `"task": True` on the list token if **any** item matches `[ ]` or `[x]`/`[X]`
- `"task": False` on the list token if no items have checkboxes
- Each `parsed_item` dict must have:
  - `"checked": True` for `[x]`/`[X]`, `False` for `[ ]`
  - `"task": True` for items with checkboxes, `False` for regular items
  - `"text"` — the raw item text **after** stripping the `[ ]`/`[x]` prefix
  - `"content"` — inline-parsed HTML tags (e.g. `<strong>bold</strong>`)

Detection pattern: `- [x] text` or `- [ ] text` (space required inside brackets).

Works with both unordered (`-`, `*`, `+`) and ordered (`1.`, `2.`) list syntax.

### 2. Renderer — `_render_list` in `mdutil/renderer.py`

When the token has `"task": True`:
- `[ ]` → `☐`
- `[x]` / `[X]` → `☑`

Regular lists must remain unchanged (no checkbox characters).

### 3. HTML Exporter — `_render_list` in `mdutil/export/html.py`

Task list items render with HTML checkboxes:
- Unchecked: `<input type="checkbox" disabled>`
- Checked: `<input type="checkbox" checked disabled>`

Text content follows the checkbox.

### 4. PDF Exporter — `_render_list` in `mdutil/export/pdf.py`

Use Unicode `☐` / `☑` (similar to terminal renderer). Already has a passing test that just validates the PDF is produced.

---

## Implementation steps

### Step 1: Detect task list syntax in the parser

In `_extract_list()` (around line 283 in `parser.py`):

```python
import re

_TASK_CHECK_RE = re.compile(r"^\s*\[([ xX])\]\s+(.*)")

# Inside the loop over raw_items:
task_match = _TASK_CHECK_RE.match(raw_item)
if task_match:
    checked = task_match.group(1).lower() == "x"
    item_text = task_match.group(2)
else:
    checked = None
    item_text = raw_item
```

Then determine if the whole list is a task list:
```python
has_task = any(
    _TASK_CHECK_RE.match(item) for item in raw_items
)
```

### Step 2: Populate `parsed_items` with task metadata

For each item, include `checked` and `task` fields alongside `text` and `content`.

### Step 3: Update renderer `_render_list`

Detect `"task": True` on the token. When rendering each item, check if it starts with `[ ]` or `[x]`/`[X]` and replace accordingly. Use Unicode: `☐` (U+2610) and `☑` (U+2611).

### Step 4: Update HTML exporter `_render_list`

Detect task items in `parsed_items`. When `item["task"]` is True, render `<input type="checkbox"` instead of the raw `-` prefix.

### Step 5: Update PDF exporter `_render_list`

Same as renderer — use `☐` / `☑` Unicode characters as prefix before each task item.

### Step 6: Run tests

```bash
python -m pytest tests/test_task_list.py -v
```

Expected: 14 passed, 0 failed.

### Step 7: Run full suite

```bash
python -m pytest -q
```

Expected: 0 failures (was 10 before, all in test_task_list.py).

---

## Files to modify

| File | Changes |
|------|---------|
| `mdutil/parser.py` | `_extract_list`: detect `- [ ]`/`- [x]`, add `checked`/`task` to parsed_items, set `task` flag on token |
| `mdutil/renderer.py` | `_render_list`: replace `[ ]`/`[x]` with `☐`/`☑` when token has `task` flag |
| `mdutil/export/html.py` | `_render_list`: emit `<input type="checkbox">` for task items |
| `mdutil/export/pdf.py` | `_render_list`: prefix task items with `☐`/`☑` |

## Tests already written (do not modify)

`tests/test_task_list.py` — 14 tests covering parser, renderer, HTML exporter, PDF exporter. These tests were written before implementation and define the contract. Do not change them.

## Risks

1. **Ordered lists**: The current `_extract_list` enforces that all items must be the same type (ordered/unordered). Task items use `- [x]` which matches the unordered regex, but `1. [ ]` uses ordered regex. Need to verify `_LIST_RE` pattern handles both.
2. **Mixed lists**: The test expects mixed regular + task items in the same list. The current `_extract_list` returns a single list token — mixed items just need the `task` flag set on the list and per-item.
3. **Inline formatting**: The test `test_parse_task_list_with_inline_formatting` expects `content` to contain parsed HTML (`<strong>`, `<em>`). The current code already calls `_parse_inline` on each item, so this should work automatically once the checkbox prefix is stripped.

---

## Kanban board update (after completion)

- Move KB-052, KB-053, KB-054 from `done` to verified status (or leave as `done`)
- Update board notes to reference this implementation
- Update `todo-v5.0.md` to check off Phase 1c
