# tdd-agents

Multi-agent Test-Driven Development (TDD) prototype. Orchestrates iterative cycles of:
1. TesterAgent – proposes (failing) pytest test
2. ImplementerAgent – minimal implementation to satisfy newest test
3. RefactorerAgent – small behavior-preserving improvement
4. SupervisorAgent – decides to continue / adjust / stop (with heuristic_reason)

The system accumulates test snippets, tracks code revisions, and stores per‑cycle unified diffs.

## Features
- Single or multi-cycle orchestration (`run_single_cycle`, `run_n_cycles`)
- Supervisor heuristic early stop (max cycles / stagnation) with `heuristic_reason` field
- Accumulated test suite (unique snippets appended)
- Per-cycle code diffs (`code_diffs`) via unified diff
- Pluggable LLM provider abstraction with offline NullLLM fallback
- CLI for running cycles from kata text or file
- Validation layer normalizing agent outputs

## Installation & Setup
Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Running
### CLI
Invoke via module or installed script.

Single cycle:
```bash
python -m tdd_agents.cli run --language python --kata "Return zero always"
```

Multi-cycle (up to N cycles, early stop possible):
```bash
python -m tdd_agents.cli run --language python --kata "Sum two numbers" --cycles 5
```

From file:
```bash
python -m tdd_agents.cli run --language python --kata-file path/to/kata.txt --cycles 3
```

Output: First line JSON describing final state; second line a summary message. Use `jq` for inspection:
```bash
python -m tdd_agents.cli run --language python --kata "X" | head -n1 | jq .tdd_history[-1].supervisor_output
```

### Programmatic
```python
from tdd_agents.orchestrator import run_single_cycle, run_n_cycles
state1 = run_single_cycle("python", "Simple kata")
stateN = run_n_cycles("python", "More complex kata", max_cycles=4)
```

## Environment Variables
Configure LLM provider and endpoint; all optional.

- `LLM_PROVIDER`: one of `openai`, `anthropic`, or `none` (fallback to NullLLM if missing keys)
- `LLM_API_KEY`: preferred generic key variable (mapped from CLI `--api-key`)
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`: alternative provider-specific keys
- `LLM_MODEL`: model name (default `gpt-4o-mini` if not overridden)
- `OPENAI_BASE_URL`: custom base URL for OpenAI-compatible endpoints

CLI flags `--provider`, `--model`, `--base-url`, `--api-key` override these vars for the process.

## State Structure (Key Fields)
Top-level JSON keys after run:
- `language`: language string used (e.g. `python`)
- `kata_description`: original kata text
- `tdd_history`: list of cycles (see below)
- `final_code`: latest refactored (or implemented) code
- `full_test_suite`: accumulated test snippets (blank-line separated)
- `code_diffs`: list of unified diff strings (one per cycle with a change)
- `system_log`: timestamped messages (validation, cycles appended, etc.)

Each `tdd_history` item (`TDDCycle`):
- `cycle_number`: sequential starting at 1
- `tester_output.test_code`
- `implementer_output.updated_code`
- `refactorer_output.refactored_code`
- `supervisor_output.status`: `continue`, `done`, or `adjust`
- `supervisor_output.heuristic_reason`: `initial`, `max_cycles`, or `stagnation` (empty if not set)

## Supervisor Heuristic
- `max_cycles`: if cycles ≥ 5 => status `done`
- `stagnation`: if last two cycles tester/implementer/refactorer outputs identical => `done`
- `initial`: first cycle default reason
LLM suggestion (`continue`, `adjust`, `done`) only considered when heuristic not already `done`.

## Diff Tracking
Each cycle’s code change produces a unified diff (from previous `final_code` to new) stored in `code_diffs`. Empty diffs are skipped.

## Development Workflow (TDD)
1. Write/adjust a failing test (agents do this automatically; you can add manual tests under `tests/`)
2. Minimal implementation
3. Refactor when green
4. Supervisor may stop early

Before committing (see `AGENTS.md`):
```bash
pytest -q
ruff check .
ruff format .
mypy src/tdd_agents
```

## Running Tests & Quality Tools
```bash
pytest -q                # all tests
pytest tests/test_multi_cycle.py::test_run_n_cycles_structure -q  # single test
ruff check .             # lint
ruff format .            # auto-format
mypy src/tdd_agents      # type checking
```

## Extending
- Add new agents under `src/tdd_agents/agents/` subclassing `Agent`.
- Keep functions small (< ~30 lines) and pure unless documented side effects.
- For new side-effect functions, include docstring describing purpose + minimal inputs.
- Integrate new context into `prompts.py` via pure formatting helpers.

## Null / Offline Mode
Set `LLM_PROVIDER=none` (or omit keys) to run deterministic stub behavior (NullLLM returns constant string). Useful for CI and reproducible tests.

## Example End-to-End
```bash
export LLM_PROVIDER=none
python -m tdd_agents.cli run --language python --kata "Implement Fibonacci" --cycles 4 | jq '.code_diffs'
```

## Caveats / Roadmap
- Prompts currently minimal; future work may inject diffs and accumulation context directly.
- Logging of supervisor heuristic_reason per cycle may be expanded.
- Refactorer improvements intentionally conservative to keep diffs readable.

## License
MIT
