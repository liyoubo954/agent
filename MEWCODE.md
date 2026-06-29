# MewCode Project Instructions

@include .mewcode/harness.md

## Project Facts

- This is a Python terminal AI coding assistant, not a Go project.
- Main package: `mewcode`.
- Main local entrypoint: `D:\anconda\envs\MewCode\python.exe -m mewcode`.
- Test runner: `D:\anconda\envs\MewCode\python.exe -m pytest`.
- Keep changes inside the current architecture: agent loop, model protocol, tools, context, permissions, memory, skills, MCP, subagents, teams, hooks, commands, sessions, and worktree support.
- Do not add features merely because Claude Code has them. Implement only behavior that is already represented by project modules, tools, configuration, or tests.
- Do not print API keys or secrets from `.mewcode/config.yaml` or environment variables.
