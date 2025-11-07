"""Naming heuristics for initial TDD seeding.

Pure helper functions extracting a target function name from kata description
and/or existing test code. Functions in this module must remain pure.
"""
from __future__ import annotations
import re
from typing import Set

# Ordered preferred names for common katas; extend cautiously.
_PREFERRED_BY_KEYWORD = [
    ("mars", ["execute_commands", "move_rover", "navigate"]),
    ("rover", ["execute_commands", "move_rover", "navigate"]),
    ("fizz", ["fizzbuzz"]),
    ("prime", ["is_prime"]),
    ("string", ["process", "transform"]),
]

_IDENTIFIER_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b")


def choose_target_function(kata_description: str) -> str:
    """Select a deterministic target function name.

    Strategy:
    - Match known keywords to preferred name list in order.
    - Fallback: extract words, pick shortest >=3 chars that is not a python keyword,
      then append an action verb if too generic.
    Pure function.
    """
    lower = kata_description.lower()
    for kw, names in _PREFERRED_BY_KEYWORD:
        if kw in lower:
            return names[0]
    # Fallback extraction
    words = [w for w in _IDENTIFIER_RE.findall(lower) if len(w) >= 3]
    if not words:
        return "solve"
    candidate: str = sorted(words, key=len)[0]
    if candidate in {"kata", "test", "code", "data", "list"}:
        return f"process_{candidate}" if candidate != "kata" else "solve_kata"
    return candidate


def extract_called_functions(test_code: str) -> Set[str]:
    """Extract function names called in test code (excluding test_ functions). Pure."""
    names: Set[str] = set()
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", test_code):
        n = match.group(1)
        if n.startswith("test_"):
            continue
        names.add(n)
    return names
