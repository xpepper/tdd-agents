"""Validation and minimal self-correction hooks for agent outputs.
All functions are pure: they take dict-like output and return (output, message).
"""

from __future__ import annotations
from typing import Dict, Tuple
from tdd_agents.sanitize import sanitize_snippet


def validate_tester(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    code = output.get("test_code", "")
    sanitized = sanitize_snippet(code)
    lines = sanitized.splitlines()
    test_blocks: list[list[str]] = []
    current_block: list[str] = []
    for line in lines:
        if line.startswith("def test_"):
            if current_block:
                test_blocks.append(current_block)
                current_block = []
            current_block.append(line)
        else:
            if current_block:
                current_block.append(line)
    if current_block:
        test_blocks.append(current_block)
    if test_blocks:
        first_block = "\n".join(test_blocks[0]).strip()
    else:
        first_block = "def test_generated(): assert False, 'auto-created failing test'"
    if "assert True" in first_block or "assert" not in first_block:
        first_block = "def test_generated(): assert False, 'ensure failing start'"
        msg = "Tester output corrected to single failing test."
    elif sanitized != first_block + "\n":
        msg = "Tester output trimmed to first test function."
    else:
        msg = "Tester output validated."
    output["test_code"] = first_block + "\n"
    return output, msg


def validate_implementer(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    code = output.get("updated_code", "")
    sanitized = sanitize_snippet(code)
    if not sanitized.strip():
        output["updated_code"] = "# auto-correct: empty implementation stub\n"
        msg = "Implementer output filled empty stub."
    else:
        output["updated_code"] = sanitized
        msg = "Implementer output sanitized and validated."
    return output, msg


def validate_refactorer(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    notes = output.get("refactor_notes", "")
    code = output.get("refactored_code", "")
    sanitized = sanitize_snippet(code)
    if sanitized:
        output["refactored_code"] = sanitized
    if not notes.strip():
        output["refactor_notes"] = "No refactor applied."  # ensure clarity
        msg = "Refactorer notes normalized."
    else:
        msg = "Refactorer output validated."
    return output, msg


def validate_supervisor(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    status = output.get("status", "")
    if not status.strip():
        output["status"] = "Cycle supervised."
        msg = "Supervisor status defaulted."
    else:
        msg = "Supervisor output validated."
    # ensure heuristic_reason key exists for schema stability
    output.setdefault("heuristic_reason", "")
    return output, msg
