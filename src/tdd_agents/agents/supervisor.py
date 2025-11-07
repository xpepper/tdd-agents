"""Supervisor agent stub."""

from __future__ import annotations
from typing import Any, Dict
from .base import Agent


class SupervisorAgent(Agent):
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if self.llm:
            from tdd_agents.prompts import supervisor_prompt

            prompt = supervisor_prompt(state)
            generated = self.llm.generate(prompt).strip().lower()
            status = (
                generated if generated in {"continue", "done", "adjust"} else "continue"
            )
        else:
            status = "Cycle supervised."
        return {
            "status": status,
            "issues_identified": [],
            "suggested_actions": [],
        }
