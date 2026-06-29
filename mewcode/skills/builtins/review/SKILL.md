---
name: review
description: Perform a code review of current or recent repository changes. Use when the user asks for review, code review, inspect changes, find bugs, assess risk, check a PR-style diff, or evaluate whether a change is safe. Prioritizes correctness, security, regressions, data loss, performance, and missing tests over style comments.
allowedTools:
  - Bash
  - ReadFile
  - Grep
  - Glob
mode: fork
context: none
---

# Code Review

Review the diff as a senior engineer. Lead with concrete findings that could affect users, production behavior, data, security, or maintainability.

## Workflow

1. Identify the review target.
   - Run `git diff` for unstaged changes.
   - Run `git diff --staged` for staged changes.
   - If both are empty, review the latest commit with `git diff HEAD~1..HEAD`.
2. Build enough context.
   - Read changed files around the modified lines.
   - Search for callers, tests, config, migrations, and related interfaces.
   - Prefer evidence from code paths over assumptions.
3. Prioritize issues.
   - Correctness bugs and regressions.
   - Security and permission problems.
   - Data loss, schema, migration, or compatibility risks.
   - Performance problems with realistic scale impact.
   - Missing or weak tests for risky behavior.
4. Avoid low-value comments.
   - Do not list generic style preferences.
   - Do not praise unless it clarifies why no issue was found.
   - Do not invent issues that are not supported by the diff or surrounding code.

## Output

Use this structure:

```text
Findings:
- [Severity] path:line - Issue and impact. Suggested fix.

Open Questions:
- <only if needed>

Test Gaps:
- <missing validation or not run>
```

Severity:

- `Critical`: likely production breakage, data loss, security vulnerability, or unusable feature.
- `High`: clear bug or regression in a common path.
- `Medium`: plausible bug, edge-case breakage, or important missing validation.
- `Low`: maintainability or test coverage concern with limited immediate impact.

If no issues are found, say so clearly and mention the remaining verification limits.

$ARGUMENTS
