 # mdutil v4.0: HTML Export with Mermaid Diagram Support

 ## Overview

 v4.0 adds Mermaid diagram rendering to HTML export. The merman-cli binary is bundled with
 mdutil to ensure offline, air-gapped operation without browser dependencies.

 ## Goal

 Export Markdown documents with Mermaid diagrams to HTML with embedded SVG diagrams, using a
 bundled merman-cli binary for rendering. No network access required.

 ## Bundle Strategy

 - Bundle `merman-cli` pre-built binary with mdutil
 - Platform-specific binaries: Linux x86_64, macOS ARM64, macOS x64, Windows x64
 - Detect platform at runtime and use appropriate binary
 - No end-user installation required
 - Air-gapped operation: zero network calls

 ## Phase 1: Foundation & Testing Infrastructure

 **Status:** In progress

 ### KB-001: Mermaid rendering research and binary selection
 - [x] Research offline mermaid rendering options
 - [x] Evaluate merman-cli (pure Rust, no browser, cross-platform)
 - [x] Verify merman-cli works with system Chromium fallback
 - [x] Confirm cross-platform support (Linux, macOS, Windows)
 - [ ] Document findings in `docs/mermaid-research.md`

 ### KB-002: Bundle infrastructure setup ✅ COMPLETE
 - [x] Add `mdutil/export/_merman_binaries/` directory structure
 - [x] Create script to download pre-built merman-cli binaries during build
 - [x] Add platform detection logic (`sys.platform`, `platform.machine()`)
 - [x] Create `MermanRenderer` class to wrap binary execution
 - [x] Write unit tests for platform detection and binary discovery

 ### KB-003: Core merman rendering integration ✅ COMPLETE
 - [x] Implement `render_mermaid_svg(mermaid_code: str) -> str`
 - [x] Handle subprocess execution with proper error handling
 - [x] Support mermaid theme configuration (default, dark, forest, etc.)
 - [x] Add fallback error messages when merman-cli is unavailable
 - [x] Write unit tests for rendering pipeline

 ## Phase 2: HTML Export with Mermaid

 ### KB-004: HTML exporter mermaid integration ✅ COMPLETE
 - [x] Extend `HtmlExporter` to detect mermaid fenced code blocks
 - [x] Render each mermaid diagram to SVG via merman-cli
 - [x] Embed SVGs inline in HTML output (or as file references)
 - [x] Preserve existing HTML export features (CSS, syntax highlighting, etc.)
 - [x] Write unit tests for HTML export with mermaid

 ### KB-005: Markdown processing for mermaid blocks ✅ COMPLETE
 - [x] Extend parser to identify ` ```mermaid ` code blocks
 - [x] Extract mermaid source code from markdown
 - [x] Track diagram positions for HTML embedding
 - [x] Write unit tests for mermaid block detection

 ## Phase 3: Testing & Documentation

 ### KB-006: Comprehensive testing
 - [ ] Unit tests for merman-cli binary detection (all platforms)
 - [ ] Unit tests for SVG rendering (flowcharts, sequence, state, etc.)
 - [ ] Integration tests for HTML export with mermaid diagrams
 - [ ] Air-gapped testing (verify no network calls)
 - [ ] Regression tests for existing HTML export features

 ### KB-007: Documentation
 - [ ] Update README with mermaid support
 - [ ] Document bundled binary and air-gapped operation
 - [ ] Add troubleshooting for merman-cli issues
 - [ ] Update specification document

 ## Phase 4: Verification & Release

 ### KB-008: Final verification
 - [ ] Run full test suite (pytest, unittest, compileall)
 - [ ] Verify HTML export with mermaid diagrams
 - [ ] Verify air-gapped operation (no network calls)
 - [x] Bump version to 4.0.1
 - [x] Update release notes

 ## Testing Requirements

 **Unit tests must cover:**
 1. Platform detection (Linux, macOS, Windows)
 2. Binary discovery and permissions
 3. Mermaid code parsing
 4. SVG rendering (basic flowcharts, sequence diagrams)
 5. HTML export with embedded SVGs
 6. Error handling (invalid mermaid syntax, missing binary)
 7. Theme configuration
 8. Air-gapped operation (no network calls)

 **Integration tests must cover:**
 1. CLI: `mdutil doc.md --export html --output doc.html` with mermaid diagrams
 2. CLI: `mdutil doc.md --export html --output doc.html --no-mermaid` to disable mermaid rendering
 3. CLI: `mdutil doc.md --export html --output doc.html` with mermaid theme option (`--mermaid-theme dark`)
 4. CLI: `mdutil doc.md --export pdf,html` multi-format export with mermaid
 5. CLI: Mermaid code blocks with invalid syntax → graceful error in HTML output
 6. Multi-diagram: document with 3+ mermaid diagrams renders all correctly
 7. Mixed content: mermaid blocks interleaved with tables, lists, code blocks

## CLI Integration

The following CLI surface is added for v4.0:

| Flag | Default | Description |
|------|---------|-------------|
| `--mermaid` | enabled | Enable Mermaid diagram rendering in HTML export |
| `--no-mermaid` | – | Disable Mermaid rendering (diagrams rendered as code blocks) |
| `--mermaid-theme <name>` | `default` | Mermaid rendering theme (`default`, `forest`, `dark`, `neutral`) |
| `--mermaid-config <json>` | `{}` | JSON string for mermaid config (e.g., `{'securityLevel':'loose'}`) |

When `--no-mermaid` is passed, mermaid code blocks are exported as regular fenced code blocks (no SVG). This is useful for testing or when the merman-cli binary is not available.

## Mermaid Themes

| Theme | Description |
|-------|-------------|
| `default` | Light theme (standard mermaid look) |
| `forest` | Green-tinted variant |
| `dark` | Dark background theme |
| `neutral` | Minimal, low-contrast theme |

## Implementation Notes

- The merman-cli binary should be shipped as part of the Python package via `package_data` in pyproject.toml.
- Platform detection uses `sys.platform` + `platform.machine()` to select the right binary.
- On Windows, the binary needs `.exe` extension.
- The binary must be executable (`chmod +x`) on Unix platforms.
- Consider using `importlib.resources` (Python 3.9+) for binary access.
- SVG embedding: inline `<svg>` tags are preferred for self-contained HTML. Fallback to `<img src="data:image/svg+xml,...">` if inline causes issues.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| merman-cli binary not available on some platform | Blocker | Graceful fallback to plain code block export |
| Large SVG increases HTML file size | Low | Inline SVG is typical; document size impact |
| merman-cli crashes on complex diagrams | Medium | Sandbox subprocess execution with timeout and stderr capture |
| Cross-platform binary distribution | Medium | Use GitHub Releases + build script for CI |

## Future: PDF Mermaid (v4.1)

PDF export of Mermaid diagrams is planned for v4.1. This requires:
1. Converting SVG output from merman-cli to an image format fpdf2 can embed (PNG).
2. Handling page breaks around diagrams.
3. Testing PDF rendering with various diagram sizes.

The architecture should be designed so the SVG→image conversion layer is reusable between HTML and PDF exporters.
