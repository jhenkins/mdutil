# Changelog

All notable changes to mdutil will be documented in this file.

## [Unreleased]

### Changed
- **Strikethrough terminal rendering** (KB-103)
  - Terminal now uses ANSI `\033[9m` (STANDOUT ON) and `\033[29m` (STANDOUT OFF) escape sequences for actual visual strikethrough
  - Works with modern terminals (VIM, iTerm2, GNOME Terminal, etc.)
  - Colour + strikethrough applied together via theme `strikethrough` key

## [5.0.0] - 2026-08-22

### Added
- **Strikethrough** (KB-051)
  - Parser detects `~~text~~` inline syntax
  - Terminal: strikethrough color via theme
  - HTML: `<del>` tag rendering
  - PDF: strikethrough font

- **Task Lists** (KB-052, KB-053, KB-054)
  - Parser detects `- [ ]` and `- [x]` / `- [X]` markers
  - Terminal: `☐` / `☑` Unicode checkboxes with theme colors
  - HTML: `<input type="checkbox" disabled>` with checked state
  - PDF: Unicode checkbox prefix on task items

- **Math Notation** (KB-055, KB-056)
  - Parser detects `$...$` inline LaTeX math
  - Terminal: monospace italic styling, `$` delimiters preserved with `--math-fallback`
  - HTML: `<span class="math">` with monospace italic CSS
  - PDF: monospace font
  - `--math-fallback` flag preserves `$...$` delimiters

- **Footnotes** (KB-057 to KB-060)
  - Parser detects `[^n]` references inline and `[^n]: text` definitions at document end
  - Terminal: superscript Unicode glyphs for references
  - HTML: `<sup><a href="#fn-N">N</a></sup>` references + `<div class="footnotes">` section with back-links
  - PDF: superscript CID glyphs + horizontal rule separator + numbered footnote section
  - `--footnote-style numbered|bracketed` flag controls reference display

- **Subscript & Superscript** (KB-061, KB-062)
  - Parser detects `~sub~` and `^super^` syntax
  - Terminal: Unicode subscript/superscript characters with nested tag stripping
  - HTML: `<sub>` / `<sup>` tags pass through
  - PDF: Unicode sub/superscript characters rendered

- **Highlight** (KB-063, KB-064)
  - Parser detects `==text==` syntax
  - Terminal: yellow background highlighting (ANSI 48;2;255;255;0)
  - HTML: `<mark>` with yellow background CSS
  - PDF: text renders normally (no background)

- **Definition Lists** (KB-065, KB-066)
  - Parser detects `Term\n:   Definition` syntax
  - Terminal: styled term (bold/blue) + indented definition (gray)
  - HTML: `<dl>/<dt>/<dd>` with CSS
  - PDF: bold term + indented definitions with `—` prefix

- **Image Rendering** (KB-067 to KB-070)
  - Parser detects `![alt](url)` syntax with optional `=WxH` dimensions
  - Terminal: `[image: alt text]` placeholder
  - HTML: `<img>` with width/height attributes, responsive CSS
  - PDF: embeds local images as PNG, placeholder for remote URLs

- **Link Titles** (KB-071, KB-072)
  - Parser extracts `title` attribute from `[text](url "title")` syntax
  - HTML: `title` attribute on `<a>` tags
  - PDF: link annotation with title

- **Nested Lists** (KB-073, KB-074)
  - Parser supports up to 8 levels of nested ordered/unordered lists
  - All renderers recurse into `sub_list` with proper indentation
  - 20 new tests covering nesting, mixed types, inline formatting

- **Theme Support for New Inline Styles** (KB-075)
  - 6 new theme keys: `strikethrough`, `task_list_checked`, `task_list_unchecked`, `highlight`, `definition_term`, `definition_definition`
  - All 4 built-in themes (colored, dracula, high-contrast, one-dark) updated

- **Configuration Options** (KB-076)
  - `--math-fallback` flag + `math_fallback` INI key
  - `--footnote-style` flag + `footnote_style` INI key (`numbered` or `bracketed`)

- **Comprehensive Test Suite** (KB-077 to KB-080)
  - 189 new tests across 5 test files
  - Parser tests: 41 tests covering all new syntax
  - Renderer tests: 38 tests for theme colors, fallback behavior, cross-feature rendering
  - Exporter tests: 83 tests for HTML/PDF v5.0 features
  - CLI integration tests: 32 tests for flags and config

### Changed
- Parser now handles strikethrough, math, footnotes, sub/superscript, highlight, definition lists, images, link titles, and nested lists
- Terminal renderer supports Unicode sub/superscript characters, checkbox symbols, highlight background
- HTML exporter renders `<del>`, `<input>`, `<math>`, `<sup>`, `<sub>`, `<mark>`, `<dl>`, `<dt>`, `<dd>`, `<img>`, link `title` attributes
- PDF exporter embeds local images, renders sub/superscript Unicode, footnote section with CID glyphs
- All exporters support recursive nested list rendering

### Technical Details
- Inline parser extension point at `_parse_inline_segment()` in `mdutil/parser.py`
- Block parser extension point at `_extract_definition_list()` for definition lists
- Theme system extended with 6 new inline-style keys
- Configuration file gains `math_fallback` and `footnote_style` options
- Total test count: 894 tests

---

## [4.1.0] - 2026-08-08

### Added
- **PDF export of Mermaid diagrams** (KB-026a, KB-026b, KB-026c)
  - Shared SVG→PNG conversion layer (`mdutil/export/svg_to_image.py`)
  - `SvgToImageRenderer` wraps merman-cli `--outputFormat png` for PNG rendering
  - `get_svg_dimensions()` extracts SVG width/height for dimension calculation
  - PdfExporter batch-renders mermaid diagrams, embeds PNGs in PDF output
  - Page-break handling: adds new page if diagram won't fit on current page
  - Aspect-ratio preservation when scaling diagrams to fit page width
  - Error fallback: renders mermaid code block when PNG conversion fails

### Changed
- Mermaid rendering now applies to both HTML and PDF export (previously HTML only)
- `--mermaid` / `--no-mermaid` / `--mermaid-theme` flags control both exporters

### Technical Details
- Shared `svg_to_image.py` module reusable by future exporters
- No `cairosvg` dependency — merman-cli produces native PNG output
- Scale factor 2.0 for HiDPI PNG output
- fpdf2 scales PNG back to fit page width via target dimensions

---

## [4.0.1] - 2026-08-06

### Added
- **Mermaid diagram rendering in HTML export** (KB-018 to KB-025)
  - Detect and render Mermaid diagrams in ` ```mermaid ` code blocks
  - Bundle `merman-cli` binary for offline, air-gapped operation
  - Support for flowcharts, sequence diagrams, state diagrams, and more
  - Inline SVG embedding in HTML output
  
- **New CLI flags** (KB-024)
  - `--mermaid` - Enable Mermaid rendering (default)
  - `--no-mermaid` - Disable Mermaid rendering (diagrams as code blocks)
  - `--mermaid-theme <name>` - Set theme: `default`, `forest`, `dark`, `neutral`

- **Comprehensive test coverage** (KB-023)
  - 382+ tests including mermaid rendering, theme passthrough, air-gapped operation
  - Regression tests for existing HTML/PDF export features

### Changed
- HTML exporter now detects `mermaid` token type and renders inline SVG
- Parser identifies ` ```mermaid ` fenced code blocks
- MermanRenderer handles subprocess execution with timeout and error handling

### Technical Details
- Platform-specific binaries: Linux x86_64, macOS ARM64/x64, Windows x64
- Zero network access required (air-gapped operation)
- Graceful fallback to code block when binary unavailable or `--no-mermaid` active

### Documentation
- Updated README with mermaid export section and troubleshooting
- Updated specification with mermaid architecture details
- Added Git branching policy to AGENTS.md

---

## [4.0.0] - Previous Release

This is the initial v4.0 release with mermaid support. All development for v4.0 has been completed in the `feature/v4.0-docs-finalization` branch.

---

## Migration Notes

### From v4.x to v5.0

- No breaking changes to existing CLI flags
- New `--math-fallback` flag for raw LaTeX display
- New `--footnote-style` flag for footnote reference display (`numbered` or `bracketed`)
- New inline syntax: `~~strikethrough~~`, `- [ ]` task lists, `$math$`, `[^1]` footnotes, `~sub~`, `^super^`, `==highlight==`, `![image](url)`, `[text](url "title")`
- Theme keys added: `strikethrough`, `task_list_checked`, `task_list_unchecked`, `highlight`, `definition_term`, `definition_definition`
- Configuration file: optional `math_fallback` and `footnote_style` options (see `--generate-config`)

---

## Future: v5.1

- TBD
