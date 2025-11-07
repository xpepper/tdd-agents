import json
import os
import subprocess
import sys
import tempfile


def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tdd_agents.cli"] + args, capture_output=True, text=True
    )


def test_streaming_and_out_dir(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")
    with tempfile.TemporaryDirectory() as tmp:
        proc = _run_cli(
            [
                "run",
                "--language",
                "python",
                "--kata",
                "Return zero",
                "--cycles",
                "2",
                "--stream",
                "--out-dir",
                os.path.join(tmp, "artifacts"),
                "--write-each-cycle",
            ]
        )
        assert proc.returncode == 0
        # Streaming lines should include cycle markers
        streamed = proc.stdout.splitlines()
        cycle_lines = [line for line in streamed if line.startswith("[cycle ")]
        assert len(cycle_lines) >= 2, (
            f"Expected at least 2 cycle lines, got: {cycle_lines}"
        )
        # First JSON line presence
        # JSON output is one of the lines; locate first line starting with '{'
        # Gather pretty-printed JSON block: starts with '{' and ends with '}' before summary line
        # Separate run without streaming to obtain clean JSON
        proc2 = _run_cli(
            ["run", "--language", "python", "--kata", "Return zero", "--cycles", "1"]
        )
        assert proc2.returncode == 0
        lines2 = proc2.stdout.splitlines()
        json_block = []
        collecting = False
        depth = 0
        for ln in lines2:
            stripped = ln.strip()
            if not collecting and stripped.startswith("{"):
                collecting = True
            if collecting:
                json_block.append(ln)
                depth += stripped.count("{")
                depth -= stripped.count("}")
                if collecting and depth == 0:
                    break
        json_text = "\n".join(json_block)
        data = json.loads(json_text)
        assert "tdd_history" in data
        # Persistence artifacts
        art_root = os.path.join(tmp, "artifacts")
        assert os.path.isfile(os.path.join(art_root, "code", "main.py"))
        assert os.path.isfile(os.path.join(art_root, "tests", "generated_tests.py"))
        # Snapshot directories
        snap1 = os.path.join(art_root, "snapshots", "cycle_1")
        snap2 = os.path.join(art_root, "snapshots", "cycle_2")
        assert os.path.isdir(snap1)
        assert os.path.isdir(snap2)
        assert os.path.isfile(os.path.join(snap1, "meta.json"))
        assert os.path.isfile(os.path.join(snap2, "meta.json"))
