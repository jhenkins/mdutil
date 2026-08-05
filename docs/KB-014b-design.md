# KB-014b: Design Export Syntax Theme Mapping

## Design Decisions

### D1: Forward `syntax_theme` through `_export_single()`

**File:** `mdutil/cli.py`

**Change:** Add `options["syntax_theme"] = runtime["syntax_theme"]` in `_export_single()` after loading the exporter, alongside `options["pdf_paper_size"]` etc. The `theme` dict is already passed as a kwarg to `exporter.render()`.

```python
def _export_single(export_format: str, args, parsed, runtime):
    exporter = PdfExporter() if export_format == "pdf" else HtmlExporter()
    theme = load_theme(runtime["theme"], runtime["theme_file"])
    options: dict[str, Any] = {}

    if export_format == "pdf":
        options["pdf_paper_size"] = runtime.get("pdf_paper_size", "A4")
        options["pdf_margin_top"] = runtime.get("pdf_margin_top", 20)
        # ... other PDF options ...
        options["pdf_bookmarks"] = True
    elif export_format == "html":
        custom_css = getattr(args, "custom_css", None)
        if custom_css:
            # ... custom CSS handling ...

    # NEW: forward syntax_theme to both exporters
    options["syntax_theme"] = runtime["syntax_theme"]

    export_output = exporter.render(parsed, theme=theme, options=options)
    # ... rest unchanged ...
```

**Rationale:** Keeps the existing `render(tokens, theme=theme, options=options)` signature intact. The `syntax_theme` key is simply another entry in the options dict.

---

### D2: `highlight_code_html()` — Pygments HtmlFormatter

**File:** `mdutil/syntax_highlighter.py`

**Signature:**
```python
def highlight_code_html(
    code: str,
    language: str = "",
    syntax_theme: str = "default",
) -> str:
    """Highlight code for HTML output using Pygments HtmlFormatter.

    Returns HTML string with <span> tags bearing CSS classes.
    Returns raw `code` (unchanged) if language is empty or unknown.
    """
```

**Approach:**
1. Parse lexer (same fallback logic as existing `highlight_code()`)
2. Use `pygments.formatters.HtmlFormatter(style=style_name)` with `cssclass="mdutil-highlight"`
3. Use `cssstyle="text"` to get inline CSS, OR use the existing CSS generation in `html.py` to inject `.mdutil-highlight` rules
4. Return the full HTML output

**Style loading:** Reuse `_style_for_theme()` from existing highlighter, but pass `None` for theme (we only need the Pygments style, not merged theme overrides).

**HTML output format:**
```html
<div class="mdutil-highlight"><pre><span class="k">def</span> ...</pre></div>
```

**CSS injection:** The HTML exporter already generates CSS in `_generate_css()`. We add `.mdutil-highlight` rules that use the same Pygments style colors. Two options:

- **Option A:** Extract style colors at design time and embed in CSS (simple, no Pygments dependency in exporter)
- **Option B:** Let Pygments generate CSS via `HtmlFormatter.get_style_defs()` and inject into the `<style>` block (cleaner, uses Pygments directly)

**Decision:** **Option B** — use Pygments `get_style_defs()` to generate CSS rules for `.mdutil-highlight .c`, `.mdutil-highlight .k`, etc. Inject into the HTML exporter's `<style>` block before `</style>`. This keeps the theme authoritative — one source of truth for colors.

---

### D3: `highlight_code_pdf()` — Token Grouping Formatter

**File:** `mdutil/syntax_highlighter.py`

**Signature:**
```python
def highlight_code_pdf(
    code: str,
    language: str = "",
    syntax_theme: str = "default",
) -> list[dict[str, Any]]:
    """Highlight code for PDF output.

    Returns list of dicts: {"text": str, "color": (r, g, b) | None}
    Consecutive tokens with the same color are grouped into one segment.
    Returns list with single {"text": code, "color": None} if language is empty/unknown.
    """
```

**Approach:**
1. Parse lexer (same fallback)
2. Use Pygments `RawTokenFormatter` (or `Tokens` formatter) to get raw token types and text
3. Look up each token type's color from the Pygments style via `_extract_syntax_theme_colors()`
4. Group consecutive tokens with identical colors into single segments
5. Convert hex colors to `(r, g, b)` tuples for fpdf2 `set_text_color()`

**Why grouping?** fpdf2's `cell()` renders one text color at a time. Without grouping, a 100-character line with 20 token types would produce 20 separate cells. Grouping reduces this to ~3-5 segments per line.

**Fallback for unknown token types:** Use default text color `(0, 0, 0)`.

**Pseudocode:**
```python
def highlight_code_pdf(code, language, syntax_theme):
    if not language or language in _PLAIN_TEXT_LANGUAGE_ALIASES:
        return [{"text": code, "color": None}]

    try:
        lexer = get_lexer_by_name(language.strip().lower(), stripall=False)
    except ClassNotFound:
        return [{"text": code, "color": None}]

    colors = _extract_syntax_theme_colors(syntax_theme)
    tokens = list(tokenize(code, lexer))  # RawTokenFormatter output
    segments = []
    current = {"text": "", "color": None}

    for ttype, text in tokens:
        if not text:
            continue
        # Resolve color for this token type
        color = _resolve_pdf_color(ttype, colors)
        if current["color"] == color and current["text"]:
            current["text"] += text
        else:
            if current["text"]:
                segments.append(current)
            current = {"text": text, "color": color}

    if current["text"]:
        segments.append(current)

    return segments
```

**`_resolve_pdf_color()` logic:**
```python
def _resolve_pdf_color(ttype, colors):
    # Walk token type hierarchy: Token.Literal.String.Doc → Token.Literal.String → Token.Literal
    token_str = str(ttype)
    # Check exact match first
    if token_str in colors:
        hex_color = colors[token_str]
        return hex_to_rgb(hex_color)
    # Try parent types (Token.Literal.String.Doc → Token.Literal.String)
    while "." in token_str:
        token_str = token_str.rsplit(".", 1)[0]
        if token_str in colors:
            hex_color = colors[token_str]
            return hex_to_rgb(hex_color)
    return None  # No color = use default (black)
```

---

### D4: PDF Exporter Integration

**File:** `mdutil/export/pdf.py`

**Change:** Update `_render_code_block()` to use `highlight_code_pdf()`.

```python
def _render_code_block(self, pdf: FPDF, token: dict) -> None:
    content = token.get("content", "")
    syntax_theme = self.options.get("syntax_theme", "default")
    segments = highlight_code_pdf(content, token.get("language", ""), syntax_theme)

    pdf.set_font(self._font_for("mono"), size=9)
    pdf.set_fill_color(240, 240, 240)

    for segment in segments:
        color = segment.get("color")
        if color:
            r, g, b = color
            pdf.set_text_color(r, g, b)
        else:
            pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 5, segment["text"], new_x="LMARGIN", new_y="NEXT", fill=True)

    pdf.ln(5)
```

**Note:** The `self.options` attribute is needed. Add `__init__` or set options in `render()` to store them on the instance.

---

### D5: HTML Exporter Integration

**File:** `mdutil/export/html.py`

**Change:** Update `_render_code_block()` to use `highlight_code_html()`. Also need to inject Pygments style CSS into the `<style>` block.

```python
def render(self, tokens, theme, options):
    css = self._generate_css(theme)
    custom_css = options.get("custom_css", "")
    
    # NEW: collect all highlighted languages to generate CSS for them
    syntax_theme = options.get("syntax_theme", "default")
    style_defs = _get_pygments_style_defs(syntax_theme, "mdutil-highlight")
    
    body = self._render_tokens(tokens, syntax_theme=syntax_theme)
    
    style_block = f"{css}\n{style_defs}"
    if custom_css:
        style_block += f"\n/* Custom CSS */\n{custom_css}\n"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>mdutil export</title>
    <style>
{style_block}
    </style>
</head>
<body>
{body}
</body>
</html>"""
```

**`_render_code_block()` change:**
```python
def _render_code_block(self, token, syntax_theme=None):
    content = token.get("content", "")
    language = token.get("language", "")

    if language:
        highlighted = highlight_code_html(content, language, syntax_theme)
        # highlight_code_html returns <div class="mdutil-highlight">...
        # We want just the inner content for <pre><code>
        inner = _strip_outer_div(highlighted)
        return f'<pre><code class="language-{language}">{inner}</code></pre>'
    
    # Fallback: plain escaped code
    content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<pre><code>{content}</code></pre>"
```

**`_get_pygments_style_defs()` helper:**
```python
def _get_pygments_style_defs(syntax_theme, css_class):
    """Return CSS rules for Pygments tokens with the given style."""
    from pygments.styles import get_style_by_name
    from pygments.formatters import HtmlFormatter

    style = get_style_by_name(syntax_theme)
    formatter = HtmlFormatter(style=style, cssclass=css_class)
    return formatter.get_style_defs(".mdutil-highlight")
```

**CSS class naming:** Use `mdutil-highlight` as the CSS class. Pygments generates rules like `.mdutil-highlight .c { color: #888; }` which is self-contained and won't leak into the rest of the document.

**Custom CSS override:** Since Pygments CSS is injected before `custom_css`, users can override with `!important` or more specific selectors in their custom CSS. This preserves existing custom CSS behavior.

---

### D6: `_render_tokens()` Signature Update

**File:** `mdutil/export/html.py`

Both exporters need to pass `syntax_theme` through `_render_tokens()` to reach `_render_code_block()`. Add as optional kwarg:

```python
# pdf.py
def _render_tokens(self, pdf, tokens, syntax_theme="default"):
    for token in tokens:
        if token.get("type") == "code":
            self._render_code_block(pdf, token, syntax_theme)
            continue
        # ... rest unchanged ...

# html.py
def _render_tokens(self, tokens, syntax_theme="default"):
    for token in tokens:
        if token.get("type") == "code":
            self._render_code_block(token, syntax_theme)
            continue
        # ... rest unchanged ...
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `mdutil/cli.py` | Forward `syntax_theme` in `options` dict |
| `mdutil/syntax_highlighter.py` | Add `highlight_code_html()`, `highlight_code_pdf()`, `_get_pygments_style_defs()`, `_resolve_pdf_color()` |
| `mdutil/export/pdf.py` | Update `_render_code_block()` to use `highlight_code_pdf()`; store options on instance |
| `mdutil/export/html.py` | Update `_render_code_block()` to use `highlight_code_html()`; inject Pygments CSS |
| `tests/test_export.py` | Add tests for both exporters (Chunk 4) |

## Dependencies Between Chunks

```
KB-014a (trace) → KB-014b (design) → KB-014c (implement helpers) → KB-014d (tests)
```

This design doc (KB-014b) feeds directly into KB-014c where the actual implementation happens. The signatures, formats, and integration points are all specified here so KB-014c has a clear implementation plan.
