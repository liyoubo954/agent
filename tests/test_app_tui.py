from __future__ import annotations

from typing import AsyncIterator
from unittest.mock import patch

import pytest
from textual.widgets import Markdown

from mewcode.app import ChatInput, MewCodeApp
from mewcode.client import LLMClient
from mewcode.config import ProviderConfig
from mewcode.conversation import ConversationManager
from mewcode.permissions import PermissionMode
from mewcode.tools.base import StreamEnd, StreamEvent, TextDelta


class FakeClient(LLMClient):
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def stream(
        self,
        conversation: ConversationManager,
        system: str = "",
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamEvent]:
        self.calls.append(conversation.get_messages()[-1].content)
        yield TextDelta(f"answer-{len(self.calls)}")
        yield StreamEnd(stop_reason="end_turn", input_tokens=1, output_tokens=1)


@pytest.mark.asyncio
async def test_tui_renders_second_turn_answer(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    provider = ProviderConfig(
        name="fake",
        protocol="openai",
        base_url="http://fake",
        model="fake",
        api_key="x",
    )
    fake = FakeClient()

    with patch("mewcode.app.create_client", return_value=fake):
        app = MewCodeApp(providers=[provider], permission_mode=PermissionMode.DEFAULT)
        async with app.run_test(headless=True, size=(100, 30)) as pilot:
            input_widget = app.query_one("#chat-input", ChatInput)
            for text in ("first", "second"):
                input_widget.insert(text)
                input_widget.action_submit()
                await pilot.pause(0.8)

            rendered = [getattr(widget, "_markdown", "") for widget in app.query(Markdown)]

    assert len(fake.calls) == 2
    assert "answer-1" in rendered
    assert "answer-2" in rendered
