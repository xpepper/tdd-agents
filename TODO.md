# TODO

## Conceptual Checklist (High-Level)
1. Define core agent roles & interfaces
2. Establish shared state + JSON schema
3. Implement orchestrator TDD cycle loop
4. Add validation, logging, persistence
5. Provide CLI, tests, docs, example run

## Detailed Implementation Tasks
- Draft 5-item conceptual checklist
- Initialize Python project structure
- Add pyproject + dependencies (langchain)
- Define system state JSON schema
- Implement state persistence module
- Design agent base interface
- Stub Tester agent logic
- Stub Implementer agent logic
- Stub Refactorer agent logic
- Stub Supervisor agent logic
- Build orchestrator TDD cycle loop
- Add validation + self-correction hooks
- Implement logging subsystem
- Integrate error/deadlock handling
- Assemble JSON output builder
- Create sample kata input loader
- Implement minimal language abstraction
- Add CLI runner entrypoint
- Write unit tests for orchestrator
- Write unit tests for agents
- Document architecture & extensibility
- Prepare example Fibonacci run
- Review for modularity & clarity
- Polish README with usage
- Log supervisor heuristic reasons (stagnation vs max cycles)
- Accumulate full test suite across cycles (append not overwrite)
- Generate per-cycle code diffs for agent prompts

- Future: truncate large diffs in prompts
- Future: richer test execution reporting (timings, failures summary)
- Future: configurable snapshot retention (keep last N)
- Future: optional HTML report generation
