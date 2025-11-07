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


def cmd_run(args: argparse.Namespace) -> Dict[str, Any]:  # pure function aside from env mutation
    _apply_env_overrides(args)
    kata_text = _read_kata(args)
    if args.cycles and args.cycles > 1:
        return dict(run_n_cycles(args.language, kata_text, max_cycles=args.cycles))
    return dict(run_single_cycle(args.language, kata_text))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tdd-agents", description="Multi-agent TDD prototype runner")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run one or more TDD cycles")
    run_p.add_argument("--language", required=True, help="Programming language")
    run_p.add_argument("--kata", help="Kata description text")
    run_p.add_argument("--kata-file", dest="kata_file", help="Path to kata description file")
    run_p.add_argument("--cycles", type=int, default=1, help="Number of cycles (default 1)")
    run_p.add_argument("--provider", help="LLM provider id (e.g. deepseek, perplexity)")
    run_p.add_argument("--model", help="Model name for provider")
    run_p.add_argument("--base-url", dest="base_url", help="Custom base URL for OpenAI-compatible endpoint")
    run_p.add_argument("--api-key", dest="api_key", help="API key (mapped to LLM_API_KEY)")
    run_p.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    # mypy: callable attached via set_defaults; ignore attribute check safely
    result = cmd_run(args) if args.command == "run" else {}
    print(json.dumps(result, indent=2))
    print(f"[tdd-agents] Completed at {now_iso()} with {len(result.get('tdd_history', []))} cycles", flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
