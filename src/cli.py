"""CLI entrypoint for running a single orchestrated cycle.
Side effects limited to printing JSON result.
"""
from __future__ import annotations
import json
import argparse
from .orchestrator import run_single_cycle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single TDD agent cycle.")
    parser.add_argument("kata_file", help="Path to a text file containing kata description.")
    parser.add_argument("--language", default="python", help="Programming language of kata.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with open(args.kata_file, "r", encoding="utf-8") as f:
        kata_description = f.read().strip()
    result = run_single_cycle(args.language, kata_description)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
