from tdd_agents import prompts


def test_tester_prompt_includes_truncated_marker_when_large_diff():
    # Construct large diff
    big_diff_lines = [f"line {i}" for i in range(300)]
    state = {
        "kata_description": "Do something",
        "tdd_history": [
            {
                "supervisor_output": {"heuristic_reason": "initial"},
                "tester_output": {},
                "implementer_output": {},
                "refactorer_output": {},
            }
        ],
        "code_diffs": ["\n".join(big_diff_lines)],
    }
    prompt = prompts.tester_prompt(state)
    assert "[truncated" in prompt, "Expected truncation marker in prompt for large diff"
