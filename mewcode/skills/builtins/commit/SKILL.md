---
name: commit
description: Create a clean Git commit from current repository changes. Use when the user asks to commit, prepare a commit message, stage changes, summarize diffs for commit, or make a safe checkpoint. Inspects git status and diffs, avoids secrets and unrelated files, stages only relevant paths, and writes a conventional, reviewable commit message.
allowedTools:
  - Bash
  - ReadFile
  - Grep
mode: inline
---

# Commit Assistant

Create one focused, reviewable commit that matches the user's intent and the actual diff.

## Workflow

1. Inspect repository state.
   - Run `git status --short --branch`.
   - Run `git diff --stat`, `git diff`, and `git diff --staged` as needed.
2. Decide commit scope.
   - Include only files relevant to the user's requested change.
   - Leave unrelated local changes untouched.
   - Do not stage secrets, credentials, local config, cache files, virtual environments, or generated noise.
3. Choose the commit type.
   - `feat`: user-facing or developer-facing feature.
   - `fix`: bug fix.
   - `docs`: documentation-only change.
   - `test`: tests only.
   - `refactor`: behavior-preserving code restructuring.
   - `chore`: maintenance, tooling, metadata, or dependency housekeeping.
4. Write the message.
   - Prefer `type(scope): summary`.
   - Use English.
   - Keep the summary under 72 characters.
   - Add a body only when the reason or risk is not obvious from the diff.
5. Stage deliberately.
   - Prefer explicit file paths.
   - Use broad staging only when the diff has been reviewed and is clearly scoped.
6. Commit and report the result.
   - Include the commit hash and message.
   - Mention any uncommitted files left intentionally.

## Safety Checks

- Stop and report if the diff contains obvious secrets or private local paths.
- Stop and ask if the repository has conflicting changes that make the intended commit ambiguous.
- Do not amend, rebase, reset, force-push, or rewrite history unless the user explicitly asks.

$ARGUMENTS
