"""Orchestrator loop stub for multi-agent TDD cycles."""
from __future__ import annotations
from typing import Any
from .state import initial_state, append_cycle, TDDCycle, CycleTesterOutput, CycleImplementerOutput, CycleRefactorerOutput, CycleSupervisorOutput
from .agents.tester import TesterAgent
from .agents.implementer import ImplementerAgent
from .agents.refactorer import RefactorerAgent
from .agents.supervisor import SupervisorAgent


def run_single_cycle(language: str, kata_description: str) -> Any:
    state = initial_state(language, kata_description)
    tester = TesterAgent("tester")
    implementer = ImplementerAgent("implementer")
    refactorer = RefactorerAgent("refactorer")
    supervisor = SupervisorAgent("supervisor")

    tester_out = tester.act(state.to_dict())
    impl_out = implementer.act(state.to_dict())
    refactor_out = refactorer.act(state.to_dict())
    supervisor_out = supervisor.act(state.to_dict())

    cycle = TDDCycle(
        cycle_number=1,
        tester_output=CycleTesterOutput(**tester_out),
        implementer_output=CycleImplementerOutput(**impl_out),
        refactorer_output=CycleRefactorerOutput(**refactor_out),
        supervisor_output=CycleSupervisorOutput(**supervisor_out),
    )
    append_cycle(state, cycle)
    state.final_code = refactor_out.get("refactored_code", "")
    state.full_test_suite = tester_out.get("test_code", "")
    return state.to_dict()
