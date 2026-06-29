---
name: test
description: Run and interpret a project's test suite. Use when the user asks to test, verify, validate, run checks, reproduce a failure, diagnose failing tests, or assess whether recent code changes are safe. Supports Python, Go, Node.js, Rust, and mixed repositories by detecting project files and selecting the most appropriate test command.
allowedTools:
  - Bash
  - ReadFile
  - Grep
  - Glob
mode: inline
---

# Test Runner

Run the smallest reliable validation that answers the user's request, then explain the result with enough evidence for the user to act.

## Workflow

1. Identify the project type and test entrypoints.
   - Python: `pyproject.toml`, `setup.py`, `pytest.ini`, `tox.ini`; prefer `python -m pytest`.
   - Go: `go.mod`; prefer `go test ./...`.
   - Node.js: `package.json`; inspect scripts and prefer the declared test script.
   - Rust: `Cargo.toml`; prefer `cargo test`.
   - Mixed repo: run only the relevant suite unless the user asks for full validation.
2. Check existing instructions before inventing commands.
   - Read README, project instructions, CI config, or package scripts when present.
3. Run the selected command and preserve the important output.
   - Include the exact command.
   - Capture failing test names, assertion messages, stack traces, and exit codes.
4. Classify failures.
   - Code bug: product behavior contradicts the expected behavior.
   - Test bug: assertion, fixture, or test setup is wrong or outdated.
   - Environment issue: missing dependency, service, credential, network, or platform assumption.
5. Recommend the next action.
   - If tests pass, mention any meaningful coverage gap or skipped validation.
   - If tests fail, identify the first useful failure and the likely fix path.

## Output

Use this structure:

```text
Command:
<exact command>

Result:
PASS | FAIL | PARTIAL | SKIPPED

Findings:
- <high-signal observation>

Next step:
- <specific recommendation>
```

Keep the response concise. Do not paste long logs; quote only the lines needed to diagnose the result.

$ARGUMENTS
