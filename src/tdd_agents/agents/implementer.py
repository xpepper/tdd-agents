"""Implementer agent stub."""

from __future__ import annotations
from typing import Any, Dict
from .base import Agent


class ImplementerAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        test_suite = str(state.get("full_test_suite", ""))
        from tdd_agents.naming import extract_called_functions

        referenced = extract_called_functions(test_suite)
        stubs = []
        for fn in sorted(referenced):
            stubs.append(
                f"def {fn}(*args, **kwargs):\n    raise NotImplementedError('{fn} stub')\n"
            )
        baseline = "\n".join(stubs) if stubs else "# implementation stub\n"
        updated = baseline
        notes = "seed stubs for referenced functions" if stubs else "no functions referenced"
        if self.llm:
            from tdd_agents.prompts import implementer_prompt
            from tdd_agents.sanitize import sanitize_snippet

            prompt = implementer_prompt(state) + "\nCurrent stubs provided:\n" + baseline
            generated = self.llm.generate(prompt)
            # If NullLLM sentinel output, keep baseline
            if generated.strip() != "[NULL_LLM_OUTPUT]":
                candidate = sanitize_snippet(generated)
                if candidate.strip():
                    updated = candidate
                    notes = "LLM augmented implementation"
        return {
            "updated_code": updated,
            "implementation_notes": notes,
        }
