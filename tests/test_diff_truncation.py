from tdd_agents.prompts import _truncate_diff


def test_truncate_diff_no_change_when_small():
    diff = "\n".join([f"line {i}" for i in range(10)])
    assert _truncate_diff(diff, max_lines=20) == diff


def test_truncate_diff_truncates_large_diff():
    diff = "\n".join([f"line {i}" for i in range(200)])
    truncated = _truncate_diff(diff, max_lines=50, head=20, tail=5)
    lines = truncated.splitlines()
    assert "...[truncated" in lines[20], "Truncation marker not inserted where expected"
    assert len(lines) == 20 + 1 + 5, "Unexpected truncated diff total lines"
    # Ensure last tail lines preserved
    assert lines[-1] == "line 199"
    assert lines[-5] == "line 195"
    # Ensure omitted count correct
    omitted_part = lines[20]
    omitted_num = int(omitted_part.split()[1])  # word after '[truncated'
    # omitted_num should equal original lines - (head + tail)
    assert omitted_num == 200 - (20 + 5)
