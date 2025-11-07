"""Base agent interface definitions."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class Agent(ABC):
    """Abstract base for all agents."""

    name: str

    def __init__(self, name: str, llm: Any | None = None):
        self.name = name
        self.llm = llm  # injected dependency (can be NullLLM)

    @abstractmethod
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:  # minimal for scaffolding
        """Perform agent action given partial state; return structured output dict."""
        raise NotImplementedError
