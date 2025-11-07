from importlib import reload
import tdd_agents.llm as llm_mod


def test_null_llm_default(monkeypatch):
    # Ensure no keys -> NullLLM tuple return
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    reload(llm_mod)
    client, info = llm_mod.build_llm()
    assert isinstance(client, llm_mod.NullLLM)
    assert client.generate("test") == "[NULL_LLM_OUTPUT]"
    assert info["provider"] == "none"
    assert info["mode"] == "offline"
    assert info["model"] == "null"


def test_openai_llm_when_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    client, info = llm_mod.build_llm()
    # Either OpenAIClient or NullLLM (if dependency missing); assert interface works.
    assert hasattr(client, "generate")
    assert info["provider"] == "openai"
    assert "mode" in info and info["mode"] in {"live", "offline"}


def test_anthropic_provider(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic-test")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    client, info = llm_mod.build_llm()
    assert info["provider"] == "anthropic"
    assert hasattr(client, "generate")
    # Model may be null if dependency missing; ensure key exists
    assert "model" in info
    assert info["mode"] in {"live", "offline"}
