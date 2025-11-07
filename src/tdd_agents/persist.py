"""Filesystem persistence helpers for TDD agent state.

Side effects: writes files under an output directory. Keep inputs minimal.
Directory layout (root = out_dir):
- code/ : latest code artifact (main.py)
- tests/ : accumulated test suite (generated_tests.py)
- snapshots/cycle_<N>/ : per-cycle snapshot files
    - code.py
    - tests.py
    - diff.txt (only if diff exists for that cycle)
    - meta.json (cycle metadata)

All write functions create parent directories as needed.
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_current(state: Dict[str, Any], out_dir: str) -> None:
    """Persist latest aggregate code and test suite.

    Writes `code/main.py` and `tests/generated_tests.py` under `out_dir`.
    """
    _ensure_dir(out_dir)
    code_dir = os.path.join(out_dir, "code")
    tests_dir = os.path.join(out_dir, "tests")
    _ensure_dir(code_dir)
    _ensure_dir(tests_dir)
    code_path = os.path.join(code_dir, "main.py")
    tests_path = os.path.join(tests_dir, "generated_tests.py")
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(state.get("final_code", ""))
    with open(tests_path, "w", encoding="utf-8") as f:
        f.write(state.get("full_test_suite", ""))


def write_snapshot(state: Dict[str, Any], out_dir: str, cycle_number: int) -> None:
    """Persist a per-cycle snapshot of state artifacts.

    Creates `snapshots/cycle_<N>/` directory with code/tests/diff/meta.
    """
    snap_root = os.path.join(out_dir, "snapshots", f"cycle_{cycle_number}")
    _ensure_dir(snap_root)
    code_path = os.path.join(snap_root, "code.py")
    tests_path = os.path.join(snap_root, "tests.py")
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(state.get("final_code", ""))
    with open(tests_path, "w", encoding="utf-8") as f:
        f.write(state.get("full_test_suite", ""))
    # Diff: latest entry if exists and corresponds to this cycle (heuristic: last diff index == cycle_count - 1)
    diffs = state.get("code_diffs", []) or []
    history = state.get("tdd_history", []) or []
    if diffs and len(diffs) == len(
        [
            c
            for c in history
            if c.get("implementer_output") or c.get("refactorer_output")
        ]
    ):
        # Write latest diff as diff.txt (not strict cycle mapping; best-effort)
        diff_path = os.path.join(snap_root, "diff.txt")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diffs[-1])
    meta = {
        "cycle_number": cycle_number,
        "history_length": len(history),
        "has_diff": bool(diffs),
        "heuristic_reason": (
            history[-1].get("supervisor_output", {}).get("heuristic_reason", "")
            if history
            else ""
        ),
        "status": (
            history[-1].get("supervisor_output", {}).get("status", "")
            if history
            else ""
        ),
    }
    meta_path = os.path.join(snap_root, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
