from tdd_agents.orchestrator import run_single_cycle


def test_run_single_cycle_structure():
    result = run_single_cycle("python", "Kata description")
    assert result["language"] == "python"
    assert result["kata_description"] == "Kata description"
    assert isinstance(result["tdd_history"], list) and len(result["tdd_history"]) == 1
    cycle = result["tdd_history"][0]
    assert cycle["cycle_number"] == 1
    assert "tester_output" in cycle
    assert "implementer_output" in cycle
    assert "refactorer_output" in cycle
    assert "supervisor_output" in cycle
