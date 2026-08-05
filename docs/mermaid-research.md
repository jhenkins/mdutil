# Mermaid Diagram Rendering Research

**Date:** 2026-08-05
**Author:** jan
**Status:** Complete
**Related:** KB-018 (v4.0 Phase 1a)

---

## 1. Problem Statement

v4.0 needs to render Mermaid diagrams in HTML export with **zero network access**. The diagrams must be embedded as inline SVG in the output HTML. This requires a fully offline, self-contained rendering pipeline.

## 2. Options Evaluated

### 2.1 Option: `mermaid-cli` (`mmdc`) via Puppeteer/Chromium

- **How it works:** Node.js CLI that uses Puppeteer to launch Chromium, renders mermaid diagrams, outputs SVG/PDF.
- **Pros:** Official tool, well-maintained, supports themes.
- **Cons:** 
  - Requires Node.js + Puppeteer (~500MB install).
  - Requires an installed Chromium browser or downloads its own.
  - Not suitable for bundling with a Python package.
  - Network access needed for initial Puppeteer/Chromium download.
- **Verdict:** ❌ Rejected — too heavy, not air-gapped compatible.

### 2.2 Option: Browser-based rendering at export time

- **How it works:** Launch a headless browser in-process, render diagrams via the mermaid.js library.
- **Pros:** Full mermaid feature support.
- **Cons:**
  - Requires browser binary (Chromium/Playwright) on the system.
  - Large footprint, complex dependency chain.
  - Not air-gapped friendly.
- **Verdict:** ❌ Rejected — same issues as above.

### 2.3 Option: `mermaid-cli` (`mmdc`) — Rust fork (merman-cli)

- **How it works:** Pure Rust implementation of mermaid-cli. Compiles to a single static binary. No browser dependency by default; can fall back to system Chromium if needed for complex diagrams.
- **Pros:**
  - **Pure Rust binary** — single static executable, no runtime dependencies.
  - **Cross-platform** — supports Linux x86_64, macOS ARM64/x64, Windows x64.
  - **Air-gapped** — zero network calls, no browser download.
  - **System Chromium fallback** — for diagrams that need it, uses already-installed Chromium.
  - **Small binary** — ~10-20MB vs ~500MB for Node+Puppeteer.
  - **Fast** — no Node.js startup overhead.
- **Cons:**
  - May not support every mermaid feature (some rendering edge cases).
  - Requires pre-built binaries for each platform (or compile from source).
  - Less actively maintained than official `@mermaid-js/mermaid-cli`.
- **Verdict:** ✅ **Selected** — best fit for air-gapped, bundled deployment.

## 3. merman-cli Technical Details

### 3.1 Build & Deployment

- Compiled as a statically-linked binary using `cargo build --release`.
- Platform-specific binaries:
  - `merman-linux-x86_64` — Linux x86_64
  - `merman-darwin-arm64` — macOS ARM64 (Apple Silicon)
  - `merman-darwin-x64` — macOS x64 (Intel)
  - `merman-win-x64.exe` — Windows x64
- On Unix, binary must be `chmod +x`.
- On Windows, binary is `merman-win-x64.exe`.

### 3.2 Rendering Command

```bash
merman-cli -i diagram.mmd -o output.svg -t dark
```

- `-i`: Input mermaid source file (or `-` for stdin).
- `-o`: Output SVG file path (or `-` for stdout).
- `-t`: Theme (`default`, `forest`, `dark`, `neutral`).
- `--config`: JSON config string for mermaid configuration.

### 3.3 Threading / Subprocess Model

- merman-cli runs as a separate process.
- mdutil spawns it via `subprocess.run()` with:
  - Timeout (default 30 seconds per diagram).
  - Stderr capture for error reporting.
  - Input via temporary file or stdin pipe.
- If merman-cli crashes or times out, mdutil falls back to rendering the diagram as a plain code block with an error message.

### 3.4 System Chromium Fallback

- merman-cli uses a built-in SVG renderer for most diagrams.
- For diagrams that require JavaScript evaluation (certain sequence diagrams, state diagrams with complex interactions), it falls back to system Chromium.
- If no Chromium is found, it gracefully degrades to the built-in renderer (which may not render perfectly for complex diagrams, but still produces valid SVG).
- **Critical:** The built-in renderer handles the vast majority of diagrams without any browser dependency.

## 4. Platform Detection Strategy

Python runtime detection in mdutil:

```python
import sys, platform

def _merman_binary_name() -> str:
    if sys.platform == "win32":
        return "merman-win-x64.exe"
    elif sys.platform == "darwin":
        machine = platform.machine()
        if machine == "arm64":
            return "merman-darwin-arm64"
        return "merman-darwin-x64"
    else:
        return "merman-linux-x86_64"
```

Binary location: `mdutil/export/_merman_binaries/<binary_name>`.

Access via `importlib.resources` (Python 3.9+):

```python
from importlib.resources import files

binary_path = files("mdutil.export._merman_binaries") / _merman_binary_name()
```

## 5. Binary Distribution

### 5.1 Packaging

- Include binaries in `package_data` in `pyproject.toml`:
  ```toml
  [tool.setuptools.package-data]
  "mdutil.export._merman_binaries" = ["*"]
  ```
- Binaries must be tracked in git (LFS or regular, depending on size).

### 5.2 CI Build (Future)

- GitHub Actions matrix builds merman-cli for each target platform.
- Upload artifacts to GitHub Releases.
- Build script downloads pre-built binaries during `pip install`.

### 5.3 Developer Setup

- Developers can build locally: `cargo build --release --target <triple>`.
- Or use pre-built binaries from the repo.

## 6. Theme Support

merman-cli supports these themes:

| Theme | Description | Visual |
|-------|-------------|--------|
| `default` | Light theme, standard mermaid look | White bg, blue accents |
| `forest` | Green-tinted variant | Light green bg |
| `dark` | Dark background | Dark gray bg, light text |
| `neutral` | Minimal, low-contrast | Gray tones |

Themes are passed via `-t <name>` flag. Default is `default`.

## 7. Limitations & Edge Cases

### 7.1 Supported Diagram Types

- Flowcharts (basic and subgraphs)
- Sequence diagrams
- State diagrams
- Class diagrams
- Gantt charts
- Pie charts
- Git graphs

### 7.2 Known Limitations

- Some complex mermaid features (e.g., clickable links in diagrams, custom CSS classes) may not be fully supported.
- Diagrams with external references (images, custom CSS) are not supported — consistent with air-gapped requirement.
- Very large diagrams (>50 nodes) may exceed the subprocess timeout.

### 7.3 Fallback Behavior

When merman-cli is unavailable or fails:
1. Diagram is rendered as a fenced code block (no SVG).
2. An HTML comment notes the rendering failure: `<!-- Mermaid diagram not rendered: <reason> -->`.
3. User sees the raw mermaid source in the HTML output.

## 8. Security Considerations

- merman-cli is run as a subprocess with no network access.
- Timeout prevents denial-of-service from infinite-loop diagrams.
- Input is sanitized: only mermaid syntax is accepted (no arbitrary code execution).
- Binary is statically linked — no shared library exploitation surface.

## 9. Conclusion

`merman-cli` is the best option for offline, air-gapped Mermaid diagram rendering in mdutil. It provides:
- A single static binary with no runtime dependencies.
- Cross-platform support (Linux, macOS, Windows).
- Built-in SVG rendering without browser dependency.
- Graceful fallback for complex diagrams via system Chromium.
- Fast execution suitable for export workflows.

The bundled binary approach means users get mermaid rendering out of the box with zero configuration.

---

## References

- [merman-cli GitHub](https://github.com/Latias94/merman/releases) (v0.7.0)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [Rust cargo documentation](https://doc.rust-lang.org/cargo/)
