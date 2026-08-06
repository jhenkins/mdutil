# Changelog

All notable changes to mdutil will be documented in this file.

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

## Future: v4.1

- PDF export of Mermaid diagrams (SVG to PNG conversion)
- Page break handling around diagrams
- Reusable SVG→image conversion layer between HTML and PDF exporters
