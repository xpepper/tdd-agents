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
    """Execute a single cycle with runtime validation + retries.

    Returns (supervisor_status, last_outputs_dict_for_code_update).
    Rollback semantics:
    - Tester phase: syntax errors trigger single retry; failing assertion kept.
    - Implementer/refactorer phases: require tests to pass; retries up to env limit.
    - On exhaustion set state.aborted and do not append cycle.
    """
    import os
    from tdd_agents.runtime_validation import compile_snippet, run_tests

    max_retries = int(os.getenv("TDD_AGENTS_MAX_RETRIES", "3"))

    pre_cycle_code = state.final_code  # capture code before any changes this cycle
    # Tester phase
    tester_attempts = 0
    while True:
        tester_raw = tester.act(state.to_dict())
        tester_out, tester_msg = validate_tester(tester_raw)
        state.system_log.append({"timestamp": now_iso(), "message": tester_msg})
        ok, comp_msg = compile_snippet(tester_out.get("test_code", ""))
        if ok:
            break
        tester_attempts += 1
        state.system_log.append({"timestamp": now_iso(), "message": f"Tester syntax error; rollback attempt {tester_attempts}: {comp_msg}"})
        if tester_attempts >= max_retries:
            state.aborted = True
            state.abort_reason = f"tester_syntax_retry_exhausted: {comp_msg}"
            return "aborted", {"tester": tester_out}

    # Implementer phase with test run requirement (allow failing due to assertion until implementation stage?)
    impl_attempts = 0
    impl_out: Dict[str, Any] = {}
    while True:
        # Provide tester snippet to implementer for stub inference
        augmented_state = state.to_dict()
        new_test_snippet = tester_out.get("test_code", "")
        combined_for_stubs = augmented_state.get("full_test_suite", "").strip()
        if new_test_snippet and new_test_snippet.strip() not in combined_for_stubs.split("\n\n"):
            combined_for_stubs = (combined_for_stubs + "\n\n" + new_test_snippet).strip() if combined_for_stubs else new_test_snippet
        augmented_state["full_test_suite"] = combined_for_stubs
        implementer_raw = implementer.act(augmented_state)
        impl_out, impl_msg = validate_implementer(implementer_raw)
        state.system_log.append({"timestamp": now_iso(), "message": impl_msg})
        # Run tests combining candidate code with accumulated test suite + current tester snippet
        combined_suite = state.full_test_suite.strip()
        if new_test_snippet and new_test_snippet.strip() not in combined_suite.split("\n\n"):
            combined_suite = (combined_suite + "\n\n" + new_test_snippet).strip() if combined_suite else new_test_snippet
        passed, details = run_tests(impl_out.get("updated_code", ""), combined_suite)
        state.system_log.append({"timestamp": now_iso(), "message": f"Implementer test run passed={passed}."})
        if passed:
            # Accept tester snippet into suite
            state.full_test_suite = combined_suite
            break
        impl_attempts += 1
        state.system_log.append({"timestamp": now_iso(), "message": f"Implementer failing tests attempt {impl_attempts}: {details.splitlines()[:1][0] if details else 'no details'}"})
        if impl_attempts >= max_retries:
            state.aborted = True
            state.abort_reason = "implementer_retry_exhausted"
            return "aborted", {"tester": tester_out, "implementer": impl_out}

    # Persist implementer code as current baseline for refactorer reuse
    state.final_code = impl_out.get("updated_code", state.final_code)

    # Refactorer phase: must keep tests green
    ref_attempts = 0
    refactor_out: Dict[str, Any] = {}
    while True:
        refactor_raw = refactorer.act(state.to_dict())
        refactor_out, refactor_msg = validate_refactorer(refactor_raw)
        state.system_log.append({"timestamp": now_iso(), "message": refactor_msg})
        candidate_code = refactor_out.get("refactored_code") or impl_out.get("updated_code")
        state.system_log.append({"timestamp": now_iso(), "message": f"Refactorer candidate_code_len={len(candidate_code or '')}"})
        passed, details = run_tests(candidate_code or impl_out.get("updated_code", ""), state.full_test_suite)
        state.system_log.append({"timestamp": now_iso(), "message": f"Refactorer test run passed={passed}."})
        if passed:
            break
        ref_attempts += 1
        snippet = details.replace('\n',' ')[:300] if details else 'no details'
        state.system_log.append({"timestamp": now_iso(), "message": f"Refactorer failing tests attempt {ref_attempts}: {snippet}"})
        if ref_attempts >= max_retries:
            state.aborted = True
            state.abort_reason = "refactorer_retry_exhausted"
            return "aborted", {"tester": tester_out, "implementer": impl_out, "refactorer": refactor_out}

    # Supervisor phase only if not aborted
    supervisor_raw = supervisor.act(state.to_dict())
    supervisor_out, supervisor_msg = validate_supervisor(supervisor_raw)
    state.system_log.append({"timestamp": now_iso(), "message": supervisor_msg})
    if supervisor_out.get("heuristic_reason"):
        state.system_log.append(
            {
                "timestamp": now_iso(),
                "message": f"Supervisor heuristic_reason={supervisor_out.get('heuristic_reason')} status={supervisor_out.get('status')}",
            }
        )

    cycle = TDDCycle(
        cycle_number=cycle_number,
        tester_output=CycleTesterOutput(**tester_out),
        implementer_output=CycleImplementerOutput(**impl_out),
        refactorer_output=CycleRefactorerOutput(**refactor_out),
        supervisor_output=CycleSupervisorOutput(
            status=supervisor_out.get("status", ""),
            heuristic_reason=supervisor_out.get("heuristic_reason", ""),
        ),
    )
    append_cycle(state, cycle)

    # Update aggregate code/test suite after each cycle
    prev_code = pre_cycle_code
    new_code_candidate = (
        refactor_out.get("refactored_code")
        or impl_out.get("updated_code")
        or state.final_code
    )
    state.final_code = new_code_candidate
    from tdd_agents.diff import unified_code_diff

    diff = unified_code_diff(prev_code, state.final_code)
    if diff:
        state.code_diffs.append(diff)

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
    on_cycle: Any | None = None,
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
        if state.aborted:
            break
        status, _outputs = _run_cycle(
            state, cycle_number, tester, implementer, refactorer, supervisor
        )
        if on_cycle:
            try:
                on_cycle(state.to_dict(), cycle_number)
            except Exception as e:  # keep orchestration resilient
                state.system_log.append(
                    {"timestamp": now_iso(), "message": f"on_cycle callback error: {e}"}
                )
        if state.aborted:
            state.system_log.append(
                {"timestamp": now_iso(), "message": f"Aborted: {state.abort_reason}"}
            )
            break
        if status == "done":  # early stop
            state.system_log.append(
                {"timestamp": now_iso(), "message": "Supervisor signaled completion."}
            )
            break
    return state.to_dict()
