from tdd_agents.orchestrator import run_single_cycle


def test_cycle_outputs_are_sanitized(monkeypatch):
    monkeypatch.setenv("PYTEST_RUNNING", "1")
    monkeypatch.setenv("LLM_PROVIDER", "none")
    state = run_single_cycle("python", "Simple kata: add two numbers")
    assert "```" not in state["final_code"], "final_code should not contain markdown fences"
    assert "```" not in state["full_test_suite"], "full_test_suite should not contain markdown fences"
