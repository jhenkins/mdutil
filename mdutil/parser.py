"""Markdown parser module - parses Markdown into simple tokens."""

from __future__ import annotations

import re
from typing import Any

Token = dict[str, Any]


_CODE_FENCE_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})[ \t]*(?P<info>.*)$")
_HEADING_RE = re.compile(r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<text>.*)|[ \t]*)$")
_LIST_RE = re.compile(r"^(?P<indent> {0,3})(?:(?P<unordered>[-+*])|(?P<ordered>\d{1,9}[.)]))[ \t]+(?P<item>.*)$")


def parse_markdown(content: str) -> list[Token]:
    """Parse Markdown content into a structured token list."""
    tokens: list[Token] = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            tokens.append({"type": "blank", "content": "", "text": ""})
            i += 1
            continue

        code_block, end_pos = extract_code_block(lines, i)
        if code_block:
            content_text = code_block["content"] or ""
            tokens.append(
                {
                    "type": "code",
                    "content": content_text,
                    "language": code_block["language"],
                    "text": content_text,
                }
            )
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

        table, end_pos = extract_table(lines, i)
        if table:
            tokens.append(
                {
                    "type": "table",
                    "content": table["content"],
                    "text": table["content"],
                    "headers": table["headers"],
                    "alignments": table["alignments"],
                    "rows": table["rows"],
                }
            )
            i = end_pos
            continue

        if line.strip().startswith(">"):
            blockquote_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                blockquote_lines.append(lines[i])
                i += 1
            tokens.append(
                {
                    "type": "blockquote",
                    "content": "\n".join(blockquote_lines),
                    "text": "\n".join(blockquote_lines),
                }
            )
            continue

        list_token, end_pos = _extract_list(lines, i)
        if list_token:
            tokens.append(list_token)
            i = end_pos
            continue

        text = line.strip()
        inline = _parse_inline(text)
        tokens.append(
            {
                "type": "paragraph",
                "content": inline["content"],
                "text": text,
                "spans": inline["spans"],
            }
        )
        i += 1

    return tokens


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

    return None, start_index


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


def _is_horizontal_rule(line: str) -> bool:
    stripped = line.strip()
    compact = re.sub(r"[ \t]", "", stripped)
    return len(compact) >= 3 and compact[0] in "-*_" and all(char == compact[0] for char in compact)


def _extract_list(lines: list[str], start_index: int) -> tuple[Token | None, int]:
    first = _LIST_RE.match(lines[start_index])
    if not first:
        return None, start_index

    ordered = first.group("ordered") is not None
    list_lines = [lines[start_index]]
    items = [first.group("item")]
    i = start_index + 1

    while i < len(lines):
        match = _LIST_RE.match(lines[i])
        if not match or (match.group("ordered") is not None) != ordered:
            break
        list_lines.append(lines[i])
        items.append(match.group("item"))
        i += 1

    text = "\n".join(list_lines)
    return {"type": "list", "content": text, "text": text, "ordered": ordered, "items": items}, i


def _parse_inline(text: str) -> dict[str, Any]:
    """Parse lightweight inline Markdown into renderable markup and span metadata."""
    content, spans = _parse_inline_segment(text)
    return {"content": content, "spans": spans}


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

        if char == "*":
            end = _find_unescaped(text, "*", index + 1)
            if end != -1:
                inner_content, inner_spans = _parse_inline_segment(text[index + 1 : end])
                spans.extend(inner_spans)
                emphasis_text = _visible_inline_text(inner_content)
                spans.append({"type": "emphasis", "text": emphasis_text})
                output.append(f"<em>{inner_content}</em>")
                index = end + 1
                continue

        if char == "[":
            close_label = _find_unescaped(text, "]", index + 1)
            if close_label != -1 and close_label + 1 < len(text) and text[close_label + 1] == "(":
                close_href = _find_unescaped(text, ")", close_label + 2)
                if close_href != -1:
                    link_content, link_spans = _parse_inline_segment(text[index + 1 : close_label])
                    href = text[close_label + 2 : close_href]
                    spans.extend(link_spans)
                    spans.append({"type": "link", "text": _visible_inline_text(link_content), "href": href})
                    output.append(f'<a href="{href}">{link_content}</a>')
                    index = close_href + 1
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
    text = re.sub(r"<a\s+href=\"[^\"]*\">(.*?)</a>", r"\1", text)
    return re.sub(r"</?(?:strong|em|code)>", "", text)


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
