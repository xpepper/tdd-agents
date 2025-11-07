import json
import subprocess
import sys


def test_cli_run_single_cycle(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "none")
    kata_text = "Return zero always"
    # Invoke module directly to avoid needing console script install
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tdd_agents.cli",
            "run",
            "--language",
            "python",
            "--kata",
            kata_text,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    # First line should be JSON output
    output_lines = proc.stdout.strip().splitlines()
    assert output_lines, "No output produced"
    data = json.loads(
        "\n".join(output_lines[:-1]) if len(output_lines) > 1 else output_lines[0]
    )
    assert data["language"] == "python"
    assert data["kata_description"] == kata_text
    assert len(data["tdd_history"]) == 1
