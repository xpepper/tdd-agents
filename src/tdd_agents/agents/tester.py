"""Tester agent stub."""

from __future__ import annotations
from typing import Any, Dict
from .base import Agent


class TesterAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # If llm exists, could generate a test skeleton; keep stub deterministic for now
        if self.llm:
            from tdd_agents.prompts import tester_prompt

            prompt = tester_prompt(state)
            generated = self.llm.generate(prompt)
            from tdd_agents.sanitize import sanitize_snippet
            code = sanitize_snippet(generated) or "def test_placeholder(): assert True"
        else:
            code = "def test_placeholder(): assert True"
        return {
            "test_code": code,
            "test_description": "Generated failing test candidate (may be corrected).",
        }
