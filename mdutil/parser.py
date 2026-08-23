"""Markdown parser module - parses Markdown into simple tokens."""

from __future__ import annotations

import re
from typing import Any

Token = dict[str, Any]


_CODE_FENCE_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})[ \t]*(?P<info>.*)$")
_HEADING_RE = re.compile(r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<text>.*)|[ \t]*)$")
_LIST_RE = re.compile(r"^(?P<indent> {0,8})(?:(?P<unordered>[-+*])|(?P<ordered>\d{1,9}[.)]))[ \t]+(?P<item>.*)$")
_AUTOLINK_RE = re.compile(r"<((?:https?|ftp)://[^>]+)>")
_FOOTNOTE_DEF_RE = re.compile(r"^\[\^([a-zA-Z0-9]+)\]:\s?(.*)$", re.IGNORECASE)
_FOOTNOTE_REF_RE = re.compile(r"\[\^([a-zA-Z0-9]+)\]", re.IGNORECASE)
_DEFINITION_RE = re.compile(r"^[ \t]*:[ \t]+(.*)$")


def parse_markdown(content: str) -> list[Token]:
    """Parse Markdown content into a structured token list.

    Returns a list of tokens with an attached ``footnotes`` dict (not a
    regular list element) containing any footnote definitions found at the
    end of the document.  Footnote definitions are removed from the main
    token stream and emitted as ``footnote_definition`` tokens.
    """
    tokens: list[Token] = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Blank lines → emit immediately
        if not line.strip():
            tokens.append({"type": "blank", "content": "", "text": ""})
            i += 1
            continue

        # --- block elements (single-pass detection) ---
        # Code fence (including mermaid)
        code_block, end_pos = extract_code_block(lines, i)
        if code_block:
            content_text = code_block["content"] or ""
            language = code_block["language"]
            if is_mermaid_block(language):
                tokens.append({
                    "type": "mermaid",
                    "content": content_text,
                    "language": language,
                    "text": content_text,
                })
            else:
                tokens.append({
                    "type": "code",
                    "content": content_text,
                    "language": language,
                    "text": content_text,
                })
            i = end_pos
            continue

        heading = _parse_heading(line)
        if heading:
            tokens.append(heading)
            i += 1
            continue

        if _is_horizontal_rule(line):
            text = line.strip()
            tokens.append({"type": "horizontal_rule", "content": text, "text": text})
            i += 1
            continue

        # Table: need to call extract_table to get end_pos
        table, end_pos = extract_table(lines, i)
        if table:
            tokens.append({
                "type": "table",
                "content": table["content"],
                "text": table["content"],
                "headers": table["headers"],
                "alignments": table["alignments"],
                "rows": table["rows"],
            })
            i = end_pos
            continue

        # Blockquote
        if line.strip().startswith(">"):
            blockquote_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                blockquote_lines.append(lines[i])
                i += 1
            tokens.append({
                "type": "blockquote",
                "content": "\n".join(blockquote_lines),
                "text": "\n".join(blockquote_lines),
            })
            continue

        # List
        list_token, end_pos = _extract_list(lines, i)
        if list_token:
            tokens.append(list_token)
            i = end_pos
            continue

        # Definition list: Term\n:   Definition
        def_token, end_pos = _extract_definition_list(lines, i)
        if def_token:
            tokens.append(def_token)
            i = end_pos
            continue

        # --- multi-line paragraph ---
        paragraph_lines = [line]
        paragraph_inline = [_parse_inline(line.strip())]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if not nxt.strip():
                break
            # Footnote definitions must not be merged with other paragraphs
            if _FOOTNOTE_DEF_RE.match(nxt.strip()):
                break
            if (_CODE_FENCE_RE.match(nxt) or _parse_heading(nxt)
                    or _is_horizontal_rule(nxt)
                    or _LIST_RE.match(nxt)
                    or nxt.strip().startswith(">")
                    or (i + 1 < len(lines)
                        and "|" in nxt and "|" in lines[i + 1]
                        and _is_table_separator(lines[i + 1].strip()))):
                break
            paragraph_lines.append(nxt)
            paragraph_inline.append(_parse_inline(nxt.strip()))
            i += 1

        # Join multi-line paragraphs with a single space (Markdown soft break).
        if len(paragraph_inline) == 1:
            para_content = paragraph_inline[0]["content"]
            para_spans = paragraph_inline[0]["spans"]
        else:
            para_content = " ".join(pi["content"] for pi in paragraph_inline)
            para_spans = []
            for pi in paragraph_inline:
                para_spans.extend(pi["spans"])
        para_text = " ".join(pl.strip() for pl in paragraph_lines)
        tokens.append({
            "type": "paragraph",
            "content": para_content,
            "text": para_text,
            "spans": para_spans,
            "source_lines": [pl.strip() for pl in paragraph_lines],
            "content_lines": [pi["content"] for pi in paragraph_inline],
        })

    # Post-process: collect footnote definitions and remove from main tokens.
    footnotes, filtered = _collect_footnote_definitions(tokens)
    # Append footnote_definition tokens at the end of the main stream.
    for fn_id, fn_text in footnotes.items():
        filtered.append({
            "type": "footnote_definition",
            "id": fn_id,
            "content": fn_text,
            "text": fn_text,
        })
    return filtered


def extract_code_block(lines: list[str], start_index: int) -> tuple[dict[str, str | None] | None, int]:
    """Extract a fenced code block from lines."""
    if start_index >= len(lines):
        return None, start_index

    opening = _CODE_FENCE_RE.match(lines[start_index])
    if not opening:
        return None, start_index

    fence = opening.group("fence")
    marker = fence[0]
    length = len(fence)
    info = opening.group("info").strip()
    if marker == "`" and "`" in info:
        return None, start_index

    language = info.split(None, 1)[0] if info else None
    closing_re = re.compile(rf"^ {{0,3}}{re.escape(marker)}{{{length},}}[ \t]*$")

    i = start_index + 1
    while i < len(lines):
        if closing_re.match(lines[i]):
            code_content = "\n".join(lines[start_index + 1 : i])
            return {"content": code_content, "language": language}, i + 1
        i += 1

    # Unclosed fence: treat remaining lines as code until EOF.
    # This matches common Markdown implementations (e.g. CommonMark)
    # where an opening fence without a matching close consumes to end.
    code_content = "\n".join(lines[start_index + 1 :])
    return {"content": code_content, "language": language}, len(lines)


def is_mermaid_block(language: str | None) -> bool:
    """Return True if the code block's language indicates a Mermaid diagram.

    Args:
        language: The info-string language token from a fenced code block.

    Returns:
        True if the block is a Mermaid diagram block (`` ```mermaid ``).
    """
    if language is None:
        return False
    lang = language.strip().lower()
    # Accept "mermaid", "mermaid: title", "mermaid:something", etc.
    return lang.split(":")[0].strip() == "mermaid"


def extract_table(lines: list[str], start_index: int) -> tuple[dict[str, Any] | None, int]:
    """Extract a basic pipe-delimited Markdown table."""
    if start_index + 1 >= len(lines):
        return None, start_index

    header = lines[start_index].strip()
    separator = lines[start_index + 1].strip()
    if "|" not in header or not _is_table_separator(separator):
        return None, start_index

    headers = _split_table_row(header)
    separator_cells = _split_table_row(separator)
    if len(headers) != len(separator_cells):
        return None, start_index

    alignments = [_alignment_for_separator(cell) for cell in separator_cells]
    table_lines = [lines[start_index], lines[start_index + 1]]
    rows: list[list[str]] = []
    i = start_index + 2
    while i < len(lines) and "|" in lines[i] and lines[i].strip():
        row = _split_table_row(lines[i].strip())
        if len(row) != len(headers):
            break
        rows.append(row)
        table_lines.append(lines[i])
        i += 1

    return {
        "content": "\n".join(table_lines),
        "header": table_lines[0],
        "headers": headers,
        "alignments": alignments,
        "rows": rows,
    }, i


def _parse_heading(line: str) -> Token | None:
    match = _HEADING_RE.match(line)
    if not match:
        return None

    level = len(match.group("marks"))
    text = (match.group("text") or "").strip()
    text = re.sub(r"[ \t]+#+[ \t]*$", "", text).rstrip()
    content = f"{'#' * level} {text}" if text else "#" * level
    return {"type": "heading", "content": content, "level": level, "text": text}


_TASK_CHECK_RE = re.compile(r"^\s*\[([ xX])\]\s+(.*)")


def _is_horizontal_rule(line: str) -> bool:
    stripped = line.strip()
    compact = re.sub(r"[ \t]", "", stripped)
    return len(compact) >= 3 and compact[0] in "-*_" and all(char == compact[0] for char in compact)


def _extract_list(lines: list[str], start_index: int) -> tuple[Token | None, int]:
    first = _LIST_RE.match(lines[start_index])
    if not first:
        return None, start_index

    ordered = first.group("ordered") is not None
    parent_indent = len(first.group("indent"))
    list_lines = [lines[start_index]]
    raw_items = [(first.group("item"), parent_indent)]
    i = start_index + 1

    # Collect top-level items and detect nested sub-lists
    while i < len(lines):
        line = lines[i]

        # Blank line: only bridge if next non-blank line is nested deeper
        if not line.strip():
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                next_match = _LIST_RE.match(lines[j])
                if next_match and len(next_match.group("indent")) > parent_indent:
                    # Next line is nested: bridge the blank line
                    i = j
                    continue
            # Blank line is a list terminator
            break

        match = _LIST_RE.match(line)
        if not match:
            break

        item_indent = len(match.group("indent"))
        item_ordered = match.group("ordered") is not None

        # Same indent level and marker type: continuation
        if item_indent == parent_indent and item_ordered == ordered:
            list_lines.append(line)
            raw_items.append((match.group("item"), item_indent))
            i += 1
            continue

        # More indented: could be a nested list (mixed marker types allowed)
        if item_indent > parent_indent:
            # Collect all nested lines
            nested_lines = [line]
            nested_indent = item_indent
            i += 1

            while i < len(lines):
                nl = lines[i]
                if not nl.strip():
                    # Look ahead: if next non-blank is same indent or deeper, continue
                    m = i + 1
                    while m < len(lines) and not lines[m].strip():
                        m += 1
                    if m < len(lines):
                        nm_next = _LIST_RE.match(lines[m])
                        if nm_next and len(nm_next.group("indent")) >= nested_indent:
                            i += 1
                            continue
                    break

                nm = _LIST_RE.match(nl)
                if not nm:
                    break
                nm_indent = len(nm.group("indent"))
                if nm_indent < nested_indent:
                    break
                if nm_indent > nested_indent:
                    # Deeper nesting; collect it too
                    nested_lines.append(nl)
                    i += 1
                    continue
                if nm_indent == nested_indent:
                    nested_lines.append(nl)
                    i += 1
                    continue
                break

            # Recursively parse nested list
            sub_token, _ = _extract_list(nested_lines, 0)
            if sub_token:
                # Attach sub-list to the last raw item
                raw_items[-1] = (raw_items[-1][0], item_indent, sub_token)
            continue

        # Different indent or marker type: end of list
        break

    text = "\n".join(list_lines)

    # Detect whether this list contains task items (- [ ] / - [x]).
    has_task = any(_TASK_CHECK_RE.match(item) for item, _, *rest in raw_items if not isinstance(item, tuple))
    has_task = has_task or any(
        _TASK_CHECK_RE.match(item) for item, _, *rest in raw_items if isinstance(item, tuple) and isinstance(item[0], str)
    )

    # Parse inline formatting for each list item.
    parsed_items: list[dict[str, Any]] = []
    item_texts: list[str] = []
    for item_data in raw_items:
        if isinstance(item_data, tuple):
            raw_item, _, *sub = item_data
            sub_list = sub[0] if sub else None
        else:
            raw_item = item_data
            sub_list = None

        task_match = _TASK_CHECK_RE.match(raw_item)
        if task_match:
            checked = task_match.group(1).lower() == "x"
            item_text = task_match.group(2)
        else:
            checked = None
            item_text = raw_item

        inline = _parse_inline(item_text)
        parsed_item = {
            "text": item_text,
            "content": inline["content"],
            "spans": inline["spans"],
            "checked": checked,
            "task": task_match is not None,
        }
        if sub_list:
            parsed_item["sub_list"] = sub_list
        parsed_items.append(parsed_item)
        item_texts.append(item_text)

    return {
        "type": "list",
        "content": text,
        "text": text,
        "ordered": ordered,
        "task": has_task,
        "items": item_texts,
        "parsed_items": parsed_items,
    }, i


def _extract_definition_list(lines: list[str], start_index: int) -> tuple[Token | None, int]:
    """Extract a definition list starting at ``start_index``.

    Definition list syntax::

        Term
        :   Definition

    Multiple terms can share a definition::

        Term1
        Term2
        :   Shared definition

    Args:
        lines: All document lines.
        start_index: Current line index in the document.

    Returns:
        A tuple of (definition token dict or None, next index to process).
    """
    if start_index >= len(lines):
        return None, start_index

    first_line = lines[start_index]
    if not first_line.strip():
        return None, start_index

    # Look ahead to find the first definition line (: ...)
    # Terms can span multiple lines before the definition appears
    terms_start = start_index
    i = start_index + 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            break
        if _DEFINITION_RE.match(line):
            break
        # If we hit a block element, this is not a definition list
        if (_CODE_FENCE_RE.match(line)
                or _parse_heading(line)
                or _is_horizontal_rule(line)
                or _LIST_RE.match(line)
                or line.strip().startswith(">")):
            return None, start_index
        i += 1

    # No definition line found
    if i >= len(lines) or not _DEFINITION_RE.match(lines[i]):
        return None, start_index

    # Collect terms from start_index to i
    terms: list[str] = [lines[j].strip() for j in range(terms_start, i)]

    # Collect definition lines
    definitions: list[str] = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            break
        def_match = _DEFINITION_RE.match(line)
        if not def_match:
            break
        definitions.append(def_match.group(1).strip())
        i += 1

    if not definitions:
        return None, start_index

    term_text = " / ".join(terms)
    # Build content with inline parsing on each definition
    parsed_defs: list[str] = []
    for defn in definitions:
        inline = _parse_inline(defn)
        parsed_defs.append(inline["content"])
    content = " ".join(parsed_defs)
    text = " ".join(definitions)

    return {
        "type": "definition",
        "terms": terms,
        "definitions": definitions,
        "content": content,
        "text": text,
        "term_text": term_text,
    }, i


def _parse_inline(text: str) -> dict[str, Any]:
    """Parse lightweight inline Markdown into renderable markup and span metadata."""
    content, spans = _parse_inline_segment(text)
    return {"content": content, "spans": spans}


def _collect_footnote_definitions(tokens: list[Token]) -> tuple[dict[str, str], list[Token]]:
    """Collect footnote definitions from the token stream.

    Scans for paragraph tokens whose raw text matches ``[^n]: text`` and
    extracts them into a mapping keyed by footnote index.  Returns a tuple
    of (footnotes dict, filtered token list with those paragraphs removed).
    """
    footnotes: dict[str, str] = {}
    filtered: list[Token] = []
    for token in tokens:
        if token.get("type") == "paragraph":
            raw_text = "".join(token.get("source_lines", []))
            def_match = _FOOTNOTE_DEF_RE.match(raw_text.strip())
            if def_match:
                fn_id = def_match.group(1)
                fn_text_raw = def_match.group(2).strip()
                # Parse inline formatting in footnote content
                inline_result = _parse_inline(fn_text_raw)
                fn_text = inline_result["content"]
                footnotes[fn_id] = fn_text
                continue  # skip this paragraph from main stream
        filtered.append(token)
    return footnotes, filtered


def _parse_image_dimensions(raw: str) -> tuple[str, int | None, int | None]:
    """Parse optional `=WxH` dimension hint from an image href string.

    GFM allows appending dimensions after the URL::

        ![alt](image.png =200x100)
        ![alt](image.png)        # no dimensions

    Returns:
        Tuple of (cleaned_src, width_or_None, height_or_None).
    """
    # Match optional =WxH at the end, after whitespace
    dim_match = re.search(r"\s+=(\d+)x(\d+)\s*$", raw)
    if dim_match:
        width = int(dim_match.group(1))
        height = int(dim_match.group(2))
        src = raw[: dim_match.start()].strip()
        return src, width, height
    return raw.strip(), None, None


def _parse_link_attributes(raw: str) -> tuple[str, str | None]:
    """Parse optional title attribute from a link href string.

    GFM allows appending a title after the URL::

        [text](url "title")
        [text](url "title" =100x200)
        [text](url)              # no title

    Returns:
        Tuple of (cleaned_href, title_or_None).
    """
    # Match optional =WxH dimension hint first (if present)
    dim_match = re.search(r"\s+=(\d+)x(\d+)\s*$", raw)
    stripped = raw
    if dim_match:
        stripped = raw[: dim_match.start()].strip()

    # Match optional "title" or 'title' at the end
    title_match = re.search(r'\s+(?:"(.*)"|\'(.*)\')\s*$', stripped)
    if title_match:
        title = title_match.group(1) if title_match.group(1) is not None else title_match.group(2)
        href = stripped[: title_match.start()].strip()
        # Re-append dimension hint if it was present
        if dim_match:
            href = href + raw[dim_match.start() :]
        return href, title
    return stripped, None


def _parse_inline_segment(text: str) -> tuple[str, list[dict[str, str]]]:
    output: list[str] = []
    spans: list[dict[str, str]] = []
    index = 0

    while index < len(text):
        char = text[index]

        if char == "\\" and index + 1 < len(text):
            output.append(text[index + 1])
            index += 2
            continue

        if char == "`":
            end = _find_unescaped(text, "`", index + 1)
            if end != -1:
                code_text = text[index + 1 : end]
                spans.append({"type": "inline_code", "text": code_text})
                output.append(f"<code>{code_text}</code>")
                index = end + 1
                continue

        if text.startswith("**", index):
            end = _find_unescaped(text, "**", index + 2)
            if end != -1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 2 : end])
                spans.extend(inner_spans)
                strong_text = _visible_inline_text(inner_content)
                spans.append({"type": "strong", "text": strong_text})
                output.append(f"<strong>{inner_content}</strong>")
                index = end + 2
                continue

        # Strikethrough: ~~text~~
        if text.startswith("~~", index):
            end = _find_unescaped(text, "~~", index + 2)
            if end != -1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 2 : end])
                spans.extend(inner_spans)
                strong_text = _visible_inline_text(inner_content)
                spans.append({"type": "strikethrough", "text": strong_text})
                output.append(f"<del>{inner_content}</del>")
                index = end + 2
                continue

        # Highlight: ==text==
        if text.startswith("==", index):
            end = _find_unescaped(text, "==", index + 2)
            if end != -1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 2 : end])
                spans.extend(inner_spans)
                highlight_text = _visible_inline_text(inner_content)
                spans.append({"type": "highlight", "text": highlight_text})
                output.append(f"<mark>{inner_content}</mark>")
                index = end + 2
                continue

        # Subscript: ~text~
        if char == "~" and index + 1 < len(text):
            end = _find_unescaped(text, "~", index + 1)
            if end != -1 and end > index + 1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 1 : end])
                spans.extend(inner_spans)
                subscript_text = _visible_inline_text(inner_content)
                spans.append({"type": "subscript", "text": subscript_text})
                output.append(f"<sub>{inner_content}</sub>")
                index = end + 1
                continue

        # Superscript: ^text^
        if char == "^" and index + 1 < len(text):
            end = _find_unescaped(text, "^", index + 1)
            if end != -1 and end > index + 1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 1 : end])
                spans.extend(inner_spans)
                superscript_text = _visible_inline_text(inner_content)
                spans.append({"type": "superscript", "text": superscript_text})
                output.append(f"<sup>{inner_content}</sup>")
                index = end + 1
                continue

        if char == "*" :
            end = _find_unescaped(text, "*", index + 1)
            if end != -1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 1 : end])
                spans.extend(inner_spans)
                emphasis_text = _visible_inline_text(inner_content)
                spans.append({"type": "emphasis", "text": emphasis_text})
                output.append(f"<em>{inner_content}</em>")
                index = end + 1
                continue

        # Underscore-style emphasis: _text_
        if char == "_" and index + 1 < len(text):
            end = _find_unescaped(text, "_", index + 1)
            if end != -1 and end > index + 1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 1 : end])
                spans.extend(inner_spans)
                emphasis_text = _visible_inline_text(inner_content)
                spans.append({"type": "emphasis", "text": emphasis_text})
                output.append(f"<em>{inner_content}</em>")
                index = end + 1
                continue

        # Math notation: $...$
        if char == "$" and index + 1 < len(text):
            end = _find_unescaped(text, "$", index + 1)
            if end != -1:
                math_content = text[index + 1 : end]
                spans.append({"type": "math", "text": math_content})
                output.append(f"<math>{math_content}</math>")
                index = end + 1
                continue

        # Footnote reference: [^1]
        if text.startswith("[^", index):
            ref_match = _FOOTNOTE_REF_RE.match(text, index)
            if ref_match:
                fn_id = ref_match.group(1)
                spans.append({"type": "footnote_ref", "id": fn_id})
                output.append(f'<fnref id="{fn_id}">')
                index = ref_match.end()
                continue

        # Image: ![alt](url "title" =WxH)
        if char == "!" and index + 1 < len(text) and text[index + 1] == "[":
            close_label = _find_unescaped(text, "]", index + 2)
            if close_label != -1 and close_label + 1 < len(text) and text[close_label + 1] == "(":
                close_href = _find_unescaped(text, ")", close_label + 2)
                if close_href != -1:
                    alt_content, alt_spans = _parse_inline_segment(text[index + 2 : close_label])
                    raw_href = text[close_label + 2 : close_href].strip()
                    # Parse optional =WxH dimension hint appended after the URL
                    src, img_width, img_height = _parse_image_dimensions(raw_href)
                    spans.extend(alt_spans)
                    img_span: dict[str, Any] = {
                        "type": "image",
                        "text": _visible_inline_text(alt_content),
                        "src": src,
                    }
                    if img_width is not None:
                        img_span["width"] = img_width
                    if img_height is not None:
                        img_span["height"] = img_height
                    spans.append(img_span)
                    # Reconstruct HTML with optional width/height attributes
                    img_attrs = f'src="{src}" alt="{alt_content}"'
                    if img_width is not None:
                        img_attrs += f' width="{img_width}"'
                    if img_height is not None:
                        img_attrs += f' height="{img_height}"'
                    output.append(f"<img {img_attrs}>")
                    index = close_href + 1
                    continue

        if char == "[":
            close_label = _find_unescaped(text, "]", index + 1)
            if close_label != -1 and close_label + 1 < len(text) and text[close_label + 1] == "(":
                close_href = _find_unescaped(text, ")", close_label + 2)
                if close_href != -1:
                    link_content, link_spans = _parse_inline_segment(text[index + 1 : close_label])
                    raw_href = text[close_label + 2 : close_href]
                    # Parse optional title attribute from the href string
                    href, link_title = _parse_link_attributes(raw_href)
                    spans.extend(link_spans)
                    span_data: dict[str, Any] = {
                        "type": "link",
                        "text": _visible_inline_text(link_content),
                        "href": href,
                    }
                    if link_title is not None:
                        span_data["title"] = link_title
                    spans.append(span_data)
                    # Reconstruct HTML with optional title attribute
                    attrs = f'href="{_escape_html(href)}"'
                    if link_title is not None:
                        attrs += f' title="{_escape_html(link_title)}"'
                    output.append(f'<a {attrs}>{link_content}</a>')
                    index = close_href + 1
                    continue

        # Autolinks: <https://example.com>
        if char == "<":
            autolink_match = _AUTOLINK_RE.match(text, index)
            if autolink_match:
                url = autolink_match.group(1)
                spans.append({"type": "link", "text": url, "href": url})
                output.append(f'<a href="{url}">{url}</a>')
                index = autolink_match.end()
                continue

        output.append(char)
        index += 1

    return "".join(output), spans


def _find_unescaped(text: str, marker: str, start: int) -> int:
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text.startswith(marker, index):
            return index
        index += 1
    return -1


def _visible_inline_text(text: str) -> str:
    text = re.sub(r"<a\s+[^>]*>(.*?)</a>", r"\1", text)
    text = re.sub(r"<fnref\s+id=\"\d+\">", "", text)
    text = re.sub(r"</?(?:strong|em|code|fnref)>", "", text)
    return text


def _escape_html(text: str) -> str:
    """Escape HTML special characters in text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _is_table_separator(line: str) -> bool:
    """Return True if a line looks like a Markdown table separator."""
    if "|" not in line:
        return False
    cells = _split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _alignment_for_separator(cell: str) -> str | None:
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return "center"
    if left:
        return "left"
    if right:
        return "right"
    return None
