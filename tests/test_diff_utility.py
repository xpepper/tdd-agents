from tdd_agents.diff import unified_code_diff


def test_unified_code_diff_basic():
    old = "def f():\n    return 1\n"
    new = "def f():\n    return 2\n"
    diff = unified_code_diff(old, new)
    # Expect headers and changed lines markers
    assert diff.startswith("--- prev") and "+++ current" in diff
    assert "-    return 1" in diff
    assert "+    return 2" in diff
