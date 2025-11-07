"""Command-line interface for tdd-agents.

Run one or more TDD cycles with custom kata text and optional OpenAI-compatible
provider parameters.

Examples:
    tdd-agents run --language python --kata "Implement fib(n)" --cycles 3 \
        --provider deepseek --model deepseek-chat \
        --base-url https://api.deepseek.com --api-key $DEEPSEEK_KEY

    tdd-agents run --language python --kata-file kata.txt --cycles 2

Flags override environment variables. API key mapped to LLM_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict
from .orchestrator import run_n_cycles, run_single_cycle
from .state import now_iso


def _read_kata(args: argparse.Namespace) -> str:
    if args.kata:
        return str(args.kata)
    if args.kata_file:
        with open(args.kata_file, "r", encoding="utf-8") as f:
            return str(f.read().strip())
    raise SystemExit("Provide --kata or --kata-file")


def _apply_env_overrides(args: argparse.Namespace) -> None:
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.model:
        os.environ["LLM_MODEL"] = args.model
    if args.base_url:
        os.environ["OPENAI_BASE_URL"] = args.base_url
    if args.api_key:
        os.environ["LLM_API_KEY"] = args.api_key


def cmd_run(
    args: argparse.Namespace,
) -> Dict[str, Any]:  # pure function aside from env mutation
    _apply_env_overrides(args)
    kata_text = _read_kata(args)

    # Optional streaming + persistence callback assembly
    out_dir = getattr(args, "out_dir", None)
    stream = getattr(args, "stream", False)
    write_each = getattr(args, "write_each_cycle", False)

    run_tests_each = getattr(args, "run_tests_each_cycle", False)
    git_commit = getattr(args, "git_commit", False)
    git_prefix = getattr(args, "git_prefix", "cycle")

    def on_cycle(state_dict: Dict[str, Any], cycle_number: int) -> None:
        # Persistence
        if out_dir:
            from .persist import write_current, write_snapshot

            write_current(state_dict, out_dir)
            if write_each:
                write_snapshot(state_dict, out_dir, cycle_number)
        # Basic streaming line
        if stream:
            status = (
                state_dict.get("tdd_history", [])[-1]["supervisor_output"].get(
                    "status", ""
                )
                if state_dict.get("tdd_history")
                else ""
            )
            reason = (
                state_dict.get("tdd_history", [])[-1]["supervisor_output"].get(
                    "heuristic_reason", ""
                )
                if state_dict.get("tdd_history")
                else ""
            )
            diff_count = len(state_dict.get("code_diffs", []))
            print(
                f"[cycle {cycle_number}] status={status} heuristic={reason} diffs={diff_count}",
                flush=True,
            )
        # Optional test execution (isolated to persisted artifacts)
        if run_tests_each and out_dir:
            try:
                import subprocess
                import sys
                import os as _os

                tests_file = _os.path.join(out_dir, "tests", "generated_tests.py")
                code_file = _os.path.join(out_dir, "code", "main.py")
                if _os.path.isfile(tests_file) and _os.path.isfile(code_file):
                    # Create a temp package directory for running pytest without interfering with project tests
                    # Strategy: run pytest on a temp dir assembling these two files.
                    import tempfile
                    import shutil

                    tmp_dir = tempfile.mkdtemp(prefix="tdd_agents_cycle_")
                    try:
                        shutil.copy(code_file, _os.path.join(tmp_dir, "main.py"))
                        shutil.copy(
                            tests_file, _os.path.join(tmp_dir, "test_generated.py")
                        )
                        result = subprocess.run(
                            [sys.executable, "-m", "pytest", "-q"],
                            cwd=tmp_dir,
                            capture_output=True,
                            text=True,
                            timeout=15,
                        )
                        passed = result.returncode == 0
                        summary_msg = (
                            f"Generated tests {'passed' if passed else 'FAILED'}"
                            + (
                                f" stdout={result.stdout.strip().splitlines()[-1] if result.stdout.strip().splitlines() else ''}"
                                if result.stdout
                                else ""
                            )
                        )
                        state_dict.setdefault("system_log", []).append(
                            {
                                "timestamp": state_dict.get("last_updated", ""),
                                "message": summary_msg,
                            }
                        )
                        if stream:
                            print(
                                f"[cycle {cycle_number}] generated_tests={'pass' if passed else 'fail'}",
                                flush=True,
                            )
                    finally:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception as e:  # pragma: no cover - resilience
                if stream:
                    print(f"[cycle {cycle_number}] test run error: {e}", flush=True)
        # Optional git commit (requires git repo)
        if git_commit and out_dir:
            try:
                import subprocess
                import shlex

                # Stage only out_dir
                subprocess.run(shlex.split(f"git add {out_dir}"), check=False)
                msg = (
                    f"{git_prefix}: cycle {cycle_number} status={state_dict.get('tdd_history', [])[-1]['supervisor_output'].get('status', '')} heuristic={state_dict.get('tdd_history', [])[-1]['supervisor_output'].get('heuristic_reason', '')}"
                    if state_dict.get("tdd_history")
                    else f"{git_prefix}: cycle {cycle_number}"
                )
                subprocess.run(["git", "commit", "-m", msg], check=False)
            except Exception:
                # Silent failure allowed; repo not initialized or pre-commit failing.
                pass

    if args.cycles and args.cycles > 1:
        return dict(
            run_n_cycles(
                args.language, kata_text, max_cycles=args.cycles, on_cycle=on_cycle
            )
        )
    return dict(run_single_cycle(args.language, kata_text))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tdd-agents", description="Multi-agent TDD prototype runner"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run one or more TDD cycles")
    run_p.add_argument("--language", required=True, help="Programming language")
    run_p.add_argument("--kata", help="Kata description text")
    run_p.add_argument(
        "--kata-file", dest="kata_file", help="Path to kata description file"
    )
    run_p.add_argument(
        "--cycles", type=int, default=1, help="Number of cycles (default 1)"
    )
    run_p.add_argument("--provider", help="LLM provider id (e.g. deepseek, perplexity)")
    run_p.add_argument("--model", help="Model name for provider")
    run_p.add_argument(
        "--stream", action="store_true", help="Stream per-cycle progress lines"
    )
    run_p.add_argument(
        "--out-dir", dest="out_dir", help="Directory to persist artifacts"
    )
    run_p.add_argument(
        "--write-each-cycle",
        dest="write_each_cycle",
        action="store_true",
        help="Write snapshot per cycle under out-dir",
    )
    run_p.add_argument(
        "--run-tests-each-cycle",
        dest="run_tests_each_cycle",
        action="store_true",
        help="Execute generated tests after each cycle",
    )
    run_p.add_argument(
        "--git-commit",
        dest="git_commit",
        action="store_true",
        help="Git commit artifact dir each cycle (requires repo)",
    )
    run_p.add_argument(
        "--git-prefix",
        dest="git_prefix",
        default="feat",
        help="Commit message Conventional Commit prefix (default feat)",
    )
    run_p.add_argument(
        "--base-url",
        dest="base_url",
        help="Custom base URL for OpenAI-compatible endpoint",
    )
    run_p.add_argument(
        "--api-key", dest="api_key", help="API key (mapped to LLM_API_KEY)"
    )
    run_p.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    # mypy: callable attached via set_defaults; ignore attribute check safely
    result = cmd_run(args) if args.command == "run" else {}
    print(json.dumps(result, indent=2))
    print(
        f"[tdd-agents] Completed at {now_iso()} with {len(result.get('tdd_history', []))} cycles",
        flush=True,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
