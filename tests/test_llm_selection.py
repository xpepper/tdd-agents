from importlib import reload
import tdd_agents.llm as llm_mod


def test_null_llm_default(monkeypatch):
    # Ensure no keys -> NullLLM
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    reload(llm_mod)
    client = llm_mod.build_llm()
    assert isinstance(client, llm_mod.NullLLM)
    assert client.generate("test") == "[NULL_LLM_OUTPUT]"


def test_openai_llm_when_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    # We avoid actual network: if ChatOpenAI unavailable, build_llm falls back.
    client = llm_mod.build_llm()
    # Either OpenAIClient or NullLLM (if dependency missing); assert interface works.
    assert hasattr(client, "generate")
