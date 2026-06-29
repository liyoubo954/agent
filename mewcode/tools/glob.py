from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from mewcode.tools.base import Tool, ToolResult, is_skipped_path


class Params(BaseModel):
    pattern: str = Field(description="Glob pattern to match files or directories (e.g. '**/*.py' or '*')")
    path: str = Field(default=".", description="Base directory to search from")


class Glob(Tool):
    name = "Glob"
    description = "Find files or directories matching a glob pattern, returning relative paths."
    params_model = Params
    category = "read"
    is_concurrency_safe = True

    def __init__(self) -> None:
        self._work_dir: str | None = None

    def set_work_dir(self, work_dir: str) -> None:
        self._work_dir = work_dir

    def _resolve_path(self, path_value: str) -> Path:
        base = Path(path_value)
        if not base.is_absolute() and self._work_dir:
            base = Path(self._work_dir) / base
        return base

    async def execute(self, params: Params) -> ToolResult:
        base = self._resolve_path(params.path)
        if not base.exists():
            return ToolResult(output=f"Error: path not found: {params.path}", is_error=True)

        try:
            matches: list[str] = []
            for p in base.glob(params.pattern):
                if is_skipped_path(p, base):
                    continue
                if p.is_file():
                    matches.append(str(p.relative_to(base)))
                elif p.is_dir():
                    matches.append(str(p.relative_to(base)) + "/")
            matches.sort()
        except Exception as e:
            return ToolResult(output=f"Error: {e}", is_error=True)

        if not matches:
            return ToolResult(output="No files matched the pattern.")
        return ToolResult(output=f"Matched {len(matches)} item(s):\n" + "\n".join(matches))
