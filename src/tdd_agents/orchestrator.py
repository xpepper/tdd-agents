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
    from .llm import build_llm
    from .state import now_iso

    llm_client, llm_info = build_llm()
    state.system_log.append(
        {"timestamp": now_iso(), "message": f"LLM provider selected: {llm_info}"}
    )
    tester = TesterAgent("tester", llm=llm_client)
    implementer = ImplementerAgent("implementer", llm=llm_client)
    refactorer = RefactorerAgent("refactorer", llm=llm_client)
    supervisor = SupervisorAgent("supervisor", llm=llm_client)

    tester_raw = tester.act(state.to_dict())
    tester_out, tester_msg = validate_tester(tester_raw)
    from .state import now_iso

    state.system_log.append({"timestamp": now_iso(), "message": tester_msg})

    implementer_raw = implementer.act(state.to_dict())
    impl_out, impl_msg = validate_implementer(implementer_raw)
    from .state import now_iso

    state.system_log.append({"timestamp": now_iso(), "message": impl_msg})

    refactor_raw = refactorer.act(state.to_dict())
    refactor_out, refactor_msg = validate_refactorer(refactor_raw)
    from .state import now_iso

    state.system_log.append({"timestamp": now_iso(), "message": refactor_msg})

    supervisor_raw = supervisor.act(state.to_dict())
    supervisor_out, supervisor_msg = validate_supervisor(supervisor_raw)
    from .state import now_iso

    state.system_log.append({"timestamp": now_iso(), "message": supervisor_msg})

    cycle = TDDCycle(
        cycle_number=1,
        tester_output=CycleTesterOutput(**tester_out),
        implementer_output=CycleImplementerOutput(**impl_out),
        refactorer_output=CycleRefactorerOutput(**refactor_out),
        supervisor_output=CycleSupervisorOutput(
            status=supervisor_out.get("status", "")
        ),
    )
    append_cycle(state, cycle)
    state.final_code = refactor_out.get("refactored_code", "")
    state.full_test_suite = tester_out.get("test_code", "")
    return state.to_dict()
