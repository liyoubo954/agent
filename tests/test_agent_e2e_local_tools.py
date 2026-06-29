from __future__ import annotations

from typing import Any, AsyncIterator

import pytest

from mewcode.agent import Agent
from mewcode.client import LLMClient
from mewcode.conversation import ConversationManager
from mewcode.serialization import build_chat_completion_messages
from mewcode.tools import create_default_registry
from mewcode.tools.base import StreamEnd, StreamEvent, TextDelta, ToolCallComplete


class ScriptedClient(LLMClient):
    def __init__(self, responses: list[list[StreamEvent]]) -> None:
        self.responses = responses
        self.calls: list[ConversationManager] = []

    async def stream(
        self,
        conversation: ConversationManager,
        system: str = "",
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamEvent]:
        self.calls.append(conversation)
        events = self.responses.pop(0)
        for event in events:
            yield event


@pytest.mark.asyncio
async def test_local_agent_tool_roundtrip_uses_agent_work_dir(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "main.py").write_text("def answer():\n    return 42\n", encoding="utf-8")

    client = ScriptedClient([
        [
            ToolCallComplete("glob-1", "Glob", {"pattern": "**/*.py", "path": "."}),
            StreamEnd("end_turn", input_tokens=10, output_tokens=5),
        ],
        [
            ToolCallComplete("grep-1", "Grep", {"pattern": "answer", "path": ".", "include": "*.py"}),
            StreamEnd("end_turn", input_tokens=20, output_tokens=5),
        ],
        [
            ToolCallComplete("bash-1", "Bash", {"command": "echo ok", "timeout": 5}),
            ToolCallComplete("read-1", "ReadFile", {"file_path": "pkg/main.py"}),
            StreamEnd("end_turn", input_tokens=30, output_tokens=5),
        ],
        [
            TextDelta("Found pkg/main.py and verified it returns 42."),
            StreamEnd("end_turn", input_tokens=40, output_tokens=10),
        ],
    ])

    agent = Agent(
        client=client,
        registry=create_default_registry(),
        protocol="openai-compat",
        work_dir=str(tmp_path),
    )
    conv = ConversationManager()
    final = await agent.run_to_completion("Inspect the project and summarize.", conv)

    assert "returns 42" in final
    wire = build_chat_completion_messages(conv.get_messages())
    tool_outputs = [m for m in wire if m.get("role") == "tool"]
    assert len(tool_outputs) == 4
    assert any("pkg\\main.py" in m["content"] or "pkg/main.py" in m["content"] for m in tool_outputs)
    assert any("STDOUT" in m["content"] and "ok" in m["content"] for m in tool_outputs)


@pytest.mark.asyncio
async def test_agent_binds_local_tools_to_its_work_dir(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "main.py").write_text(
        "def answer():\n    return 42\n",
        encoding="utf-8",
    )

    client = ScriptedClient([
        [
            ToolCallComplete("glob-1", "Glob", {"pattern": "**/*.py", "path": "."}),
            ToolCallComplete(
                "read-1",
                "ReadFile",
                {"file_path": "pkg/main.py"},
            ),
            StreamEnd("end_turn", input_tokens=10, output_tokens=5),
        ],
        [
            TextDelta("Done."),
            StreamEnd("end_turn", input_tokens=20, output_tokens=5),
        ],
    ])

    registry = create_default_registry()
    agent = Agent(
        client=client,
        registry=registry,
        protocol="openai-compat",
        work_dir=str(tmp_path),
    )
    conv = ConversationManager()
    await agent.run_to_completion("Inspect the project.", conv)

    wire = build_chat_completion_messages(conv.get_messages())
    tool_outputs = [m["content"] for m in wire if m.get("role") == "tool"]
    assert any("Matched 1 item(s)" in output and "pkg" in output for output in tool_outputs)
    assert any("return 42" in output for output in tool_outputs)
