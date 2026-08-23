# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)^1^,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)^2^.

## [5.0.0] - 2024-02-01

### Added
- Strikethrough support via `~~text~~` syntax
- Task list checkboxes (`- [ ]` and `- [x]`)
- Math notation with `$...$` inline delimiters
- Footnote definitions and references (`[^1]`)
- Subscript (`~text~`) and superscript (`^text^`)
- Highlight syntax (`==text==`)
- Definition lists (`Term\n: Definition`)
- Image rendering with `![alt](url)` syntax
- Nested list support with arbitrary depth
- Link title attributes: `[text](url "title")`
- Mermaid diagram rendering

### Changed
- Updated parser to handle all GFM extensions
- Enhanced HTML exporter with new element types
- PDF exporter now embeds images and diagrams

### Fixed
- Nested list items no longer merge into single line
- Code blocks inside lists preserve indentation

## [4.1.0] - 2024-01-15

### Added
- PDF export with Mermaid diagram support

## [4.0.0] - 2024-01-01

### Added
- HTML export with Mermaid diagram rendering
- SVG-to-PNG conversion layer

## [3.1.0] - 2023-12-01

### Added
- Syntax highlighting for code blocks in PDF
- Theme-aware code highlighting

## [3.0.0] - 2023-11-01

### Added
- Initial release with terminal rendering
- HTML export support
- PDF export support
- CLI interface with configuration

---

^1^ Keep a Changelog — https://keepachangelog.com
^2^ Semantic Versioning 2.0.0 — https://semver.org
