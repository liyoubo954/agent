from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".mewcode",
    ".pytest_cache",
    ".uv-cache",
    ".venv",
    ".venvs",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
}

SAFE_COMMANDS = {
    "echo",
    "pwd",
    "cd",
    "dir",
    "ls",
    "python",
    "pytest",
    "rg",
    "where",
    "Get-ChildItem",
    "Get-Location",
}
SAFE_COMMANDS_LOWER = {cmd.lower() for cmd in SAFE_COMMANDS}
SHELL_CONTROL_PATTERN = re.compile(r"(&&?|\|\|?|[;<>`()]|\$\()")

DANGEROUS_TOKENS = {
    "rm",
    "del",
    "erase",
    "rmdir",
    "remove-item",
    "format",
    "shutdown",
    "restart-computer",
    "reg",
    "set-executionpolicy",
}


def _server_root() -> Path:
    raw = os.environ.get("MEWCODE_MCP_ROOT") or os.getcwd()
    return Path(raw).resolve()


mcp = FastMCP(
    "mewcode-local",
    instructions=(
        "Local MCP server for MewCode. Tools are rooted at MEWCODE_MCP_ROOT "
        "and are intended for filesystem inspection, code search, small memory "
        "records, safe HTTP GET requests, and restricted shell execution."
    ),
)


def _resolve_path(path: str | None = None) -> Path:
    root = _server_root()
    raw = path or "."
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path outside MCP root is not allowed: {path}") from exc
    return resolved


def _is_excluded(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts)


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _load_memory() -> dict[str, Any]:
    memory_file = _server_root() / ".mewcode" / "mcp-memory.json"
    if not memory_file.exists():
        return {}
    try:
        raw = json.loads(memory_file.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def _save_memory(memory: dict[str, Any]) -> None:
    memory_file = _server_root() / ".mewcode" / "mcp-memory.json"
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@mcp.tool()
def fs_list(path: str = ".", recursive: bool = False, limit: int = 200) -> dict[str, Any]:
    """List files under the MCP root."""
    root = _server_root()
    target = _resolve_path(path)
    if not target.exists():
        return {"ok": False, "error": "path not found", "path": str(target)}
    if not target.is_dir():
        return {"ok": False, "error": "path is not a directory", "path": str(target)}

    max_items = max(1, min(int(limit), 1000))
    iterator = target.rglob("*") if recursive else target.iterdir()
    items: list[dict[str, Any]] = []
    for entry in sorted(iterator, key=lambda p: str(p).lower()):
        if _is_excluded(entry):
            continue
        rel = entry.relative_to(root)
        items.append({
            "path": str(rel),
            "type": "dir" if entry.is_dir() else "file",
            "size": entry.stat().st_size if entry.is_file() else None,
        })
        if len(items) >= max_items:
            break
    return {"ok": True, "root": str(root), "items": items, "truncated": len(items) >= max_items}


@mcp.tool()
def fs_read(path: str, max_chars: int = 12000) -> dict[str, Any]:
    """Read a text file under the MCP root."""
    root = _server_root()
    target = _resolve_path(path)
    if not target.exists():
        return {"ok": False, "error": "file not found", "path": str(target)}
    if not target.is_file():
        return {"ok": False, "error": "path is not a file", "path": str(target)}
    text = _read_text(target)
    max_len = max(1, min(int(max_chars), 200000))
    return {
        "ok": True,
        "path": str(target.relative_to(root)),
        "content": text[:max_len],
        "truncated": len(text) > max_len,
    }


@mcp.tool()
def code_search(pattern: str, path: str = ".", include: str = "", limit: int = 100) -> dict[str, Any]:
    """Search text files under the MCP root using a regular expression."""
    root = _server_root()
    target = _resolve_path(path)
    if not target.exists():
        return {"ok": False, "error": "path not found", "path": str(target)}
    regex = re.compile(pattern)
    max_items = max(1, min(int(limit), 1000))
    files = [target] if target.is_file() else target.rglob(include or "*")
    matches: list[dict[str, Any]] = []
    for file_path in files:
        if not file_path.is_file() or _is_excluded(file_path):
            continue
        try:
            text = _read_text(file_path)
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                matches.append({
                    "path": str(file_path.relative_to(root)),
                    "line": lineno,
                    "text": line[:500],
                })
                if len(matches) >= max_items:
                    return {"ok": True, "matches": matches, "truncated": True}
    return {"ok": True, "matches": matches, "truncated": False}


@mcp.tool()
def memory_set(key: str, value: str) -> dict[str, Any]:
    """Store a small project-local MCP memory value."""
    if not key or len(key) > 200:
        return {"ok": False, "error": "key must be 1-200 characters"}
    memory = _load_memory()
    memory[key] = value
    _save_memory(memory)
    return {"ok": True, "key": key}


@mcp.tool()
def memory_get(key: str = "") -> dict[str, Any]:
    """Read one or all project-local MCP memory values."""
    memory = _load_memory()
    if key:
        return {"ok": True, "key": key, "value": memory.get(key)}
    return {"ok": True, "items": memory}


@mcp.tool()
def http_fetch(url: str, timeout: float = 10.0, max_chars: int = 20000) -> dict[str, Any]:
    """Fetch a URL with HTTP GET and return text content."""
    if not url.startswith(("http://", "https://")):
        return {"ok": False, "error": "only http:// and https:// URLs are supported"}
    req = urllib.request.Request(url, headers={"User-Agent": "MewCode-MCP/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=max(1.0, min(float(timeout), 30.0))) as resp:
            data = resp.read(max(1, min(int(max_chars), 200000)) + 1)
            charset = resp.headers.get_content_charset() or "utf-8"
            text = data.decode(charset, errors="replace")
            max_len = max(1, min(int(max_chars), 200000))
            return {
                "ok": True,
                "status": resp.status,
                "url": url,
                "content": text[:max_len],
                "truncated": len(text) > max_len,
            }
    except urllib.error.URLError as exc:
        return {"ok": False, "error": str(exc)}


@mcp.tool()
def shell_exec(command: str, timeout: float = 10.0) -> dict[str, Any]:
    """Run a restricted, non-destructive shell command under the MCP root."""
    lowered = command.strip().lower()
    if not lowered:
        return {"ok": False, "error": "command is required"}
    if SHELL_CONTROL_PATTERN.search(command):
        return {"ok": False, "error": "shell control operators are not allowed"}
    first = command.strip().split()[0]
    tokens = [token for token in re.split(r"\s+", lowered) if token]
    if any(token in DANGEROUS_TOKENS for token in tokens):
        return {"ok": False, "error": "dangerous command token blocked"}
    if first.lower() not in SAFE_COMMANDS_LOWER:
        return {"ok": False, "error": f"command '{first}' is not in the MCP safe allowlist"}
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=str(_server_root()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(1.0, min(float(timeout), 30.0)),
        )
        return {
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-20000:],
            "stderr": completed.stderr[-20000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "error": "command timed out",
            "stdout": (exc.stdout or "")[-20000:],
            "stderr": (exc.stderr or "")[-20000:],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="MewCode local MCP server")
    parser.add_argument("--root", default=None, help="Root directory exposed to MCP tools")
    args = parser.parse_args()
    if args.root:
        os.environ["MEWCODE_MCP_ROOT"] = str(Path(args.root).resolve())
    mcp.run("stdio")


if __name__ == "__main__":
    main()
