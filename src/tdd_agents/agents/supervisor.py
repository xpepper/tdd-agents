"""Supervisor agent with simple stagnation heuristic.

Determines whether to continue, adjust, or declare done based on recent
cycle outputs. Pure analysis logic precedes optional LLM status suggestion.
Heuristic:
- If >=5 cycles -> done.
- If last two consecutive cycles have identical tester, implementer and
  refactorer outputs -> potential stagnation; return 'done'.
- If only first cycle -> continue.
LLM may still override to 'adjust' if it suggests that status; 'done'
from heuristic is final.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import Agent


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


class SupervisorAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        history = _extract_history(state)
        cycles = len(history)
        heuristic_status = "continue"

        heuristic_reason = "initial"
        if cycles >= 5:
            heuristic_status = "done"
            heuristic_reason = "max_cycles"
        elif cycles >= 2 and _is_cycle_equal(history[-1], history[-2]):
            heuristic_status = "done"
            heuristic_reason = "stagnation"

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
            "issues_identified": [],
            "suggested_actions": [],
        }
