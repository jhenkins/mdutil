# mdutil

A simple and comfortable Markdown viewer and editor for terminal written in Python.

## A note on this project

*mdutil* began as an experiment in AI-assisted coding and remains a sandbox project. You are welcome to use
it. Just be aware that given its experimental nature, pull requests are unlikely to be accepted.

## Where we are today

We currently have a functional Markdown reader and editor with syntax highlighting, themes, and a prompt-toolkit
interactive view. File-backed sessions support raw Markdown editing, explicit saves, dirty-buffer protection,
copy/paste helpers, and mode-aware search. We also have a very simple ini-style configuration file that you can
edit to make your choice of theme and a few other things permanent.

## Quick Overview

- Read markdown documents with syntax highlighting
- Edit file-backed Markdown interactively with normal/insert modes
- Export documents to PDF or HTML with `--export pdf` / `--export html` and `--output`
- PDF export renders Markdown headings, inline bold/emphasis/code, clickable links, wrapped tables, and blockquote blocks
- Search in normal mode with `/`, then navigate matches with `n` and `N`
- Search while editing with `Ctrl-/`; literal `/` remains text input in insert mode
- Highlight visible search matches in the rendered preview
- Multiple theme support (default, dracula, one-dark, etc.)
- ANSI color output for terminal
- Supports file input or stdin
- Math notation: `$E = mc^2$` with `--math-fallback` toggle
- Footnotes: `[^1]` references with `--footnote-style` (numbered/bracketed)
- Full GFM syntax: strikethrough, task lists, highlight, definition lists, images, link titles, nested lists

Release history is documented in [CHANGELOG.md](CHANGELOG.md).

## Interactive controls

When stdout is a TTY and a file path is provided, `mdutil` opens the interactive viewer/editor.

- Normal mode renders the Markdown preview. Use `i` to enter insert/edit mode, `q` to quit when unmodified, and `!q` to discard unsaved changes.
- Insert/edit mode edits the raw Markdown buffer. Use Escape to return to normal mode and Ctrl-S to save file-backed changes explicitly.
- Search keys are mode-aware and shown in the bottom status bar: `/` searches from normal mode, `Ctrl-/` searches while editing, and `n` / `N` move between matches.
- Search matches are highlighted in the rendered preview.

---

## v5.0 Features

mdutil v5.0 adds comprehensive support for GFM and CommonMark syntax, including strikethrough, task lists, math notation, footnotes, subscript/superscript, highlighting, definition lists, image rendering, link titles, and nested lists.

### Strikethrough

Use `~~text~~` for strikethrough:

```markdown
This is ~~deleted~~ text.
```

### Task Lists

Create checklists with `- [ ]` (unchecked) and `- [x]` / `- [X]` (checked):

```markdown
- [x] Write documentation
- [ ] Review code
- [x] Run tests
```

### Math Notation

Inline math with `$...$`:

```markdown
Einstein's equation: $E = mc^2$
```

Use `--math-fallback` to show raw LaTeX instead of stripping delimiters.

### Footnotes

Define footnotes at the end of the document and reference them inline:

```markdown
This has a footnote[^1].

[^1]: This is the footnote definition.
```

Control reference display with `--footnote-style numbered` (default, superscript) or `--footnote-style bracketed` (e.g., `[1]`).

### Subscript & Superscript

Use `~text~` for subscript and `^text^` for superscript:

```markdown
Water: H~2~O
Superscript: X^2^
```

### Highlight

Highlight text with `==text==`:

```markdown
This is ==important== text.
```

### Definition Lists

Define terms and definitions:

```markdown
Markdown
:   A lightweight markup language

HTML
:   HyperText Markup Language
```

### Images

Render images with `![alt text](url)`:

```markdown
![Logo](https://example.com/logo.png "Company Logo")
```

HTML export embeds images directly; PDF export embeds local images; remote URLs render as placeholders.

### Link Titles

Add hover titles to links:

```markdown
[Google](https://google.com "Search Engine")
```

### Nested Lists

Support arbitrarily nested lists with indentation:

```markdown
- Item 1
  - Sub-item 1a
  - Sub-item 1b
    - Deep item
- Item 2
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--math-fallback` | disabled | Show raw LaTeX in `$...$` delimiters instead of stripping tags |
| `--footnote-style` | `numbered` | Footnote reference display style (`numbered` or `bracketed`) |

### Configuration

New options are available in the configuration file (`~/.mdutilcfg`):

```ini
[mdutil]
# Show raw LaTeX instead of stripping math delimiters
# math_fallback = true

# Footnote reference style: "numbered" (superscript) or "bracketed" (e.g., [1])
# footnote_style = numbered
```

---

## Installation

### Quick Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/jhenkins/mdutil.git
cd mdutil

# Install from source
pip install .

# Or install in editable mode (recommended for development)
pip install -e .
```

### Manual Installation

```bash
# If you have a local copy
cd path/to/mdutil
pip install .
```

### Direct Python Usage (No Installation)

```bash
# Run directly from source directory
python -m mdutil your_file.md
```

---

## Usage Examples

### Display a markdown file

```bash
mdutil your_document.md
```

### Read from stdin

```bash
echo -e "# Hello World\n\nSome *markdown* text." | mdutil -
```

### With syntax highlighting

```bash
mdutil your_document.md  # Shows with colors
```

### Quiet mode

```bash
mdutil your_document.md --quiet
```

### Export to PDF

```bash
mdutil your_document.md --export pdf --output output.pdf
```

PDF output includes headings, paragraphs, lists, code blocks, tables with wrapped cell text, blockquotes, horizontal rules, and inline formatting such as bold, emphasis, inline code, and clickable links. Specification-style document metadata headers (`Author`, `Version`, `Last-Updated`, `License`, `Repository`) are preserved as separate lines.

### Export to HTML

```bash
mdutil your_document.md --export html --output output.html
```

HTML output includes embedded CSS and preserves inline Markdown formatting, links, tables, lists, blockquotes, code blocks, and the same line-preserved document metadata header handling as PDF export.

### Export both formats

```bash
mdutil your_document.md --export pdf,html --output-dir ./exports
```

### Export with custom CSS for HTML

```bash
mdutil your_document.md --export html --custom-css style.css --output-dir ./html
```

### Default output directory

```bash
# Writes to ./output.pdf (or ./output.html) in the current directory
echo -e "# Hello\n\nWorld" | mdutil --export html
```

### Export with Mermaid Diagrams

```bash
mdutil your_document.md --export html --output doc.html
```

Both HTML and PDF export include **Mermaid diagram rendering**. Mermaid diagrams are detected in ` ```mermaid ` fenced code blocks and rendered using the bundled `merman-cli` binary.

- **HTML export:** Renders to inline SVG embedded in `<div class="mermaid">` containers.
- **PDF export:** Renders to PNG via SVG→PNG conversion, embedded in the PDF with page-break handling and aspect-ratio preservation.

#### Mermaid CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--mermaid` | enabled | Enable Mermaid diagram rendering (both HTML and PDF) |
| `--no-mermaid` | – | Disable Mermaid rendering (diagrams rendered as code blocks) |
| `--mermaid-theme <name>` | `default` | Mermaid rendering theme (`default`, `forest`, `dark`, `neutral`) |

**Example with dark theme:**

```bash
mdutil your_document.md --export pdf --output doc.pdf --mermaid-theme dark
```

**Example disabling mermaid:**

```bash
mdutil your_document.md --export pdf --output doc.pdf --no-mermaid
```

#### Air-Gapped Operation

mdutil bundles the `merman-cli` binary, ensuring **zero network access** is required for Mermaid rendering. This works in air-gapped environments without browser dependencies.

**Supported platforms:**
- Linux x86_64
- macOS ARM64 (Apple Silicon)
- macOS x64 (Intel)
- Windows x64

When `--no-mermaid` is passed or the binary is unavailable, mermaid code blocks are exported as regular fenced code blocks (no SVG).

---

## Demo

```bash
# Create a test markdown file
mkdir -p target
echo -e "# Hello World\n\nSome *markdown* text.\n\nUse **bold** and `code`." > target/demo.md

# Display the file
cd target
mdutil demo.md
```

Expected output:
```
# Hello World

Some markdown text.

Use bold and code.
```

---

## Troubleshooting

### Mermaid Diagrams Not Rendering

**Symptom:** Mermaid code blocks appear as plain text instead of SVG diagrams.

**Cause:** The `merman-cli` binary is not available or not executable.

**Solution:**
1. Verify the binary exists:
   ```bash
   python -c "from mdutil.export.merman_renderer import MermanRenderer; print(MermanRenderer.find_binary())"
   ```
2. If binary not found, reinstall:
   ```bash
   pip install --force-reinstall mdutil
   ```
3. Check platform support:
   - Linux x86_64: ✅ Supported
   - macOS ARM64: ✅ Supported
   - macOS x64: ✅ Supported
   - Windows x64: ✅ Supported
   - Other platforms: Falls back to code block export

**Force disable mermaid:**
```bash
mdutil doc.md --export pdf --no-mermaid
```

### Invalid Mermaid Syntax

**Symptom:** SVG renders as empty box or contains error text.

**Cause:** Invalid mermaid syntax in your markdown.

**Solution:** Validate mermaid syntax using the [mermaid.live editor](https://mermaid.live) before export. mdutil reports errors in the terminal but continues rendering the rest of the document.

### Slow Export with Many Diagrams

**Symptom:** Export takes longer than expected with multiple mermaid diagrams.

**Cause:** Each diagram requires a subprocess call to `merman-cli`.

**Solution:** 
- Use `--no-mermaid` for quick previews
- Batch diagrams where possible
- Use simpler diagram types (flowcharts are fastest)

---

## Requirements
- Python 3.11 or higher
- Please note that this project uses [fpdf2](https://github.com/akademic/fpdf2) as the sole external dependency for PDF export, beyond the core Python Markdown, Pygments, and prompt-toolkit libraries.

---

## Versioning and Release Strategy

mdutil follows Semantic Versioning 2.0.0 using `MAJOR.MINOR.PATCH` versions, with optional prerelease/build metadata such as `1.0.0-rc.1` or `1.0.0+build.5`.

### Version source of truth

The package version is defined in one place only:

```python
mdutil/version.py
```

`pyproject.toml` reads the package version dynamically from `mdutil.version.__version__`, and the CLI prints the same value via:

```bash
mdutil --version
```

Release tags should use this exact format:

```text
v{version}
```

For example, version `1.2.3` should be tagged as `v1.2.3`.

### What increments each part

- MAJOR: incompatible CLI, theme-file, rendering-contract, Python API, or packaging changes after 1.0.0.
- MINOR: backward-compatible features, new Markdown rendering support, new themes, new CLI options, or additive Python APIs.
- PATCH: backward-compatible bug fixes, documentation fixes, test-only changes, and internal refactors that do not change user-visible behavior.

### Pre-1.0 policy

While mdutil is in the `0.y.z` phase, the public contract is still stabilizing:

- `0.MINOR.0` may include breaking changes.
- `0.MINOR.PATCH` must remain backward compatible within that minor line.
- Breaking changes should still be called out clearly in release notes.
- Once the CLI flags, theme schema, rendered output contract, and packaging workflow are stable, release `1.0.0`.

### Release checklist

1. Decide the next version from the change set using the rules above.
2. Update `mdutil/version.py` only.
3. Run the full verification suite:

   ```bash
   python -m pytest -q
   python -m unittest discover -v
   python -m compileall -q mdutil tests
   python setup.py check
   python -m pip install -e '.[dev]'
   python -m mdutil --version
   ```

4. Ensure `python -m mdutil --version` prints the intended version.
5. Commit the version change and release notes together.
6. Create an annotated tag named `v{version}`.
7. Build/publish artifacts from that tag.

---

## License

MIT License - see LICENSE file for details.

---

## Documentation

Programming specification can be found in the mdutil-specification.md file.