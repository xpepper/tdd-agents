"""State management and JSON assembly for multi-agent TDD cycles.
Pure functions only (except timestamp generation).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, List, Dict

ISOFormat = str


def now_iso() -> ISOFormat:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CycleTesterOutput:
    test_code: str = ""
    test_description: str = ""


@dataclass
class CycleImplementerOutput:
    updated_code: str = ""
    implementation_notes: str = ""


@dataclass
class CycleRefactorerOutput:
    refactored_code: str = ""
    refactor_notes: str = ""


@dataclass
class CycleSupervisorOutput:
    status: str = ""
    heuristic_reason: str = ""
    issues_identified: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)


@dataclass
class TDDCycle:
    cycle_number: int
    tester_output: CycleTesterOutput = field(default_factory=CycleTesterOutput)
    implementer_output: CycleImplementerOutput = field(
        default_factory=CycleImplementerOutput
    )
    refactorer_output: CycleRefactorerOutput = field(
        default_factory=CycleRefactorerOutput
    )
    supervisor_output: CycleSupervisorOutput = field(
        default_factory=CycleSupervisorOutput
    )


@dataclass
class SystemState:
    language: str
    kata_description: str
    tdd_history: List[TDDCycle] = field(default_factory=list)
    final_code: str = ""
    full_test_suite: str = ""
    code_diffs: List[str] = field(default_factory=list)
    system_log: List[Dict[str, Any]] = field(default_factory=list)
    aborted: bool = False
    abort_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def initial_state(language: str, kata_description: str) -> SystemState:
    state = SystemState(language=language, kata_description=kata_description)
    state.system_log.append({"timestamp": now_iso(), "message": "State initialized."})
    return state


def append_cycle(state: SystemState, cycle: TDDCycle) -> SystemState:
    state.tdd_history.append(cycle)
    state.system_log.append(
        {"timestamp": now_iso(), "message": f"Cycle {cycle.cycle_number} appended."}
    )
    return state
