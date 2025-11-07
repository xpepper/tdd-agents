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
            if generated.strip() == "[NULL_LLM_OUTPUT]":
                refactored = base_code
                notes = "No refactor (null LLM)."
            else:
                candidate = sanitize_snippet(generated)
                import re
                existing_fns = re.findall(r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', base_code, flags=re.MULTILINE)
                if existing_fns and not any(f"def {fn}" in candidate for fn in existing_fns):
                    refactored = base_code
                    notes = "Ignored LLM refactor lacking function defs"
                else:
                    refactored = candidate or base_code
                    notes = "LLM suggested refactor or echoed original."
        else:
            refactored = base_code
            notes = "No refactor applied."
        return {
            "refactored_code": refactored,
            "refactor_notes": notes,
        }
