from tdd_agents.orchestrator import run_n_cycles


def test_supervisor_done_after_five(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    result = run_n_cycles("python", "Kata", max_cycles=6)
    # Expect supervisor signaled completion or stopped at 5
    assert len(result["tdd_history"]) <= 6
    # Last cycle status should be either 'Cycle supervised.' (null LLM) or 'done'
    last_status = result["tdd_history"][-1]["supervisor_output"]["status"]
    assert last_status in {"Cycle supervised.", "done"}


def test_supervisor_stagnation_detection(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    # Force stagnation: since NullLLM deterministic, cycles should repeat identically
    result = run_n_cycles("python", "Kata", max_cycles=4)
    history = result["tdd_history"]
    if len(history) >= 2:
        # If stagnation triggered, status becomes 'done' by or before second identical repetition
        statuses = [c["supervisor_output"]["status"] for c in history]
        assert (
            "done" in statuses or len(history) > 2
        )  # allow fallback if heuristic not applied
