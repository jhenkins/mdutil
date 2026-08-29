# Debug Plan: PDF Diagram Sizing (Page Overflow)

## Problem

Mermaid diagrams in PDF export overflow A4 pages in some cases. Tall diagrams (stateDiagram, classDiagram) render at a height that exceeds the available page content area, causing them to be cut off or overflow the page boundary.

## Root Cause

`PdfExporter._render_mermaid()` renders PNGs using `pdf.image(w=available_width)` which scales to fill the full page width. This makes tall diagrams overflow the page height because width-first scaling ignores the vertical constraint.

## Evidence from `tests/tmp/test_mermaid_diagrams.pdf`

When diagrams are scaled to fill the full page width (174mm A4 content):

| Diagram | viewBox | Scaled height | Fits A4? |
|---------|---------|--------------|----------|
| flowchart | 481×508 px | 184 mm | ✅ Yes |
| sequence | 864×435 px | 88 mm | ✅ Yes |
| stateDiagram | 236×412 px | 303 mm | ❌ No (exceeds 257mm) |
| classDiagram | 252×668 px | 462 mm | ❌ No (way too tall) |

## Fix: Dual-axis scaling constraint

### Approach: Fit-to-box with aspect-ratio preservation
- Instead of scaling to fill width only, scale to fit within a constrained box
- Target box: page width minus 20% margin on each side (80% of epw), height = page content height minus buffer
- If diagram fits in width-first: use that
- If diagram overflows height: scale to fit height instead, let width be proportional
- This ensures no diagram overflows a single page

### Implementation Steps

1. In `PdfExporter._render_mermaid()`:
   - Measure the PNG dimensions (in pixels)
   - Calculate the target box:
     - target_w = `available_width * 0.80` (80% of page width, 10% margin each side)
     - target_h = `available_height - 20mm` (page content minus 10mm top/bottom buffer)
   - Compute scale_w = target_w / png_width_mm
   - Compute scale_h = target_h / png_height_mm  
   - Use `min(scale_w, scale_h)` to get the constrained scale
   - Render with `w = png_width_mm * constrained_scale`

2. Handle very tall diagrams that still overflow:
   - If constrained height > page content height, add page break before diagram
   - Consider rendering as a code block fallback for extremely tall diagrams

## Verification

- Re-export test document to PDF
- All 4 diagrams should fit within a single A4 page
- No diagram should be cut off at page boundary
- Aspect ratio preserved for all diagrams
- Run full test suite: `pytest tests/ -x`

## Priority

This is a correctness bug — diagrams being cut off by page boundaries is a clear user-facing defect. Fix before v4.1 release.
