# mdutil TODO

Last updated: 2026-07-07
Current branch: `feature/v2.2-editing`
Current package version: `2.2.0`
Baseline verification at update time: `python -m pytest -q` -> 118 passed, 12 subtests passed in 2.99s

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
- Prompt-toolkit interactive file viewer/editor for real file output when stdout is a TTY.
- Interactive scrolling with `j`, `k`, arrow keys, `PageDown`, and `PageUp`.
- Interactive line-number toggle with `l`.
- Interactive editing mode with `i`, Escape back to normal mode, `dd` current-line deletion, and `cw` word-change.
- Explicit Ctrl-S file save for file-backed interactive sessions, dirty-buffer status, dirty quit blocking, and `!q` discard-and-quit.
- Compact bottom status bar showing mode, document name, dirty/save state, and mode-aware search hints.
- F1 help modal with title, proper prompt-toolkit shadow, Escape close behavior, and no manual full-height shadow artifact.
- Long-line wrapping in the interactive viewer.
- Cached normal-mode rendered previews and plain-text code-fence fast paths for large documents.
- Mode-aware interactive search: `/` in normal mode, Ctrl-/ in insert/edit mode, `n`/`N` match navigation, and highlighted rendered-preview matches.
- SemVer version source of truth in `mdutil/version.py`, dynamically consumed by `pyproject.toml` and `mdutil --version`.

## Recently completed

- v2.0.0 release version bump.
- v2.1.0 performance release version bump.
- v2.2.0 editing/search release version bump.
- Issue #19 large-document performance improvements.
- Issue #6 visual cleanup for the F1 modal:
  - Added titled modal border: `F1 - Help`.
  - Reworked shadow handling to avoid the left-side full-height artifact.
  - Kept the status bar compact.
- Issue #11 interactive viewer long-line wrapping.
- Added/kept regression coverage for interactive viewer behavior, config behavior, project metadata, parser, renderer, syntax highlighter, and themes.
- Ignored Hermes workspace artifacts in `.gitignore`.
- Started the v2.0 true file editor foundation on `feature/v2.0-planning`.

## Immediate priorities

### 1. Keep the housekeeping branch clean

- [x] Reviewed `git status` before making documentation changes on 2026-06-05.
- [x] Confirmed the working tree was clean before this documentation audit.
- [x] Kept this as a local documentation update only; no push or PR was opened.

### 2. Reconcile documentation metadata with the current implementation

Completed on 2026-06-05.

- [x] Updated `mdutil-specification.md` header fields:
  - version now says `2.1.0` and points to `mdutil/version.py` as the source of truth.
  - last-updated now says `2026-06-05`.
- [x] Audited roadmap rows against the current implementation; v1.0/v1.5 viewer rows remain `Done`, v2.1 performance is `Done`, and remaining future rows remain `Todo`.
- [x] Re-ran the doc-related metadata tests after the spec update.

### 3. Start the next roadmap slice: v2.0 editing foundation

Completed on 2026-06-07.

The next incomplete roadmap item is v2.0 editing: in-place editing and key bindings such as `i`, `dd`, and `cw`.

Implemented incremental first slice:

- [x] Defined a small editing-state model independent of prompt-toolkit rendering in `mdutil/editor.py`.
- [x] Added tests first/alongside implementation for:
  - entering insert mode with `i`;
  - returning to normal/view mode with Escape;
  - deleting the current line with `dd`;
  - replacing/changing a word with `cw` after the editing model was stable.
- [x] Switched v2.0 editing direction to a true file editor using the prompt-toolkit `TextArea` as the main interactive body, rather than a modal buffer overlay.
- [x] Added key-binding tests before/with wiring behavior into the interactive app.
- [x] Added explicit save semantics for the first editor slice: Ctrl-S writes only when a file-backed target is available.

### 4. Continue hardening save/write behavior

The first editor slice now has explicit Ctrl-S save, dirty indicators, and dirty-quit blocking. Before treating file mutation as release-ready, harden failure and safety behavior.

- [x] Decide whether save is explicit-only: Ctrl-S is the initial explicit save binding.
- [x] Decide dirty-buffer indicators in the status bar: normal mode shows `modified`, `Ctrl-S Save`, and `!q Discard`; insert mode shows modified/unmodified state.
- [x] Decide whether quitting with unsaved changes prompts, blocks, or discards: plain `q` blocks when dirty; `!q` discards and quits.
- [x] Add tests for write failures, missing permissions, and preserving original file contents on failure.
  - Covered failed Ctrl-S writes, permission errors, dirty-state preservation, and original-file preservation.
- [x] Consider backup/atomic-write behavior before modifying user files.
  - Implemented atomic same-directory temp-file writes with `os.replace`; failed writes clean up temp files and leave the original target unchanged.

### 5. Next viewer/rendering quality slice

The v2.0 editing foundation and save/write hardening are now clear enough that
viewer and rendering quality can move into the next incremental backlog slice.

- [ ] Improve inline rendering beyond current lightweight handling of links and simple `<strong>`, `<em>`, and `<code>` tags; cover nested spans, mixed emphasis/code, escapes, and punctuation edge cases.
- [ ] Add more representative golden Markdown fixtures.
- [ ] Review table rendering for alignment, wide Unicode, combining characters, and ANSI-width edge cases.
- [ ] Add a normal-mode scroll percentage to the status bar beside the document name, based on the rendered preview scroll offset.
- [ ] Bind Home/End in normal mode to jump to the top/bottom of the document.
- [ ] Expand large-document performance coverage if scrolling/rendering regresses; include cache reuse, representative fixture sizes, and an explicit budget or benchmark for interactive scroll latency.

### 6. Proposed roadmap reconciliation with `mdutil-specification.md`

Keep this section aligned with the roadmap table in `mdutil-specification.md`.

- [x] v2.0: Editing foundation: in-place editing, key bindings (`i`, `dd`, `cw`), explicit Ctrl-S save, dirty indicators, dirty quit blocking, and atomic file writes.
- [x] v2.1: Deal with performance issues with large documents.
- [x] v2.2: Enhance and normalise editor functionality:
  - [x] Ensure insert/editing mode shows raw Markdown only; normal/viewer mode remains responsible for rendered preview output.
  - [x] Add copy/paste support for characters, words, and whole lines.
  - [x] Choose and document the command model: Vim-like normal commands with prompt-toolkit insert editing.
  - [x] Improve status-bar text in normal and editing modes.
  - [x] Add distinct normal/edit status-bar colors.
  - [x] Add normal/edit status-bar color keys to built-in themes and custom theme files, then expose config defaults for selecting or overriding them.
  - [x] Add search in normal and edit modes: `/` in normal mode, Ctrl-/ while editing, `n`/`N` navigation, highlighted matches, F1 help, and mode-aware status-bar hints.
- [ ] v2.3: Expose all Pygments syntax highlighting styles.
- [ ] v2.4: Cycle through styles and save the last used style on exit.
- [ ] v3.0: render/export to PDF/HTML.
- [ ] v3.5: support rendering of Mermaid diagrams.
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

---

