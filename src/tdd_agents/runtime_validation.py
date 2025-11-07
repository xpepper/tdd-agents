"""Runtime compilation + test execution helpers.

Side-effect boundary: running pytest in a temporary directory. All functions
here remain small; entry points wrap side effects with minimal inputs.
"""
from __future__ import annotations
import ast
import os
import tempfile
import subprocess
from typing import Tuple

MAX_TEST_LINES = 200  # guardrail


def compile_snippet(snippet: str) -> Tuple[bool, str]:
    try:
        ast.parse(snippet)
        return True, "ok"
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"  # deterministic message


def _write_runtime_files(tmp: str, impl_code: str, test_suite: str) -> None:
    with open(os.path.join(tmp, "impl.py"), "w", encoding="utf-8") as f:
        f.write(impl_code or "# empty impl\n")
    # prepend import line once
    tests_path = os.path.join(tmp, "tests")
    os.makedirs(tests_path, exist_ok=True)
    suite = test_suite.strip()
    if not suite:
        suite = "def test_placeholder():\n    assert True\n"
    content = "from impl import *\n" + suite
    with open(os.path.join(tests_path, "test_generated.py"), "w", encoding="utf-8") as f:
        f.write(content)


def run_tests(impl_code: str, test_suite: str, timeout_sec: int = 5) -> Tuple[bool, str]:
    # safeguard size
    if test_suite.count("\n") > MAX_TEST_LINES:
        return False, "Test suite exceeds MAX_TEST_LINES guardrail"
    with tempfile.TemporaryDirectory() as tmp:
        _write_runtime_files(tmp, impl_code, test_suite)
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = tmp + os.pathsep + env.get("PYTHONPATH", "")
            proc = subprocess.run(
                ["pytest", "-q"], cwd=tmp, capture_output=True, text=True, timeout=timeout_sec, env=env
            )
        except subprocess.TimeoutExpired:
            return False, "Test execution timeout"
        passed = proc.returncode == 0
        details = proc.stdout + proc.stderr
        return passed, details.strip()[:4000]
