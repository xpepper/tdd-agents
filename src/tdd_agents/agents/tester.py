"""Tester agent with deterministic seeding of initial failing test.
"""
from __future__ import annotations
from typing import Any, Dict
from .base import Agent
from tdd_agents.naming import choose_target_function


class TesterAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        kata = str(state.get("kata_description", ""))
        target_fn = choose_target_function(kata)
        # simplest failing test referencing target function; expectation intentionally incorrect
        test_code = (
            f"def test_{target_fn}_initial():\n"
            f"    # initial failing seed referencing {target_fn}\n"
            f"    assert {target_fn}([]) == ['EXPECTED'], 'seed failure'\n"
        )
        if self.llm:
            # Allow LLM to propose replacement but ensure it still references target function
            from tdd_agents.prompts import tester_prompt
            from tdd_agents.sanitize import sanitize_snippet

            prompt = tester_prompt(state) + f"\nTarget function to reference: {target_fn}\n"
            generated = self.llm.generate(prompt)
            candidate = sanitize_snippet(generated)
            if target_fn in candidate and candidate.startswith("def test_"):
                test_code = candidate.strip() + ("\n" if not candidate.endswith("\n") else "")
        return {
            "test_code": test_code,
            "test_description": f"Seed failing test for {target_fn}",
        }
