# AGENTS.md
Purpose: Guidance for agentic contributors building multi-agent TDD prototype.
Build/Setup: run `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`.
Install deps via pyproject; avoid global installs.
Tests: run all `pytest -q`; single test `pytest tests/test_fib.py::test_fib0 -q`.
Re-run last failing: `pytest --lf -q`.
Lint/Format: use `ruff check .` then `ruff format .`; fix incrementally.
Type checking: `mypy src`.
Import order: stdlib, third-party, local; no wildcard imports.
File layout: code in `src/`, tests in `tests/`, agents under `src/agents/`.
Naming: snake_case funcs/vars, PascalCase classes, UPPER_CASE constants.
Functions ≤ ~30 lines; extract helpers early.
Errors: raise explicit exceptions; never swallow; log via centralized logger (planned `src/logging.py`).
TDD cycle: add failing test, minimal code, refactor; commit after green+refactor.
JSON state builder: keep pure (no side effects except parameter-free timestamp generation).
Side effects (IO/network) must be wrapped with confirmation step docstring describing purpose + minimal inputs.
Avoid premature abstractions; prefer clear stubs with TODO comments (no leaving dead code).
External tools limited to allowed LangChain integrations; explain necessity before adding.
No Cursor/Copilot rules exist; if added later, summarize them here.
Keep commits focused; avoid unrelated formatting; include AGENTS.md compliance in PR summary.
