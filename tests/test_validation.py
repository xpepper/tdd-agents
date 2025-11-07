from tdd_agents.orchestrator import run_single_cycle


def test_validation_log_entries_present():
    result = run_single_cycle("python", "Kata")
    log_messages = [entry["message"] for entry in result["system_log"]]
    assert any("Tester output" in m for m in log_messages)
    assert any("Implementer output" in m for m in log_messages)
    assert any("Refactorer" in m for m in log_messages)
    assert any("Supervisor" in m for m in log_messages)
