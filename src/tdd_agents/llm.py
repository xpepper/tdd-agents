"""LLM provider abstraction layer.

Minimal wrapper to allow swapping any OpenAI API compatible provider
(OpenAI, Anthropic via OpenAI compatibility, local server) while keeping
agents decoupled from LangChain specifics.

Purity: construction reads environment; generation performs remote call.
Side-effect boundaries are documented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional, Any, Dict, Tuple, TYPE_CHECKING
import os

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from langchain_openai import ChatOpenAI
else:  # runtime import guarded
    try:  # Optional import to keep tests passing without network/API keys
        from langchain_openai import ChatOpenAI  # type: ignore
    except Exception:  # pragma: no cover
        ChatOpenAI = None  # type: ignore


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:  # minimal surface
        ...


@dataclass
class NullLLM:
    """Fallback deterministic LLM returning placeholder output.

    Used when no provider configuration is present so tests remain fast
    and offline.
    """

    def generate(self, prompt: str) -> str:  # pragma: no cover - trivial
        return "[NULL_LLM_OUTPUT]"  # concise sentinel


@dataclass
class OpenAIClient:
    """OpenAI-compatible chat client wrapper.

    Confirmation step: requires model name and API key via environment.
    Reads: OPENAI_API_KEY or ANTHROPIC_API_KEY (if provider anthropic),
    plus optional LLM_MODEL, OPENAI_BASE_URL.
    """

    model: str
    temperature: float = 0.0
    api_key: Optional[str] = None
    base_url: Optional[str] = None

    def __post_init__(self) -> None:  # construct underlying ChatOpenAI
        if ChatOpenAI is None:
            raise RuntimeError("langchain_openai not available; install dependency.")
        kwargs = {"model": self.model, "temperature": self.temperature}
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self._client = ChatOpenAI(**kwargs)  # type: ignore[arg-type]

    def generate(self, prompt: str) -> str:
        resp = self._client.invoke(prompt)
        # LangChain's ChatOpenAI returns an AIMessage; extract content
        return getattr(resp, "content", str(resp))


def build_llm() -> Tuple[LLMClient, Dict[str, Any]]:
    """Factory selecting appropriate LLMClient.

    Returns (client, info_dict) where info_dict contains:
    - provider: resolved provider string
    - model: model name (or 'null')
    - base_url: custom base URL if any
    - mode: 'live' or 'offline'
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL")

    if provider == "none":
        return NullLLM(), {
            "provider": "none",
            "model": "null",
            "base_url": None,
            "mode": "offline",
        }

    if api_key:
        try:
            client = OpenAIClient(model=model, api_key=api_key, base_url=base_url)
            return client, {
                "provider": provider or "openai",
                "model": model,
                "base_url": base_url,
                "mode": "live",
            }
        except Exception:
            return NullLLM(), {
                "provider": provider or "openai",
                "model": "null",
                "base_url": base_url,
                "mode": "offline",
            }
    return NullLLM(), {
        "provider": provider or "none",
        "model": "null",
        "base_url": base_url,
        "mode": "offline",
    }
