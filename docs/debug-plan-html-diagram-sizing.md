# Debug Plan: HTML Diagram Sizing

## Problem

Mermaid diagrams in HTML export are too large. The inline `style="max-width: XXXpx"` on SVG elements overrides CSS rules, and diagrams are rendered at their full natural size (e.g., 864px for sequence diagrams) instead of fitting the document content area.

## Root Cause

`MermanRenderer.render_mermaid_svg()` passes SVG output directly to HTML export without any size constraints. merman-cli produces SVGs with an inline `style="max-width: NNNpx"` matching the diagram's natural viewBox width. The CSS rule `.mermaid svg { max-width: 100%; height: auto; }` is overridden by this inline style.

## Evidence from `tests/tmp/test_mermaid_diagrams.html`

| Diagram | viewBox | max-width (inline) | Problem |
|---------|---------|-------------------|---------|
| flowchart | 481×508 px | 481 px | Too big for 960px container |
| sequence | 864×435 px | 864 px | Way too wide |
| stateDiagram | 236×412 px | 236 px | Needs shrink |
| classDiagram | 252×668 px | 252 px | Needs shrink |

## Fix: Shrink SVG inline max-width by 40-50%

### Option A: Post-process SVG after render (preferred)
- After `merman-cli` produces the SVG, modify the inline `max-width` style to be 50% of the natural width
- This keeps the viewBox intact (diagram content unchanged) but constrains the rendered size
- Implementation: parse SVG `<svg>` tag, compute `natural_width = viewBox_width`, set `max-width = natural_width * 0.5`
- Add to `MermanRenderer.render_mermaid_svg()` or `HtmlExporter._render_mermaid()`

### Option B: Use merman-cli `--rasterFitWidth` (for PNG path only)
- Not applicable to HTML (SVG output), only relevant for PDF PNG path

### Option C: CSS-only fix
- Override inline style with `!important` in `.mermaid svg` CSS
- Less precise — doesn't respect diagram-specific sizing
- Simpler but loses per-diagram sizing control

## Recommendation

**Option A**: Post-process the SVG in `HtmlExporter._render_mermaid()` to set `max-width: 50%` of the diagram's natural viewBox width. This is the most surgical fix and preserves diagram readability.

## Implementation Steps

1. In `HtmlExporter._render_mermaid()` or `MermanRenderer.render_mermaid_svg()`:
   - Extract viewBox width from the SVG
   - Compute `constrained_width = viewBox_width * 0.5`
   - Replace inline `max-width` style with the constrained value
2. Add regression tests for diagram sizing
3. Verify in browser (open `tests/tmp/test_mermaid_diagrams.html` — should look reasonable at 800-1024px viewport)

## Verification

- Open `tests/tmp/test_mermaid_diagrams.html` in a browser
- All 4 diagrams should fit comfortably within the 960px content area
- Sequence diagram (864→432px) should be clearly readable
- No horizontal scrolling in HTML output
