from tdd_agents.state import initial_state, append_cycle, TDDCycle


def test_initial_state_has_required_keys():
    s = initial_state("python", "Sample kata")
    d = s.to_dict()
    assert "language" in d and d["language"] == "python"
    assert "kata_description" in d
    assert isinstance(d.get("tdd_history"), list)
    assert isinstance(d.get("system_log"), list)


def test_append_cycle_adds_cycle():
    s = initial_state("python", "Sample kata")
    cycle = TDDCycle(cycle_number=1)
    append_cycle(s, cycle)
    assert len(s.tdd_history) == 1
    assert s.tdd_history[0].cycle_number == 1
