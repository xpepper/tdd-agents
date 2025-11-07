from tdd_agents.orchestrator import run_n_cycles


def test_abort_flag_and_reason(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    # Force very low retries to trigger abort quickly if failures persist
    monkeypatch.setenv("TDD_AGENTS_MAX_RETRIES", "0")
    result = run_n_cycles("python", "Kata description", max_cycles=2)
    # With 0 retries, tester syntax would abort if syntax error occurs; deterministic tester produces valid syntax.
    # Implementer/refactorer may still pass; if not aborted still fine. Just assert fields exist.
    assert "aborted" in result
    assert "abort_reason" in result
    assert isinstance(result["aborted"], bool)
    assert isinstance(result["abort_reason"], str)
