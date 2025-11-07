from tdd_agents.agents.tester import TesterAgent
from tdd_agents.agents.implementer import ImplementerAgent
from tdd_agents.llm import NullLLM


def test_tester_seeds_target_function():
    kata = "Mars rover navigates a grid executing commands"
    state = {"kata_description": kata, "tdd_history": []}
    agent = TesterAgent(name="tester", llm=NullLLM())
    out = agent.act(state)
    assert "execute_commands" in out["test_code"], "Should choose execute_commands for mars rover kata"


def test_implementer_creates_stub_for_referenced_function():
    test_code = "def test_execute_commands_initial():\n    assert execute_commands([]) == ['EXPECTED']\n"
    state = {"full_test_suite": test_code}
    agent = ImplementerAgent(name="implementer", llm=NullLLM())
    out = agent.act(state)
    assert "def execute_commands" in out["updated_code"], "Stub/implementation for execute_commands should be created"
    # Should return the expected literal now for simple patterns
    assert "return ['EXPECTED']" in out["updated_code"]
