# mdutil Manual QA Checklist

**Version target:** 3.0.0  
**Last updated:** 2026-07-27  
**Test platforms:** Linux, macOS, Windows (Python 3.11+)

> This checklist covers the terminal display viewer, editor, and the v3.0 PDF/HTML export features. Each step includes a concrete command to run and an expected result to verify.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Test Document Setup](#2-test-document-setup)
3. [Basic Viewing & Rendering](#3-basic-viewing--rendering)
4. [Interactive Viewer & Editor](#4-interactive-viewer--editor)
5. [Themes & Configuration](#5-themes--configuration)
6. [PDF Export](#6-pdf-export)
7. [HTML Export](#7-html-export)
8. [Export Edge Cases & Errors](#8-export-edge-cases--errors)
9. [Stdin & Pipelines](#9-stdin--pipelines)
10. [Performance & Large Documents](#10-performance--large-documents)
11. [Platform-Specific Notes](#11-platform-specific-notes)
12. [Sign-Off](#12-sign-off)

---

## 1. Prerequisites

### 1.1 Environment

| Step | Action | Expected |
|------|--------|----------|
| 1.1a | `python --version` | `Python 3.11.x` or higher |
| 1.1b | `pip install -e .` from project root | Installs successfully, no errors |
| 1.1c | `python -m mdutil --version` | Prints `mdutil 3.0.0` (or target version) |
| 1.1d | `python -m pytest -q` | All tests pass (192 passed at time of writing) |

### 1.2 Test fixture document

Create a file at `/tmp/qa-test.md` with the following content:

~~~markdown
# mdutil QA Test Document

This is a standard paragraph with **bold**, *italic*, ~~strikethrough~~, and `inline code`.

## Level 2 Heading

### Level 3 Heading

#### Level 4 Heading

##### Level 5 Heading

###### Level 6 Heading

---

## Lists

### Unordered

- Item one
- Item two
  - Nested item A
  - Nested item B
- Item three

### Ordered

1. First step
2. Second step
   1. Sub-step 2a
   2. Sub-step 2b
3. Third step

---

## Code Blocks

### Python

```python
def greet(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"

print(greet("World"))
```

### JavaScript

```javascript
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
greet("World");
```

### Plain text (no language)

```
$ echo "Hello World"
Hello World
```

---

## Tables

| Name      | Age | City      | Country   |
|-----------|-----|-----------|-----------|
| Alice     | 30  | London    | UK        |
| Bob       | 25  | Paris     | France    |
| Charlie   | 35  | Tokyo     | Japan     |
| Diana     | 28  | Berlin    | Germany   |

---

## Blockquotes

> This is a standard blockquote.
>
> It can span multiple paragraphs.
>
> > Nested blockquotes are also supported.

---

## Horizontal Rules

Above this line is text.

---

Below this line is more text.

---

## Links

Visit [GitHub](https://github.com).

---

## Unicode & Special Characters

- **CJK:** 你好世界
- **Emoji:** 🎉🚀📝
- **Accents:** àéüñç
- **Greek:** αβγδ
- **Codec test:** `print("Hello 🎉")`

---

## Edge Cases

### Empty heading (no text)

#

### Table with a single column

| Just one |
|----------|
| Value A  |
| Value B  |

### Empty code block

```python
```

### Mixed content in list item

1. Item with **bold**, *italic*, and `code`.
2. Another item.

### Horizontal rule inside a list

Not standard, but should not crash.

---

## Long Paragraph

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
~~~

---

## 2. Basic Viewing & Rendering

### 2.1 File input

| Step | Command | Expected |
|------|---------|----------|
| 2.1a | `python -m mdutil /tmp/qa-test.md` | Opens interactive viewer. All headings, lists, tables, code blocks, blockquotes, and horizontal rules are visible with proper formatting. |

### 2.2 Stdin input

| Step | Command | Expected |
|------|---------|----------|
| 2.2a | `cat /tmp/qa-test.md \| python -m mdutil` | Rendered output prints to stdout and exits. No interactive viewer. |
| 2.2b | `cat /tmp/qa-test.md \| python -m mdutil -` | Same as 2.2a. |

### 2.3 Quiet mode

| Step | Command | Expected |
|------|---------|----------|
| 2.3a | `python -m mdutil --quiet /tmp/qa-test.md` | No visible output (exit code 0). |
| 2.3b | `echo $?` | `0` |

---

## 3. Interactive Viewer & Editor

> Requires a real TTY. On Windows, use PowerShell or Windows Terminal.

| Step | Action | Expected |
|------|--------|----------|
| 3.1 | `python -m mdutil /tmp/qa-test.md` | Viewer opens with rendered Markdown. Status bar shows normal mode indicators. |
| 3.2 | Press `j` and `k` | Scrolls up and down one line at a time. |
| 3.3 | Press `g` then `G` | `g` jumps to top, `G` jumps to bottom. |
| 3.4 | Press `q` | Exits viewer (no changes to save). |
| 3.5 | Press `i` | Enters insert/edit mode. Raw Markdown is shown. Status bar changes to insert indicators. |
| 3.6 | Type some text, then Escape | Returns to normal mode. Status bar reverts to normal mode indicators. |
| 3.7 | Press `dd` on a non-empty line | The line is copied to clipboard (no visual change unless pasted). |
| 3.8 | Press `yy` | Copies the current line (same as `dd` without deleting). |
| 3.9 | Press `i`, move cursor, press Ctrl-V | Pastes clipboard content at cursor. |
| 3.10 | Press Escape, then `/` | Search bar appears at bottom. |
| 3.11 | Type `Alice`, press Enter | First match is highlighted in the rendered preview. Press `n` / `N` to cycle forward/backward. |
| 3.12 | Press Escape to dismiss search | Search highlight disappears. |
| 3.13 | Press `q` | Returns to normal mode if in search. |
| 3.14 | Press Ctrl-S in insert mode | Saves the file. Status bar confirms save. |
| 3.15 | Make an edit, press `q` | Warning: "Unsaved changes. Use `!q` to discard." |
| 3.16 | Press `!q` | Discards changes and exits. |
| 3.17 | Press `F1` | Help modal opens with keybinding reference. Press any key to close. |

---

## 4. Themes & Configuration

### 4.1 Built-in themes

| Step | Command | Expected |
|------|---------|----------|
| 4.1a | `python -m mdutil --theme dracula /tmp/qa-test.md` | Opens with Dracula theme colors. Dark background, pink/green highlights. |
| 4.1b | `python -m mdutil --theme one-dark /tmp/qa-test.md` | Opens with One Dark theme. |
| 4.1c | `python -m mdutil --theme high-contrast /tmp/qa-test.md --quiet` | Renders to stdout with high-contrast colors. |

### 4.2 Syntax theme

| Step | Command | Expected |
|------|---------|----------|
| 4.2a | `python -m mdutil --syntax-theme monokai /tmp/qa-test.md --quiet` | Code blocks use Monokai syntax colors. |
| 4.2b | `python -m mdutil --syntax-theme native /tmp/qa-test.md --quiet` | Code blocks use native syntax colors. |

### 4.3 Configuration file

| Step | Command | Expected |
|------|---------|----------|
| 4.3a | `python -m mdutil --generate-config` | Prints "Configuration file ready: /home/user/.mdutilcfg" (path varies by OS). |
| 4.3b | `cat ~/.mdutilcfg` (Linux/macOS) or `type %USERPROFILE%\\mdutil.ini` (Windows) | Shows commented INI file with all sections including `[export]`. |
| 4.3c | Edit `~/.mdutilcfg`, change `theme = dracula`, then `python -m mdutil /tmp/qa-test.md` | Opens with Dracula theme (config default, no `--theme` flag needed). |
| 4.3d | Restore default theme after test. | |

### 4.4 Line numbers

| Step | Command | Expected |
|------|---------|----------|
| 4.4a | `python -m mdutil --line-numbers /tmp/qa-test.md --quiet` | Line numbers shown at the start of each line. |

---

## 5. PDF Export

### 5.1 Basic PDF generation

| Step | Command | Expected |
|------|---------|----------|
| 5.1a | `python -m mdutil --export pdf --output /tmp/test.pdf /tmp/qa-test.md` | Prints "Exported to: /tmp/test.pdf" to stderr. |
| 5.1b | `head -c 5 /tmp/test.pdf` | Output starts with `%PDF-`. |
| 5.1c | `file /tmp/test.pdf` | Returns "PDF document" (or similar). |
| 5.1d | Open `/tmp/test.pdf` in a PDF reader (Evince, Chrome, Acrobat). | All content rendered: headings, lists, code blocks (with background fill), tables (bordered, alternating rows), blockquotes (grey), horizontal rules. |

### 5.2 PDF bookmarks

| Step | Command | Expected |
|------|---------|----------|
| 5.2a | Open `/tmp/test.pdf` in a PDF reader with a sidebar/navigation pane. | Bookmarks/outline entries exist for h1, h2, h3 headings. h4-h6 are NOT bookmarked. |
| 5.2b | Click a bookmark. | Jumps to the correct page. |

### 5.3 PDF paper sizes

| Step | Command | Expected |
|------|---------|----------|
| 5.3a | `python -m mdutil --export pdf --output /tmp/test-letter.pdf /tmp/qa-test.md` (with `pdf_paper_size = Letter` in config if testing letter) | PDF generated successfully. File size differs from A4. |
| 5.3b | `python -m mdutil --export pdf --output /tmp/test-legal.pdf /tmp/qa-test.md` (with config change if testing legal) | PDF generated successfully. |

### 5.4 PDF with header/footer

| Step | Command | Expected |
|------|---------|----------|
| 5.4a | Edit `~/.mdutilcfg` `[export]` section to add `pdf_header = Draft` and `pdf_footer = Page` | |
| 5.4b | `python -m mdutil --export pdf --output /tmp/test-hf.pdf /tmp/qa-test.md` | PDF generated. Header text "Draft" visible at top of pages, footer text visible at bottom. |
| 5.4c | Restore config to remove header/footer after test. | |

### 5.5 PDF auto-naming (no --output)

| Step | Command | Expected |
|------|---------|----------|
| 5.5a | `cd /tmp && python -m mdutil --export pdf /tmp/qa-test.md` | "Exported to: /tmp/qa-test.pdf" |
| 5.5b | `ls -la /tmp/qa-test.pdf` | File exists. |
| 5.5c | Clean up: `rm /tmp/qa-test.pdf` | |

### 5.6 PDF via --output-dir

| Step | Command | Expected |
|------|---------|----------|
| 5.6a | `python -m mdutil --export pdf --output-dir /tmp/pdf-out /tmp/qa-test.md` | "Exported to: /tmp/pdf-out/qa-test.pdf" |
| 5.6b | `ls -la /tmp/pdf-out/` | Directory created with PDF inside. |

---

## 6. HTML Export

### 6.1 Basic HTML generation

| Step | Command | Expected |
|------|---------|----------|
| 6.1a | `python -m mdutil --export html --output /tmp/test.html /tmp/qa-test.md` | Prints "Exported to: /tmp/test.html" to stderr. |
| 6.1b | `head -c 20 /tmp/test.html` | Starts with `<!DOCTYPE html>`. |
| 6.1c | Open `/tmp/test.html` in a web browser. | All content rendered: headings, lists, code blocks with syntax highlighting, tables (bordered), blockquotes, links are clickable. |

### 6.2 HTML custom CSS

| Step | Command | Expected |
|------|---------|----------|
| 6.2a | Create `/tmp/custom.css`: `body { background: #ffe; } h1 { color: red; }` | |
| 6.2b | `python -m mdutil --export html --custom-css /tmp/custom.css --output /tmp/test-custom.html /tmp/qa-test.md` | HTML generated. |
| 6.2c | `grep "Custom CSS" /tmp/test-custom.html` | Shows `/* Custom CSS */` comment in the style block. |
| 6.2d | Open `/tmp/test-custom.html` in a browser. | Page has cream background (`#ffe`), h1 headings are red. |

### 6.3 HTML auto-naming (no --output)

| Step | Command | Expected |
|------|---------|----------|
| 6.3a | `cd /tmp && python -m mdutil --export html /tmp/qa-test.md` | "Exported to: /tmp/qa-test.html" |
| 6.3b | `ls -la /tmp/qa-test.html` | File exists. |
| 6.3c | Clean up: `rm /tmp/qa-test.html` | |

---

## 7. Multi-Format Export

### 7.1 Both formats in one pass

| Step | Command | Expected |
|------|---------|----------|
| 7.1a | `python -m mdutil --export pdf,html --output-dir /tmp/multi /tmp/qa-test.md` | "Exported to: /tmp/multi/qa-test.pdf" and "Exported to: /tmp/multi/qa-test.html" |
| 7.1b | `ls -la /tmp/multi/` | Both files present. |
| 7.1c | Verify `qa-test.pdf` starts with `%PDF` and `qa-test.html` starts with `<!DOCTYPE html>`. | |

### 7.2 Stdin with both formats

| Step | Command | Expected |
|------|---------|----------|
| 7.2a | `cat /tmp/qa-test.md \| python -m mdutil --export pdf,html --output-dir /tmp/multi-stdin` | Exports to /tmp/multi-stdin/output.pdf and /tmp/multi-stdin/output.html. Both valid. |
| 7.2b | Clean up: `rm -rf /tmp/multi /tmp/multi-stdin` | |

---

## 8. Export Edge Cases & Errors

### 8.1 Unsupported format

| Step | Command | Expected |
|------|---------|----------|
| 8.1a | `python -m mdutil --export docx /tmp/qa-test.md` | "Error: Unsupported export format: 'docx' (choose from pdf, html)" — exit code 1. |

### 8.2 Missing input file

| Step | Command | Expected |
|------|---------|----------|
| 8.2a | `python -m mdutil --export pdf nonexistent.md` | Error about file not found. Exit code 1. |

### 8.3 Read-only output directory

| Step | Command | Expected |
|------|---------|----------|
| 8.3a | `mkdir -p /tmp/readonly && chmod 444 /tmp/readonly` | |
| 8.3b | `python -m mdutil --export pdf --output-dir /tmp/readonly /tmp/qa-test.md` | "Export error (pdf): Permission denied — cannot write to /tmp/readonly/qa-test.pdf" |
| 8.3c | `chmod 755 /tmp/readonly && rmdir /tmp/readonly` | Clean up. |

### 8.4 Missing custom CSS file

| Step | Command | Expected |
|------|---------|----------|
| 8.4a | `python -m mdutil --export html --custom-css /tmp/nonexistent.css /tmp/qa-test.md` | "Error reading custom CSS file: [Errno 2] No such file or directory: '/tmp/nonexistent.css'" — exit code 1. |

### 8.5 Partial failure in multi-format

| Step | Command | Expected |
|------|---------|----------|
| 8.5a | `python -m mdutil --export bad,pdf /tmp/qa-test.md` | "Error: Unsupported export format: 'bad' (choose from pdf, html)" — PDF export still runs and succeeds. Exit code 1 (overall). |

---

## 9. Stdin & Pipelines

### 9.1 Pipe Markdown to stdout viewer

| Step | Command | Expected |
|------|---------|----------|
| 9.1a | `echo "# Hello World" \| python -m mdutil` | Rendered output: `# Hello World` (styled). Exits immediately. |
| 9.1b | `echo "# Hello\n\nWorld" \| python -m mdutil --quiet` | No output. Exit code 0. |

### 9.2 Pipe Markdown to export

| Step | Command | Expected |
|------|---------|----------|
| 9.2a | `cat /tmp/qa-test.md \| python -m mdutil --export pdf --output /tmp/pipe-test.pdf` | PDF generated. |
| 9.2b | `head -c 5 /tmp/pipe-test.pdf` | `%PDF-` |
| 9.2c | Clean up: `rm /tmp/pipe-test.pdf` | |

### 9.3 Multiple files

| Step | Command | Expected |
|------|---------|----------|
| 9.3a | `echo "Doc 1" > /tmp/doc1.md && echo "Doc 2" > /tmp/doc2.md` | |
| 9.3b | `python -m mdutil /tmp/doc1.md /tmp/doc2.md` | Opens first file. After quitting, opens second file. |
| 9.3c | Clean up: `rm /tmp/doc1.md /tmp/doc2.md` | |

---

## 10. Performance & Large Documents

### 10.1 Generate a large document

| Step | Command | Expected |
|------|---------|----------|
| 10.1a | `python -c "print('# Large Doc\\n'); [print(f'## Section {i}\\n\\nLorem ipsum dolor sit amet.\\n') for i in range(200)]" > /tmp/large.md` | Creates ~200-section doc (~1000+ lines). |
| 10.1b | `wc -l /tmp/large.md` | ~1000+ lines. |

### 10.2 Render performance

| Step | Command | Expected |
|------|---------|----------|
| 10.2a | `time python -m mdutil --quiet /tmp/large.md` | Renders in under 2 seconds. Exit code 0. |
| 10.2b | `time python -m mdutil --export pdf --output /tmp/large.pdf /tmp/large.md` | Exports PDF in under 5 seconds. File is valid. |
| 10.2c | `time python -m mdutil --export html --output /tmp/large.html /tmp/large.md` | Exports HTML in under 5 seconds. File is valid. |
| 10.2d | Clean up: `rm /tmp/large.md /tmp/large.pdf /tmp/large.html` | |

---

## 11. Platform-Specific Notes

### Linux (Ubuntu 24.04 / Fedora)

- PDF Unicode fonts (DejaVu TTF) are auto-detected from `/usr/share/fonts/truetype/dejavu/`
- All sections above should pass fully.

### macOS

- DejaVu fonts may not be pre-installed. If missing, PDF export falls back to Helvetica/Courier (Latin-1 only). CJK/emoji characters will produce a warning (glyph missing) but the PDF will still render Latin-1 text correctly.
- To install DejaVu fonts on macOS: `brew install --cask font-dejavu`
- All other sections should pass.

### Windows (10/11)

- **Shell note:** Use PowerShell, Windows Terminal, or Command Prompt. Some `echo -e` commands may not work — use `cat` and redirection instead.
- **Stdin pipe:** In PowerShell, `Get-Content qa-test.md | python -m mdutil` works.
- **TTY detection:** Interactive viewer requires a real TTY. PowerShell ISE may not work; use Windows Terminal.
- **Configuration path:** `%USERPROFILE%\mdutil.ini` instead of `~/.mdutilcfg`.
- **DejaVu fonts:** May not be pre-installed. PDF export will fall back to Latin-1 fonts.
- **Known limitation:** `file` command is not available on Windows — use `python -c "print(open('/tmp/test.pdf','rb').read(5))"` to check for `%PDF-`.

---

## 12. Sign-Off

| Platform         | Tester      | Date       | Pass/Fail | Notes |
|------------------|-------------|------------|-----------|-------|
| Linux (Ubuntu)   |             |            |           |       |
| Linux (Fedora)   |             |            |           |       |
| macOS (Intel)    |             |            |           |       |
| macOS (Apple Si) |             |            |           |       |
| Windows 10       |             |            |           |       |
| Windows 11       |             |            |           |       |

---

**Test summary:** ___ / 60 tests passed  (___ / 60 attempted)  
**Overflow failures:** ___ (link to bug tracker issue(s))
