"""Supervisor agent with stagnation + unrelated code heuristic.

Determines whether to continue, adjust, or declare done based on recent
cycle outputs and simple semantic alignment checks.
Heuristics:
- If >=5 cycles -> done.
- If last two consecutive cycles have identical tester, implementer and
  refactorer outputs -> potential stagnation; return 'done'.
- If current test references function names absent from implementation/refactor
  code -> 'adjust'.
LLM may still override to 'adjust' if it suggests that status; 'done'
from heuristic is final.
"""

from __future__ import annotations
from typing import Any, Dict, List, Set
import re
from .base import Agent


_FUNCTION_IGNORE = {
    # common pytest / builtin names that appear as calls but shouldn't trigger function-missing
    "assert", "range", "len", "print", "int", "str", "float", "list", "dict", "set",
}


def _extract_history(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return state.get("tdd_history", []) or []


def _is_cycle_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    tester_a = a.get("tester_output", {})
    tester_b = b.get("tester_output", {})
    impl_a = a.get("implementer_output", {})
    impl_b = b.get("implementer_output", {})
    ref_a = a.get("refactorer_output", {})
    ref_b = b.get("refactorer_output", {})
    return (
        str(tester_a.get("test_code")) == str(tester_b.get("test_code"))
        and str(impl_a.get("updated_code")) == str(impl_b.get("updated_code"))
        and str(ref_a.get("refactored_code")) == str(ref_b.get("refactored_code"))
    )


def _extract_function_calls(test_code: str) -> Set[str]:
    """Extract candidate function names referenced in the test code.

    Simple regex-based scan for name followed by '(' excluding ignored names and test functions.
    Pure function.
    """
    candidates: Set[str] = set()
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", test_code):
        name = match.group(1)
        if name.startswith("test_") or name in _FUNCTION_IGNORE:
            continue
        candidates.add(name)
    return candidates


def _missing_function_defs(functions: Set[str], impl_code: str, ref_code: str) -> Set[str]:
    """Return function names that are referenced but have no 'def name(' in impl/refactor code."""
    missing: Set[str] = set()
    combined = f"{impl_code}\n{ref_code}" if ref_code else impl_code
    for fn in functions:
        pattern = rf"def\s+{re.escape(fn)}\s*\("
        if not re.search(pattern, combined):
            missing.add(fn)
    return missing


class SupervisorAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        history = _extract_history(state)
        cycles = len(history)
        heuristic_status = "continue"
        heuristic_reason = "initial"
        issues_identified: List[str] = []
        suggested_actions: List[str] = []

        # Existing stagnation / max cycles heuristics
        if cycles >= 5:
            heuristic_status = "done"
            heuristic_reason = "max_cycles"
        elif cycles >= 2 and _is_cycle_equal(history[-1], history[-2]):
            heuristic_status = "done"
            heuristic_reason = "stagnation"

        # Unrelated / missing function heuristic (only if not already done)
        if heuristic_status != "done":
            tester_output = state.get("tester_output", {}) or {}
            implementer_output = state.get("implementer_output", {}) or {}
            refactorer_output = state.get("refactorer_output", {}) or {}
            test_code = str(tester_output.get("test_code", ""))
            impl_code = str(implementer_output.get("updated_code", ""))
            ref_code = str(refactorer_output.get("refactored_code", ""))

            referenced = _extract_function_calls(test_code)
            if referenced:
                missing = _missing_function_defs(referenced, impl_code, ref_code)
                if missing:
                    heuristic_status = "adjust"
                    heuristic_reason = "missing_function"
                    issues_identified.append(
                        "Missing function definitions: " + ", ".join(sorted(missing))
                    )
                    for fn in sorted(missing):
                        suggested_actions.append(f"Define function '{fn}' minimally to satisfy test.")
                elif not impl_code.strip() or impl_code.strip().startswith("#"):
                    # Implementation is still placeholder while test references functions
                    heuristic_status = "adjust"
                    heuristic_reason = "placeholder_implementation"
                    issues_identified.append(
                        "Implementation is placeholder while test references functions."
                    )
                    suggested_actions.append("Add minimal function implementations referenced by test.")

        llm_status = None
        if self.llm and heuristic_status != "done":  # only ask LLM if not already done
            from tdd_agents.prompts import supervisor_prompt

            prompt = supervisor_prompt(state)
            generated = self.llm.generate(prompt).strip().lower()
            if generated in {"continue", "done", "adjust"}:
                llm_status = generated

        # Resolve final status precedence: heuristic 'done' wins; else llm suggestion or heuristic fallback
        final_status = (
            heuristic_status
            if heuristic_status == "done"
            else (llm_status or heuristic_status)
        )

        return {
            "status": final_status,
            "heuristic_reason": heuristic_reason,
            "issues_identified": issues_identified,
            "suggested_actions": suggested_actions,
        }
