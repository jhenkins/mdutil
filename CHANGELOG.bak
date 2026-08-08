# Changelog

All notable changes to mdutil will be documented in this file.

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

### From v3.x to v4.0

- No breaking changes to existing CLI flags
- New `--mermaid`, `--no-mermaid`, `--mermaid-theme` flags added
- Mermaid rendering is enabled by default for HTML export
- Use `--no-mermaid` to disable if you don't need diagram rendering

---

## Future: v5.0

- TBD
