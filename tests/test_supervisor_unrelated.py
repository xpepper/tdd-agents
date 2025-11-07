from tdd_agents.agents.supervisor import SupervisorAgent
from tdd_agents.llm import NullLLM


def _run(state):
    agent = SupervisorAgent(name="supervisor", llm=NullLLM())
    return agent.act(state)


def test_supervisor_missing_function_triggers_adjust():
    state = {
        "tester_output": {"test_code": "def test_calls_foo():\n    assert foo(1) == 1\n"},
        "implementer_output": {"updated_code": "# implementation stub\n"},
        "refactorer_output": {"refactored_code": ""},
        "tdd_history": [],
    }
    out = _run(state)
    assert out["status"] == "adjust"
    assert out["heuristic_reason"] == "missing_function"
    assert any("foo" in issue for issue in out["issues_identified"])
    assert any("foo" in act for act in out["suggested_actions"])


def test_supervisor_present_function_allows_continue():
    state = {
        "tester_output": {"test_code": "def test_calls_bar():\n    assert bar(2) == 2\n"},
        "implementer_output": {"updated_code": "def bar(x):\n    return x\n"},
        "refactorer_output": {"refactored_code": ""},
        "tdd_history": [],
    }
    out = _run(state)
    assert out["status"] == "continue"
    assert out["heuristic_reason"] == "initial"
    assert out["issues_identified"] == []


def test_supervisor_cycles_stagnation_overrides_adjust():
    cycle = {
        "tester_output": {"test_code": "def test_calls_baz():\n    assert baz(3) == 3\n"},
        "implementer_output": {"updated_code": "def baz(x):\n    return x\n"},
        "refactorer_output": {"refactored_code": ""},
    }
    state = {
        "tester_output": cycle["tester_output"],
        "implementer_output": cycle["implementer_output"],
        "refactorer_output": cycle["refactorer_output"],
        "tdd_history": [cycle, cycle],  # identical last two cycles -> stagnation
    }
    out = _run(state)
    assert out["status"] == "done"
    assert out["heuristic_reason"] == "stagnation"


def test_supervisor_placeholder_impl_triggers_adjust():
    state = {
        "tester_output": {"test_code": "def test_calls_qux():\n    assert qux() == 0\n"},
        "implementer_output": {"updated_code": "# implementation stub\n"},
        "refactorer_output": {"refactored_code": ""},
        "tdd_history": [],
    }
    out = _run(state)
    assert out["status"] == "adjust"
    assert out["heuristic_reason"] in {"missing_function", "placeholder_implementation"}
