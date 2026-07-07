"""Search logic for mdutil."""

from dataclasses import dataclass
from typing import List
import re

@dataclass
class SearchState:
    """Tracks the state of a search operation."""
    query: str
    matches: List[int]
    current_index: int = 0

def find_all_matches(text: str, query: str) -> List[int]:
    """
    Find all starting character indices for a query in the given text.
    Supports simple string matching and regex (if query starts with /).
    """
    if not query:
        return []

    if query.startswith("/"):
        # Basic regex support: allow characters that are valid in regex
        # but escape the actual slash for the engine.
        regex_query = query[1:]
        try:
            # Use finditer to get all matches
            # We use re.DOTALL to ensure . matches newlines if necessary
            return [m.start() for m in re.finditer(regex_query, text, re.DOTALL)]
        except re.error:
            # Fallback to literal if regex is invalid
            return _find_literal_matches(text, regex_query)
    else:
        return _find_literal_matches(text, query)

def _find_literal_matches(text: str, query: str) -> List[int]:
    """Find all starting indices of a literal string in text."""
    indices = []
    start = 0
    while True:
        idx = text.find(query, start)
        if idx == -1:
            break
        indices.append(idx)
        start = idx + 1
    return indices
