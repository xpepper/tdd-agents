"""Validation and minimal self-correction hooks for agent outputs.
All functions are pure: they take dict-like output and return (output, message).
"""
from __future__ import annotations
from typing import Dict, Tuple


def validate_tester(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    code = output.get("test_code", "")
    # Self-correct: ensure test is initially failing to honor TDD.
    if "assert True" in code:
        output["test_code"] = "def test_placeholder(): assert False, 'Replace with real failing test'"
        msg = "Tester output corrected to a failing placeholder test."
    elif not code.strip():
        output["test_code"] = "def test_empty(): assert False"
        msg = "Tester output generated default failing test."\
            
    else:
        msg = "Tester output validated."
    return output, msg


def validate_implementer(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    code = output.get("updated_code", "")
    if not code.strip():
        output["updated_code"] = "# auto-correct: empty implementation stub\n"
        msg = "Implementer output filled empty stub."
    else:
        msg = "Implementer output validated."
    return output, msg


def validate_refactorer(output: Dict[str, str]) -> Tuple[Dict[str, str], str]:
    notes = output.get("refactor_notes", "")
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
    return output, msg
