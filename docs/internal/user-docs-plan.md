# User Documentation Plan for mdutil

> Status: Planning — not yet started.

## Background

The README is growing unwieldy and there is no structured user guide. We need a proper documentation system that supports navigation, search, and clean web rendering.

## Current State

- Single `README.md` (~100+ lines) covering installation, features, keybindings, export formats
- `docs/` folder contains development/planning notes (KBs, debug plans), not user-facing content
- No documentation-related tasks in the roadmap

## Options Considered

### Option A: mdbook (recommended)

**Pros:**
- Beautiful navigation sidebar, search, responsive design
- Publishes to HTML, PDF, ePub
- Uses Markdown — easy to write
- Rust toolchain, well-maintained (used by the Rust project itself)
- Plugin ecosystem: syntax highlighting, Mermaid diagrams, copy buttons

**Cons:**
- Requires Rust toolchain install
- Build step needed before publishing

**Proposed structure:**
```
docs/
├── book.toml
└── src/
    ├── SUMMARY.md
    ├── 00-intro.md
    ├── 01-installation.md
    ├── 02-usage.md          (CLI commands, options)
    ├── 03-keybindings.md
    ├── 04-themes.md
    ├── 05-configuration.md
    ├── 06-export.md         (PDF/HTML export)
    ├── 07-advanced.md       (themes dev, stdin, large files)
    └── 08-faq.md
```

### Option B: MkDocs Material

**Pros:**
- Python-based (fits mdutil's stack), no Rust needed
- Stunning theme with built-in search, dark mode, tabs
- Great for code-heavy docs
- Can deploy to GitHub Pages with one click

**Cons:**
- Slightly heavier pip install

### Option C: Refactor the README

**Pros:** Zero new tooling, just refactor what exists
**Cons:** No navigation, no search, no nice web rendering

## Recommendation

**Go with mdbook** — it matches the "Markdown tool documenting Markdown" theme nicely, and the plugin ecosystem is great for code examples.

## Next Steps

- [ ] Scaffold mdbook project in `docs/`
- [ ] Migrate README content into structured pages
- [ ] Add build step to CI or Makefile
- [ ] Set up GitHub Pages deployment
