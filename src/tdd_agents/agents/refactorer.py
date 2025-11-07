"""Refactorer agent stub."""

from __future__ import annotations
from typing import Any, Dict
from .base import Agent


class RefactorerAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        base_code = state.get("final_code", "")
        if self.llm:
            from tdd_agents.prompts import refactorer_prompt

            prompt = refactorer_prompt(state)
            generated = self.llm.generate(prompt)
            from tdd_agents.sanitize import sanitize_snippet
            refactored = sanitize_snippet(generated) or base_code
            notes = "LLM suggested refactor or echoed original."
        else:
            refactored = base_code
            notes = "No refactor applied."
        return {
            "refactored_code": refactored,
            "refactor_notes": notes,
        }
