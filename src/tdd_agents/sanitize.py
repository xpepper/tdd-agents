"""Sanitization helpers for LLM-generated Python snippets.

Pure functions removing markdown code fences and trivial surrounding noise.
"""
from __future__ import annotations
import re

FENCE_PATTERN = re.compile(r"^```(?:python|py)?\n(.*?)\n```$", re.DOTALL)
MULTI_FENCE_PATTERN = re.compile(r"```(?:python|py)?\n(.*?)\n```", re.DOTALL)
TRIPLE_BACKTICKS = re.compile(r"```")


def strip_code_fences(code: str) -> str:
    """Remove leading/trailing markdown code fences if present.

    Accepts fenced blocks like ```python\n...\n``` or ```\n...\n```.
    Returns inner content unchanged otherwise.
    Pure function.
    """
    text = code.strip()
    m = FENCE_PATTERN.match(text)
    if m:
        inner = m.group(1).rstrip()
        return inner + "\n"
    # Generic fallback: if lone backticks present, drop all triple backticks
    if text.startswith("```") and text.endswith("```"):
        inner = TRIPLE_BACKTICKS.sub("", text).strip().rstrip()
        return inner + "\n"
    return code


def sanitize_snippet(code: str) -> str:
    """Apply all snippet sanitizations.

    Currently: strip fences; if multiple fenced blocks detected concatenate their inner contents
    separated by blank lines. Ensures exactly one trailing newline.
    Pure function.
    """
    # First, detect multiple fenced blocks anywhere in text
    blocks = MULTI_FENCE_PATTERN.findall(code)
    if len(blocks) > 1:
        joined = "\n\n".join(b.rstrip() for b in blocks if b.strip())
        return joined.rstrip() + "\n"
    cleaned = strip_code_fences(code)
    return cleaned.rstrip() + "\n" if cleaned else "\n"