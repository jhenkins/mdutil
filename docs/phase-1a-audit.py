"""
KB-050: Parser coverage audit against CommonMark/GFM spec.

Systematic audit: feed representative inputs to parse_markdown() and render(),
classify each feature as Supported/Partially/Not supported.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mdutil.parser import parse_markdown
from mdutil.renderer import render

THEME = "colored"

FEATURES = [
    # --- Block elements already supported ---
    ("Paragraphs (plain)", "Hello world.\n\nSecond paragraph."),
    ("Headings h1-h6", "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"),
    ("Horizontal rule", "---\n***\n___\n\n- - -"),
    ("Blockquotes", "> quote line 1\n> quote line 2\n\n> > nested quote"),
    ("Ordered lists", "1. one\n2. two\n3. three"),
    ("Unordered lists", "- item a\n- item b\n- item c\n\n+ item x\n* item y"),
    ("Code fences (basic)", "```python\nprint('hi')\n```"),
    ("Code fences (tilde)", "~~~js\nconst x = 1;\n~~~"),
    ("Tables", "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"),
    ("Tables (align)", "| L | C | R |\n|:--|:-:|--:|\n| 1 | 2 | 3 |"),

    # --- Existing inline features ---
    ("Bold (**)", "This is **bold text**."),
    ("Italic (*)", "This is *italic text*."),
    ("Italic (_)", "This is _italic text_."),
    ("Inline code (`)", "Use `print()` for output."),
    ("Links [text](url)", "[Example](https://example.com)"),
    ("Autolinks <url>", "Visit <https://example.com>"),
    ("Escaped chars (\\*)", "Literal star: \\*not italic\\*"),

    # --- GFM/CommonMark features NOT yet supported ---
    ("Strikethrough ~~text~~", "This is ~~deleted~~ text."),
    ("Task list [ ]", "- [ ] unchecked\n- [x] checked\n- [X] also checked"),
    ("Math inline $E=mc^2$", "Einstein said $E=mc^2$."),
    ("Math display $$...$$", "$$\n\\sum_{i=0}^{n} i^2\n$$"),
    ("Footnote ref [^1]", "Text with a footnote[^1].\n\n[^1]: Footnote definition text."),
    ("Footnote name [^label]", "See note[^note].\n\n[^note]: Detailed note text here."),
    ("Subscript H~2~O", "Water is H~2~O."),
    ("Superscript e^2", "The value is e^2^."),
    ("Highlight ==text==", "This is ==important== text."),
    ("Definition list", "Term\n:   Definition\n\nAnother term\n:   Another definition"),
    ("Image ![alt](url)", "![Logo](https://example.com/logo.png)"),
    ("Image with title", '![alt](image.png "Title")'),
    ("Link with title", '[link](http://example.com "Tooltip")'),
    ("Nested lists (indent)", "- item 1\n    - nested 1a\n    - nested 1b\n- item 2"),
    ("Nested lists (mixed)", "1. ordered\n    - nested unordered\n    - nested unordered\n2. ordered again"),
    ("Fenced code bare (no lang)", "```\ncode without language\n```"),
    ("Fenced code info string", "```mermaid: flowchart\ngraph TD\nA-->B\n```"),
    ("Multi-line paragraph (soft break)", "Line one\ncontinues here\nline three"),
    ("Escaped backslash (\\)", "Literal backslash: \\\" \\"),
]

results = []
for name, md in FEATURES:
    try:
        tokens = parse_markdown(md)
        types = [t["type"] for t in tokens]
        # Render with a theme (load_theme requires 'colored', not 'default')
        output = render(tokens, theme=THEME)
        output = output.replace("\033[0m", "").replace("\033[1m", "")  # strip ANSI
        output = output.replace("\033[38;2;", "").replace("m", "")
    except Exception as e:
        types = []
        output = f"ERROR: {e}"

    results.append({
        "feature": name,
        "md": md,
        "token_types": types,
        "render_preview": output[:80].replace("\n", "\\n"),
    })

# Print results
for r in results:
    feature = r["feature"]
    types = ", ".join(r["token_types"])
    preview = r["render_preview"][:60]
    print(f"[{len(types):3d}] {feature}")
    print(f"       Types: {types}")
    print(f"       Render: {preview}")
    print()

# Classification summary
print("\n=== CLASSIFICATION ===")
# Re-run with tokens preserved
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mdutil.parser import parse_markdown
from mdutil.renderer import render

THEME = "colored"
for r in results:
    name = r["feature"]
    md = r["md"]
    types = r["token_types"]
    tokens_for_check = parse_markdown(md)
    # Check for specific token types we know we want
    if "mermaid" in types:
        status = "Supported (mermaid)"
    elif "heading" in types:
        status = "Supported (heading)"
    elif "table" in types:
        status = "Supported (table)"
    elif "list" in types:
        status = "Supported (list)"
    elif "code" in types:
        status = "Supported (code)"
    elif "blockquote" in types:
        status = "Supported (blockquote)"
    elif "paragraph" in types:
        # Paragraph - check if inline markup survived
        if any(s.get("type") == "strong" for t in tokens for s in t.get("spans", [])):
            status = "Partially supported (bold in paragraph)"
        else:
            status = "Not yet supported (no new feature detected)"
    else:
        status = "Unknown"
    print(f"  {status:50s} ← {name}")
