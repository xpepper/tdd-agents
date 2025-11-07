# Objective
Develop a Python prototype for a multi-agent Test-Driven Development (TDD) tool using LangChain. The prototype should be generic, able to work with any programming language and kata, utilizing a user-supplied kata description and goal.
For any of the agents we'll be using an LLM provider such as OpenAI or Anthropic via LangChain. It should be possible to use any LLM provider compatible with the OpenAI API standard.

Begin with a concise checklist (3–7 conceptual bullet points) outlining the main components and sequencing steps you will follow. Keep these items conceptual rather than implementation-specific.

# Core Agents
Define and scaffold the following agents:
- **Tester Agent:** Generates a small, failing unit test to capture new required behavior.
- **Implementer Agent:** Updates the code to make the failing test pass using a minimal change. May request a refactor before fixing the test if that facilitates a simpler implementation.
- **Refactorer Agent:** Improves code readability, structure, and maintainability after all tests pass (e.g., splitting large functions, improving naming), making the code easier to understand and modify.
Agents must operate in incremental TDD cycles: writing a failing test, implementing a simple passing solution, then refactoring. Agents may communicate adaptively (e.g., Implementer can hand off to Refactorer before submitting a final solution), but must preserve the strict TDD cycle logic.
After each agent cycle or code update, validate the step in 1–2 lines and proceed or self-correct if validation fails. For every agent action—especially before invoking tools, code edits, or integrations—briefly state the purpose and minimal inputs.

# Supervisor Agent
Scaffold a fourth agent:
- **Supervisor Agent:** Oversees the TDD workflow, monitors agent progress, and intervenes if progress stalls (for example, by proposing simpler tests or preemptive refactoring if the Tester Agent cannot produce a viable test).

# Extensibility and Clarity
Design the code to be modular, supporting straightforward future integration with a UI that displays agent outputs and workflow progress. Scaffold the LangChain agents, orchestrator logic, and a basic TDD cycle loop using placeholder (stub) logic to clearly delineate responsibilities and support separation of concerns.
Use only tools and external resources consistent with permitted LangChain integrations. For any new integration, explain its necessity and required inputs before invocation. Use only those listed in allowed_tools; for routine read-only tasks call automatically, for destructive tasks require explicit confirmation.

# Output Format
Represent the complete system state and workflow in a single structured JSON object, containing, at minimum:
- `language`: (string) Programming language for the kata
- `kata_description`: (string) Full user-provided kata description and goal
- `tdd_history`: (array) Ordered list of TDD cycles (by `cycle_number`, ascending); each object includes:
- `cycle_number`: (int) Sequential cycle number
- `tester_output`:
- `test_code`: (string) Language-specific test code
- `test_description`: (string) Brief summary of the test's intent
- `implementer_output`:
- `updated_code`: (string) Code changes made to pass the test
- `implementation_notes`: (string) Implementation rationale
- `refactorer_output`:
- `refactored_code`: (string) Code after refactoring
- `refactor_notes`: (string) Explanation of refactor decisions
- `supervisor_output`:
- `status`: (string) Summary or intervention/update
- `issues_identified`: (array) List of problems that occurred (can be empty)
- `suggested_actions`: (array) Supervisor suggestions if stuck (can be empty)
- `final_code`: (string) Complete codebase after all TDD cycles
- `full_test_suite`: (string) Concatenated code for all tests written
- `system_log`: (array) Log entries, each as an object with:
- `timestamp`: (string, ISO 8601 format)
- `message`: (string) Description of the action, agent message, or supervisor intervention

## Logging, Error Handling, and Persistence
- All errors, deadlocks, or exceptions among agents must:
- Populate the relevant `supervisor_output > issues_identified` field
- Append a corresponding entry to the `system_log`
- The state representation must support persistence between cycles and straightforward UI integration.

## Example Output Structure
```json
{
    "language": "python",
    "kata_description": "Implement a function that returns the nth Fibonacci number.",
    "tdd_history":
    [
        {
            "cycle_number": 1,
            "tester_output":
            {
                "test_code": "def test_fib0(): assert fib(0) == 0",
                "test_description": "Test that fib(0) returns 0."
            },
            "implementer_output":
            {
                "updated_code": "def fib(n): return 0",
                "implementation_notes": "Minimal implementation to pass fib(0)."
            },
            "refactorer_output":
            {
                "refactored_code": "def fib(n): return 0",
                "refactor_notes": "No refactor needed at this step."
            },
            "supervisor_output":
            {
                "status": "Cycle complete.",
                "issues_identified":
                [],
                "suggested_actions":
                []
            }
        }
    ],
    "final_code": "def fib(n): return 0",
    "full_test_suite": "def test_fib0(): assert fib(0) == 0",
    "system_log":
    [
        {
            "timestamp": "2024-06-25T12:00:00Z",
            "message": "Cycle 1 started."
        },
        {
            "timestamp": "2024-06-25T12:00:01Z",
            "message": "Tester created test for fib(0)."
        },
        {
            "timestamp": "2024-06-25T12:00:02Z",
            "message": "Implementer made code pass for fib(0)."
        },
        {
            "timestamp": "2024-06-25T12:00:03Z",
            "message": "No refactor needed."
        },
        {
            "timestamp": "2024-06-25T12:00:04Z",
            "message": "Supervisor reports no issues."
        }
    ]
}
```
