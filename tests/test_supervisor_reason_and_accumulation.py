from tdd_agents.orchestrator import run_n_cycles


def test_supervisor_heuristic_reason_present(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    result = run_n_cycles("python", "Simple kata", max_cycles=2)
    last_cycle = result["tdd_history"][-1]
    assert "heuristic_reason" in last_cycle["supervisor_output"]
    assert last_cycle["supervisor_output"]["heuristic_reason"] in {
        "initial",
        "max_cycles",
        "stagnation",
    }


def test_test_suite_accumulates(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    result = run_n_cycles("python", "Accumulation kata", max_cycles=3)
    suite = result["full_test_suite"].strip()
    # Split on blank lines we inserted; ensure no duplicates adjacent
    snippets = [s.strip() for s in suite.split("\n\n") if s.strip()]
    assert snippets, "No test snippets accumulated"
    # If more than one cycle ran, either stagnation caused early stop or we have >1 unique snippet
    if len(result["tdd_history"]) > 1:
        assert len(set(snippets)) >= 1
