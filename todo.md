# mdutil TODO

Last updated: 2026-06-05
Current branch: `housekeeping`
Current package version: `1.5.1`
Baseline verification at update time: `python -m pytest -q` -> 86 passed in 2.64s

## Current state

`mdutil` is currently a functional terminal Markdown viewer written in Python. The current implementation includes:

- File input and stdin input (`mdutil file.md`, `mdutil -`, and piped stdin).
- ANSI Markdown rendering for headings, paragraphs, lists, blockquotes, tables, horizontal rules, and code blocks.
- Pygments-backed syntax highlighting with fallback to plain text for unknown or missing languages.
- Built-in themes: `colored`, `dracula`, `high-contrast`, `one-dark`, and `onedark` alias.
- Custom JSON/TOML theme-file overlay via `--theme-file`.
- INI-style user configuration with generated defaults and precedence:
  built-in defaults -> user config -> explicit CLI options.
- Cross-platform config paths:
  - Linux/macOS: `~/.mdutilcfg`
  - Windows: `%USERPROFILE%\mdutil.ini`
- CLI flags for `--theme`, `--theme-file`, `--config`, `--generate-config`, `--line-numbers`, `--quiet`, and `--version`.
- Prompt-toolkit interactive viewer for real file output when stdout is a TTY.
- Interactive scrolling with `j`, `k`, arrow keys, `PageDown`, and `PageUp`.
- Interactive line-number toggle with `l`.
- Compact bottom status bar showing F1 help, document name, and quit hint.
- F1 help modal with title, proper prompt-toolkit shadow, Escape close behavior, and no manual full-height shadow artifact.
- Long-line wrapping in the interactive viewer.
- SemVer version source of truth in `mdutil/version.py`, dynamically consumed by `pyproject.toml` and `mdutil --version`.

## Recently completed

- v1.5.1 release version bump.
- Issue #6 visual cleanup for the F1 modal:
  - Added titled modal border: `F1 - Help`.
  - Reworked shadow handling to avoid the left-side full-height artifact.
  - Kept the status bar compact.
- Issue #11 interactive viewer long-line wrapping.
- Added/kept regression coverage for interactive viewer behavior, config behavior, project metadata, parser, renderer, syntax highlighter, and themes.
- Ignored Hermes workspace artifacts in `.gitignore`.

## Immediate priorities

### 1. Keep the housekeeping branch clean

- [ ] Review `git status` before making feature changes.
- [ ] Confirm `todo.md` is the only intended housekeeping change on this branch unless additional cleanup is explicitly requested.
- [ ] Do not push or open a PR unless explicitly asked.

### 2. Reconcile documentation metadata with the current implementation

The specification still has stale front-matter-style metadata even though the roadmap is broadly current.

- [ ] Update `mdutil-specification.md` header fields as appropriate:
  - version currently says `1.0.0` while package version is `1.5.1`.
  - last-updated currently says `2026-05-15`.
- [ ] Keep roadmap rows aligned with implemented state.
- [ ] Re-run the doc-related metadata tests after any spec/README changes.

### 3. Start the next roadmap slice: v2.0 editing foundation

The next incomplete roadmap item is v2.0 editing: in-place editing and key bindings such as `i`, `dd`, and `cw`.

Suggested incremental first slice:

- [ ] Define a small editing-state model independent of prompt-toolkit rendering.
- [ ] Add tests first for:
  - entering insert mode with `i`;
  - returning to normal/view mode;
  - deleting the current line with `dd`;
  - replacing/changing a word with `cw` only after the editing model is stable.
- [ ] Keep the first implementation in memory only; do not write files back to disk until save semantics are specified.
- [ ] Decide and document whether v2.0 editing is a true file editor or a modal buffer prototype.
- [ ] Add key-binding tests before wiring behavior into the interactive app.

### 4. Define save/write behavior before enabling file mutation

Before any editing feature writes to disk, specify and test the safety behavior.

- [ ] Decide whether save is explicit-only, e.g. `:w`, Ctrl-S, or another key.
- [ ] Decide dirty-buffer indicators in the status bar.
- [ ] Decide whether quitting with unsaved changes prompts, blocks, or discards.
- [ ] Add tests for write failures, missing permissions, and preserving original file contents on failure.
- [ ] Consider backup/atomic-write behavior before modifying user files.

### 5. Broaden viewer/rendering quality only after v2.0 direction is clear

These are useful improvements, but lower priority than the next roadmap slice.

- [ ] Improve inline rendering beyond stripping simple `<strong>`, `<em>`, and `<code>` tags.
- [ ] Add more representative golden Markdown fixtures.
- [ ] Review table rendering for width, alignment, and ANSI-width edge cases.
- [ ] Add performance checks for larger documents if scrolling/rendering gets slower.

### 6. Future roadmap items after v2.0

From `mdutil-specification.md`:

- [ ] v2.5: expose all Pygments syntax highlighting styles.
- [ ] v2.5: cycle through styles and save the last used style on exit.
- [ ] v3.0: render/export to PDF/HTML.
- [ ] v4.0: runtime loading of custom syntax highlighters.

## Verification checklist before committing changes

Run at minimum:

```bash
python -m pytest -q
python -m unittest discover -v
python -m compileall -q mdutil tests
python setup.py check
python -m mdutil --version
```

For changes touching interactive behavior, also add or update focused tests in `tests/test_display.py` and `tests/test_cli.py`.

For changes touching docs/spec tables, read the edited section back from disk and verify Markdown table rows still have consistent cell counts.
