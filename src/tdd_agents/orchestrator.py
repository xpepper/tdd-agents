"""Orchestrator loop for multi-agent TDD cycles.

Provides single-cycle and multi-cycle entry points. Multi-cycle stops when
supervisor returns status 'done' or when max_cycles reached.
"""

from __future__ import annotations
from typing import Any, Dict, Tuple
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
from .state import now_iso
from .llm import build_llm


def _run_cycle(
    state: Any,
    cycle_number: int,
    tester: TesterAgent,
    implementer: ImplementerAgent,
    refactorer: RefactorerAgent,
    supervisor: SupervisorAgent,
) -> Tuple[str, Dict[str, Any]]:
    """Execute a single cycle given existing agents and state.

    Returns (supervisor_status, last_outputs_dict_for_code_update).
    """
    tester_raw = tester.act(state.to_dict())
    tester_out, tester_msg = validate_tester(tester_raw)
    state.system_log.append({"timestamp": now_iso(), "message": tester_msg})

    implementer_raw = implementer.act(state.to_dict())
    impl_out, impl_msg = validate_implementer(implementer_raw)
    state.system_log.append({"timestamp": now_iso(), "message": impl_msg})

    refactor_raw = refactorer.act(state.to_dict())
    refactor_out, refactor_msg = validate_refactorer(refactor_raw)
    state.system_log.append({"timestamp": now_iso(), "message": refactor_msg})

    supervisor_raw = supervisor.act(state.to_dict())
    supervisor_out, supervisor_msg = validate_supervisor(supervisor_raw)
    state.system_log.append({"timestamp": now_iso(), "message": supervisor_msg})

    cycle = TDDCycle(
        cycle_number=cycle_number,
        tester_output=CycleTesterOutput(**tester_out),
        implementer_output=CycleImplementerOutput(**impl_out),
        refactorer_output=CycleRefactorerOutput(**refactor_out),
        supervisor_output=CycleSupervisorOutput(status=supervisor_out.get("status", "")),
    )
    append_cycle(state, cycle)

    # Update aggregate code/test suite after each cycle
    state.final_code = refactor_out.get("refactored_code", state.final_code)
    state.full_test_suite = tester_out.get("test_code", state.full_test_suite)

    return supervisor_out.get("status", ""), {
        "tester": tester_out,
        "implementer": impl_out,
        "refactorer": refactor_out,
        "supervisor": supervisor_out,
    }


def run_single_cycle(language: str, kata_description: str) -> Any:
    state = initial_state(language, kata_description)
    llm_client, llm_info = build_llm()
    state.system_log.append(
        {"timestamp": now_iso(), "message": f"LLM provider selected: {llm_info}"}
    )
    tester = TesterAgent("tester", llm=llm_client)
    implementer = ImplementerAgent("implementer", llm=llm_client)
    refactorer = RefactorerAgent("refactorer", llm=llm_client)
    supervisor = SupervisorAgent("supervisor", llm=llm_client)

    _run_cycle(state, 1, tester, implementer, refactorer, supervisor)
    return state.to_dict()


def run_n_cycles(
    language: str,
    kata_description: str,
    max_cycles: int = 3,
) -> Any:
    """Run up to `max_cycles` TDD cycles, stopping early if supervisor says 'done'."""
    state = initial_state(language, kata_description)
    llm_client, llm_info = build_llm()
    state.system_log.append(
        {"timestamp": now_iso(), "message": f"LLM provider selected: {llm_info}"}
    )
    tester = TesterAgent("tester", llm=llm_client)
    implementer = ImplementerAgent("implementer", llm=llm_client)
    refactorer = RefactorerAgent("refactorer", llm=llm_client)
    supervisor = SupervisorAgent("supervisor", llm=llm_client)

    for cycle_number in range(1, max_cycles + 1):
        status, _outputs = _run_cycle(
            state, cycle_number, tester, implementer, refactorer, supervisor
        )
        if status == "done":  # early stop
            state.system_log.append(
                {"timestamp": now_iso(), "message": "Supervisor signaled completion."}
            )
            break
    return state.to_dict()
