"""Simple unified diff utility (pure function)."""

from __future__ import annotations
from difflib import unified_diff


def unified_code_diff(old: str, new: str, context: int = 3) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff_iter = unified_diff(
        old_lines, new_lines, fromfile="prev", tofile="current", n=context
    )
    return "".join(diff_iter)


__all__ = ["unified_code_diff"]
