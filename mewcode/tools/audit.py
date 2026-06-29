from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SENSITIVE_KEYWORDS = ("key", "token", "password", "secret", "authorization")
MAX_ARG_CHARS = 4000
MAX_OUTPUT_CHARS = 4000


def sanitize_audit_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(word in str(key).lower() for word in SENSITIVE_KEYWORDS):
                out[key] = "<redacted>"
            else:
                out[key] = sanitize_audit_value(item)
        return out
    if isinstance(value, list):
        return [sanitize_audit_value(item) for item in value[:100]]
    if isinstance(value, str):
        if len(value) > MAX_ARG_CHARS:
            return value[:MAX_ARG_CHARS] + "...(truncated)"
        return value
    return value


def _truncate_output(text: str) -> str:
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + "...(truncated)"
    return text


@dataclass
class ToolAuditLogger:
    work_dir: str
    session_id: str = ""

    @property
    def path(self) -> Path:
        return Path(self.work_dir) / ".mewcode" / "tool-audit.jsonl"

    def record(
        self,
        *,
        tool_id: str,
        tool_name: str,
        arguments: dict[str, Any] | None,
        status: str,
        elapsed: float,
        is_error: bool,
        output: str = "",
        permission: str = "",
        category: str = "",
        validation_error: str = "",
        exception: str = "",
    ) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            event = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "tool_id": tool_id,
                "tool_name": tool_name,
                "category": category,
                "status": status,
                "permission": permission,
                "elapsed_ms": round(elapsed * 1000, 2),
                "is_error": is_error,
                "arguments": sanitize_audit_value(arguments or {}),
                "output_preview": _truncate_output(output or ""),
            }
            if validation_error:
                event["validation_error"] = validation_error
            if exception:
                event["exception"] = exception
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        except Exception:
            return
