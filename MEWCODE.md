# MewCode Project Instructions

@include .mewcode/harness.md

## Project Facts

- This is a Python terminal AI coding assistant, not a Go project.
- Main package: `mewcode`.
- Main CLI entrypoint: `python -m mewcode`.
- Installed console command: `mewcode`.
- Local development entrypoint used by the original environment: `D:\anconda\envs\MewCode\python.exe -m mewcode`.
- Test runner used by the original environment: `D:\anconda\envs\MewCode\python.exe -m pytest`.
- Keep changes inside the existing architecture: agent loop, model protocol, tools, context, permissions, memory, skills, MCP, subagents, teams, hooks, commands, sessions, and worktree support.
- Do not add features merely because another coding assistant has them. Implement only behavior that is already represented by project modules, tools, configuration, or tests.
- Do not print API keys or secrets from `.mewcode/config.yaml`, `.mewcode/config.local.yaml`, environment variables, or user-level config files.

## Development Notes

- Prefer the existing module boundaries and naming style.
- When changing config behavior, update both `mewcode/config.py` and `mewcode/validator.py`.
- When changing commands, check `mewcode/commands/handlers/` and the interactive `/help` behavior.
- When changing tools, check registration in `mewcode/tools/__init__.py` and any permission implications.
- When changing agent behavior, add or update focused tests under `tests/`.
