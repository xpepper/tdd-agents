"""Prompt template helpers for agents.
Pure functions returning formatted prompt strings.
"""

from __future__ import annotations
from typing import Dict, Any


def tester_prompt(state: Dict[str, Any]) -> str:
    kata = state.get("kata_description", "")
    history_len = len(state.get("tdd_history", []))
    return (
        "You are a TDD test author. Produce ONE failing pytest test for the kata.\n"
        f"Kata description: {kata}\n"
        f"Previous cycles: {history_len}. If zero, start with simplest failing test.\n"
        "Return ONLY the test function code (no imports unless needed)."
    )


def implementer_prompt(state: Dict[str, Any]) -> str:
    last_test = state.get("full_test_suite", "")
    return (
        "You are an implementation agent. Provide minimal code to make the latest failing test pass.\n"
        "Return ONLY python code snippet (no explanations). If impossible yet, return a placeholder comment.\n"
        f"Latest test snippet:\n{last_test}\n"
    )


def refactorer_prompt(state: Dict[str, Any]) -> str:
    current_code = state.get("final_code", "")
    return (
        "You are a refactoring assistant. Suggest an improved version of the code without changing behavior.\n"
        "Keep it small; return ONLY code. If no improvements, echo original.\n"
        f"Current code:\n{current_code}\n"
    )


def supervisor_prompt(state: Dict[str, Any]) -> str:
    return "You are supervising the TDD cycle. Provide a short status string summarizing progress: one of 'continue', 'done', or 'adjust'."
