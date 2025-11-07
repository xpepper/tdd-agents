from tdd_agents.orchestrator import run_n_cycles
import tdd_agents.orchestrator as orchestrator_mod


class RecordingLLM:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:  # pragma: no cover - trivial
        self.prompts.append(prompt)
        return "pass"  # minimal deterministic output


def test_prompts_include_latest_diff_and_heuristic(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "custom")

    recorder = RecordingLLM()

    def fake_build_llm():  # returns our recording client
        return recorder, {"provider": "record", "model": "record", "mode": "offline"}

    monkeypatch.setattr(orchestrator_mod, "build_llm", fake_build_llm)

    # Run two cycles so that second cycle prompts see first diff + heuristic
    result = run_n_cycles("python", "Diff aware kata", max_cycles=2)

    # We expect at least 2 cycles worth of prompts captured: tester, implementer, refactorer, supervisor per cycle
    assert len(recorder.prompts) >= 4, "Not enough prompts captured"

    # Prompts from second cycle should contain unified diff markers from first cycle change
    # We conservatively search all prompts after the first four (cycle 1)
    cycle2_prompts = recorder.prompts[4:]
    assert cycle2_prompts, "No second cycle prompts captured"
    assert any("--- prev" in p and "+++ current" in p for p in cycle2_prompts), "Unified diff markers not found in second cycle prompts"

    # Heuristic reason from first cycle should be included (expected 'initial')
    assert any("heuristic_reason: initial" in p for p in cycle2_prompts), "Heuristic reason not injected into prompts"

    # System log should have at least one heuristic_reason entry
    log_messages = [e["message"] for e in result["system_log"]]
    assert any("Supervisor heuristic_reason=" in m for m in log_messages), "Supervisor heuristic log entry missing"
