"""Orchestrator loop stub for multi-agent TDD cycles with validation hooks."""

from __future__ import annotations
from typing import Any
from .state import (
    initial_state,
    append_cycle,
    TDDCycle,
    CycleTesterOutput,
    CycleImplementerOutput,
    CycleRefactorerOutput,
    CycleSupervisorOutput,
)
from .agents.tester import TesterAgent
from .agents.implementer import ImplementerAgent
from .agents.refactorer import RefactorerAgent
from .agents.supervisor import SupervisorAgent
from .validation import (
    validate_tester,
    validate_implementer,
    validate_refactorer,
    validate_supervisor,
)


def run_single_cycle(language: str, kata_description: str) -> Any:
    state = initial_state(language, kata_description)
    tester = TesterAgent("tester")
    implementer = ImplementerAgent("implementer")
    refactorer = RefactorerAgent("refactorer")
    supervisor = SupervisorAgent("supervisor")

    tester_raw = tester.act(state.to_dict())
    tester_out, tester_msg = validate_tester(tester_raw)
    state.system_log.append({"timestamp": state.system_log[-1]["timestamp"], "message": tester_msg})

    implementer_raw = implementer.act(state.to_dict())
    impl_out, impl_msg = validate_implementer(implementer_raw)
    state.system_log.append({"timestamp": state.system_log[-1]["timestamp"], "message": impl_msg})

    refactor_raw = refactorer.act(state.to_dict())
    refactor_out, refactor_msg = validate_refactorer(refactor_raw)
    state.system_log.append({"timestamp": state.system_log[-1]["timestamp"], "message": refactor_msg})

    supervisor_raw = supervisor.act(state.to_dict())
    supervisor_out, supervisor_msg = validate_supervisor(supervisor_raw)
    state.system_log.append({"timestamp": state.system_log[-1]["timestamp"], "message": supervisor_msg})

    cycle = TDDCycle(
        cycle_number=1,
        tester_output=CycleTesterOutput(**tester_out),
        implementer_output=CycleImplementerOutput(**impl_out),
        refactorer_output=CycleRefactorerOutput(**refactor_out),
        supervisor_output=CycleSupervisorOutput(status=supervisor_out.get("status", "")),
    )
    append_cycle(state, cycle)
    state.final_code = refactor_out.get("refactored_code", "")
    state.full_test_suite = tester_out.get("test_code", "")
    return state.to_dict()
