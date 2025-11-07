"""Prompt template helpers for agents.
Pure functions returning formatted prompt strings.
"""

from __future__ import annotations
from typing import Dict, Any


def _latest_diff(state: Dict[str, Any]) -> str:
    diffs = state.get("code_diffs", []) or []
    return diffs[-1] if diffs else ""


def _last_heuristic(state: Dict[str, Any]) -> str:
    history = state.get("tdd_history", []) or []
    if not history:
        return ""
    last_cycle = history[-1]
    sup = last_cycle.get("supervisor_output", {}) or {}
    return str(sup.get("heuristic_reason", ""))


def _context_block(state: Dict[str, Any]) -> str:
    diff = _latest_diff(state)
    heuristic = _last_heuristic(state)
    parts = []
    if heuristic:
        parts.append(f"heuristic_reason: {heuristic}")
    if diff:
        parts.append("Latest unified diff:\n" + diff)
    return "\n".join(parts) if parts else "(no prior diff or heuristic context)"


def tester_prompt(state: Dict[str, Any]) -> str:
    kata = state.get("kata_description", "")
    history_len = len(state.get("tdd_history", []))
    context = _context_block(state)
    return (
        "You are a TDD test author. Produce ONE failing pytest test for the kata.\n"
        f"Kata description: {kata}\n"
        f"Previous cycles: {history_len}. If zero, start with simplest failing test.\n"
        f"Context:\n{context}\n"
        "Return ONLY the test function code (no imports unless needed)."
    )


def implementer_prompt(state: Dict[str, Any]) -> str:
    last_test = state.get("full_test_suite", "")
    context = _context_block(state)
    return (
        "You are an implementation agent. Provide minimal code to make the latest failing test pass.\n"
        "Return ONLY python code snippet (no explanations). If impossible yet, return a placeholder comment.\n"
        f"Latest test snippet:\n{last_test}\n"
        f"Context:\n{context}\n"
    )


def refactorer_prompt(state: Dict[str, Any]) -> str:
    current_code = state.get("final_code", "")
    context = _context_block(state)
    return (
        "You are a refactoring assistant. Suggest an improved version of the code without changing behavior.\n"
        "Keep it small; return ONLY code. If no improvements, echo original.\n"
        f"Current code:\n{current_code}\n"
        f"Context:\n{context}\n"
    )


def supervisor_prompt(state: Dict[str, Any]) -> str:
    context = _context_block(state)
    return (
        "You are supervising the TDD cycle. Provide a short status string summarizing progress: one of 'continue', 'done', or 'adjust'.\n"
        f"Context:\n{context}\n"
    )
