from tdd_agents.orchestrator import run_n_cycles


def test_run_n_cycles_structure(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    result = run_n_cycles("python", "Kata description", max_cycles=3)
    # Ensure at least one cycle and at most max_cycles
    assert 1 <= len(result["tdd_history"]) <= 3
    # Cycle numbers sequential
    cycle_numbers = [c["cycle_number"] for c in result["tdd_history"]]
    assert cycle_numbers == list(range(1, len(cycle_numbers) + 1))
    # Final code and test suite updated from last cycle outputs
    assert isinstance(result["final_code"], str)
    assert isinstance(result["full_test_suite"], str)
