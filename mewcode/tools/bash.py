from __future__ import annotations

import asyncio
from pathlib import Path

from pydantic import BaseModel, Field

from mewcode.tools.base import Tool, ToolResult

MAX_TIMEOUT = 600


class Params(BaseModel):
    command: str = Field(description="Shell command to execute")
    timeout: int = Field(default=120, description="Timeout in seconds (max 600)")


class Bash(Tool):
    name = "Bash"
    description = "Execute a shell command and return stdout and stderr."
    params_model = Params
    category = "command"

    def __init__(self, cwd: str | None = None) -> None:
        self.cwd = cwd

    def set_work_dir(self, work_dir: str) -> None:
        self.cwd = work_dir

    def get_execution_timeout(self, params: BaseModel) -> float:
        assert isinstance(params, Params)
        return float(min(params.timeout, MAX_TIMEOUT) + 5)

    async def execute(self, params: Params) -> ToolResult:
        timeout = min(params.timeout, MAX_TIMEOUT)
        cwd = str(Path(self.cwd).resolve()) if self.cwd else None

        try:
            proc = await asyncio.create_subprocess_shell(
                params.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ToolResult(output=f"Error: command timed out after {timeout}s", is_error=True)
        except Exception as e:
            return ToolResult(output=f"Error executing command: {e}", is_error=True)

        parts: list[str] = []
        if stdout:
            parts.append(f"STDOUT:\n{stdout.decode(errors='replace')}")
        if stderr:
            parts.append(f"STDERR:\n{stderr.decode(errors='replace')}")
        if not parts:
            parts.append("(no output)")

        output = "\n".join(parts)
        if (
            proc.returncode != 0
            and params.command.strip().lower().startswith("git status")
            and "not a git repository" in output.lower()
        ):
            return ToolResult(output=output, is_error=False)
        return ToolResult(output=output, is_error=proc.returncode != 0)
