# Markdown Viewer CLI – Program Specification

**Author:** _Jan Henkins_  
**Version:** 2.2.1 (source of truth: `mdutil/version.py`)  
**Last‑Updated:** 2026‑07‑07  
**License:** MIT  
**Repository:** <https://github.com/jhenkins/mdutil>

---

## 1. Introduction

`mdutil` is a **cross‑platform, terminal‑based Markdown viewer** that renders Markdown files with syntax‑highlighted code blocks and basic styling (headings, lists, blockquotes, etc.).  
The focus is on a clean, fast, and fully‑featured viewer that can later evolve into a light‑weight editor. The program is written in Python.

**Key design goals**

- 100 % terminal‑only (no GUI).
- Minimal dependencies – a single static binary.
- Cross‑platform: runs on **Linux, macOS, Windows** (native).
- Responsive UI: scrolling, line‑number toggling, and theming.
- Extensible: future editing features can plug into the same pipeline.

---

## 2. Scope & Use‑Cases

| #   | Use‑Case             | Description                                                                                      |
| --- | -------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | **View**             | Open any Markdown file, scroll, and read formatted text.                                         |
| 2   | **Syntax Highlight** | Code blocks are highlighted using the specified theme.                                           |
| 3   | **Theming**          | User can choose from built‑in themes or provide a custom theme file.                             |
| 4   | **Line Numbers**     | Optional display of line numbers for code blocks and the main document.                          |
| 5   | **Edit**             | In-place Markdown editing with explicit save, dirty-state protection, and normal/insert modes.   |

> **Out‑of‑Scope** (for v1.0.0)
>
> - Rich text editing, live preview, or file synchronization.
> - Rendering Markdown to PDF/HTML.
> - Interactive tables or forms.

---

## 3. Functional Requirements

| Feature | Description | CLI Option(s) |
| --- | --- | --- |
| **Load Markdown** | Accept a file path or read from stdin. | `mdutil <file.md>` or <code>cat file.md &#124; mdutil</code> |
| **Basic Rendering** | Render headings, lists, blockquotes, emphasis, tables, etc. | – |
| **Code Syntax Highlighting** | Detect language via fenced code block info strings such as <code>```python</code>; fallback to plain text. | – |
| **Theming** | Choose a theme. | `--theme <theme-name>` |
| **Custom Theme** | Load a custom theme file (JSON or TOML). | `--theme-file <path>` |
| **Configuration File** | Load user defaults from an editable configuration file. | `--config <path>` and `--generate-config` |
| **Line Numbers** | Toggle line numbers for code blocks. | `--line-numbers` |
| **Scroll** | Arrow keys or `j/k` to scroll up/down; `q` to quit. | – |
| **Editing** | Vim-like normal commands with prompt-toolkit insert editing. Normal/viewer mode renders Markdown preview output; insert/editing mode shows and edits raw Markdown. Shortcuts include `i`, Escape, `dd`, `cw`, `yc`, `yw`, `yy`, Ctrl-V paste, explicit Ctrl-S save, dirty-buffer status, dirty quit blocking, and `!q` discard-and-quit. | – |
| **Search** | Search from normal mode with `/`, navigate matches with `n` and `N`, search while editing with Ctrl-/ so literal `/` remains editable text, and highlight visible matches in the rendered preview. | – |
| **Safe File Writes** | File-backed interactive sessions write through atomic same-directory temporary files and preserve the original file on failed saves. | – |
| **Status Bar** | Distinct normal/edit/dirty/error status-bar text and colors, with theme keys and optional configuration overrides. | `status_bar_normal`, `status_bar_insert` |
| **Help** | Show command-line usage. | `--help` |
| **Version** | Print version. | `--version` |

> **User‑Interface Constraints**
>
> - Must be usable on terminals up to 256 color support.
> - Works in both UTF‑8 and legacy terminals (fallback to ASCII).
>
> **Interactive UI Library Decision**
>
> - v1 uses `prompt-toolkit` for the interactive viewer because it provides cross-platform keyboard handling, terminal resizing, fullscreen rendering, and future editing primitives while remaining lighter than a full widget framework.
> - `textual` remains a good albeit heavier alternative for the future if mdutil grows into a richer TUI with panels, widgets, command palettes, tabs, or split edit/preview layouts.
>
> **Configuration File**
>
> - `mdutil` supports a plain-text, standard-editor-editable user configuration file for runtime defaults.
> - On Linux and macOS, the default user configuration file is `~/.mdutilcfg`.
> - On Windows, the default user configuration file is `%USERPROFILE%\mdutil.ini`.
> - The configuration file is stored in the user's home folder using the path convention of the operating system.
> - The configuration format is INI-style text with comments. Generated files must include the current runtime defaults and helpful comments describing available options and accepted values.
> - If the configuration file does not exist, `mdutil` runs with built-in defaults. A user can create the file manually or generate a starter file with `--generate-config`.
> - Runtime precedence is: built-in defaults → user configuration file → explicit CLI options.
> - `--config <path>` may be used to load an alternate configuration file for a single invocation.
> - Configuration must not require network access and must be parsed offline.

---

## 4. Non‑Functional Requirements

| Category          | Requirement                                                      | Rationale                              |
| ----------------- | ---------------------------------------------------------------- | -------------------------------------- |
| **Performance**   | Render < 1 ms per page load (≈ 1 k lines).                       | Fast scrolling on large docs.          |
| **Memory**        | ≤ 10 MB RAM usage on 10 k line file.                             | Lightweight on low‑resource machines.  |
| **Portability**   | Build once, run on Linux, macOS, Windows (64‑bit).               | Simplifies distribution.               |
| **Accessibility** | High‑contrast themes, `--theme high-contrast`.                   | Meets accessibility standards.         |
| **Extensibility** | Modular architecture: Parser → Renderer → Highlighter → Display. | Easier to plug editing features later. |
| **Security**      | No external network access; all parsing is offline.              | Reduces attack surface.                |

---

## 5. Architecture Overview

The CLI parser loads built-in defaults, merges any user configuration file, then applies explicit command-line options before passing resolved runtime settings through the rest of the pipeline.

Interactive terminal output has two coordinated modes. Normal/viewer mode renders
the current Markdown buffer through the parser, renderer, syntax highlighter, and
terminal display pipeline. Insert/editing mode exposes the raw Markdown buffer for
text changes. The command model is an explicit hybrid: Vim-like normal commands
for navigation and structural editing, plus prompt-toolkit text editing while in
insert mode. Normal-mode copy/paste commands are `yc` for the character under the
cursor, `yw` for the word under the cursor, `yy` for the current line, and Ctrl-V
to paste clipboard text at the cursor. File-backed sessions save explicitly with
Ctrl-S, track dirty state, block accidental dirty quits, and write atomically via
same-directory temporary files before replacing the target path. The bottom status
bar identifies normal/insert state, save/dirty state, and the relevant safe action;
its normal and insert colors can be supplied by the active theme or overridden from
the configuration file. Search keys are mode-aware and appear in the bottom status
bar: normal mode advertises `/` plus `n/N`, while insert/editing mode advertises
Ctrl-/ so `/` remains normal text input.

```
┌───────────────────────┐
│      CLI Parser       │
└──────▲───────┬────────┘
       │       │
       │      args
       │       │
┌──────▼───────┴────────┐
│   Markdown Reader     │
└──────▲───────┬────────┘
       │       │
       │      file
       │       │
┌──────▼───────┴────────┐
│   Markdown Parser     │ 
└──────▲───────┬────────┘
       │       │
       │     events
       │       │
┌──────▼───────┴────────┐
│    Markdown Renderer  │
└──────▲───────┬────────┘
       │       │
       │    tokens
       │       │
┌──────▼───────┴────────┐
│   Syntax Highlighter   │
└──────▲───────┬────────┘
       │       │
       │     ANSI
       │       │
┌──────▼───────┴────────┐
│   Terminal Display    │
└───────────────────────┘
```

---

## 6. Testing Strategy

| Test Type                  | Description                                                                                                           |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Unit Tests**             | Each component (`Renderer`, `Highlighter`) gets pure‑function tests.                                                  |
| **Integration Tests**      | Run `mdutil` against a set of sample Markdown files (covering tables, code fences, footnotes).                        |
| **Configuration Tests**    | Verify default config paths, config generation, comments/default values, alternate `--config`, and CLI precedence.    |
| **Interactive Editor Tests** | Verify normal/insert mode transitions, `i`, Escape, `dd`, `cw`, explicit Ctrl-S save, dirty indicators, dirty quit blocking, discard quit, failed-save preservation, atomic-write cleanup, mode-aware search keys, status-bar search hints, and highlighted search matches. |
| **End‑to‑End (CLI)**       | Use `assert_cmd` to spawn `mdutil` with various flags and verify output length / presence of expected ANSI sequences. |
| **Cross‑Platform CI**      | GitHub Actions matrix: ubuntu, macos, windows.                                                                        |
| **Performance Benchmarks** | Measure rendering time on large docs (10k lines).                                                                     |

> **Coverage Goal**: ≥ 90 % code coverage.


---

## 7. Maintenance & Contribution

- **Issue Tracker**: Use GitHub issues.
- **Pull Requests**: Follow the template, run CI, ensure tests pass.
- **Release Process**: Semantic versioning; tag releases; publish binaries on GitHub Releases and, optionally, as a Homebrew/Cargo package.

---

## 8. Future Enhancements (Roadmap)

| Phase    | Feature        | Description                                             | Status |
| -------- | -------------- | ------------------------------------------------------- |--------|
| **v1.0** | _Viewing_      | Scroll with j/k and arrows, and page up/down.           | Done   |
| **v1.0** | _Viewing_      | Enable/disable line numbers while viewing with 'l'      | Done   |
| **v1.5** | _Viewing_      | Add F1 help modal popup to clean up status bar area     | Done   |
| **v1.5** | _Viewing_      | Bottom status bar: F1 help, document name               | Done   |
| **v2.0** | _Editing_      | In-place editing foundation: `i`, Escape, `dd`, `cw`, explicit Ctrl-S save, dirty protection, and atomic writes. | Done   |
| **v2.1** | _Performance_  | Improve interactive performance on large documents.     | Done   |
| **v2.2** | _Editing_      | Enhance and normalize editor functionality: raw Markdown editing, copy/paste, command model, search in normal/edit modes, highlighted matches, clearer status bars, status colors, and theme/config color settings. | Done   |
| **v2.3** | _Highlighting_ | Expose all Pygments syntax highlighting styles.         | Todo   |
| **v2.4** | _Highlighting_ | Cycle through styles and save last used style on exit.  | Todo   |
| **v3.0** | _Export_       | Render to PDF/HTML using `pulldown-cmark` + `printpdf`. | Todo   |
| **v3.5** | _Export_       | Support rendering of Mermaid diagrams.                  | Todo   |
| **v4.0** | _Plugins_      | Runtime loading of custom syntax highlighters.          | Todo   |
