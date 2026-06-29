"""MCP 客户端系统的测试（第 6 章）。"""
from __future__ import annotations

import asyncio
import os
import sys
import textwrap
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from mewcode.config import (
    AppConfig,
    ConfigError,
    MCPServerConfig,
    build_child_env,
    load_config,
    resolve_env_vars,
)

# ===========================================================================
# resolve_env_vars
# ===========================================================================

class TestResolveEnvVars:

    def test_substitutes_existing_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_TOKEN", "secret123")
        assert resolve_env_vars("${MY_TOKEN}") == "secret123"

    def test_preserves_missing_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        assert resolve_env_vars("${NONEXISTENT_VAR}") == "${NONEXISTENT_VAR}"

    def test_no_placeholder_passthrough(self) -> None:
        assert resolve_env_vars("plain-text") == "plain-text"

    def test_multiple_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("A", "hello")
        monkeypatch.setenv("B", "world")
        assert resolve_env_vars("${A}-${B}") == "hello-world"

    def test_mixed_existing_and_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("EXISTS", "yes")
        monkeypatch.delenv("NOPE", raising=False)
        assert resolve_env_vars("${EXISTS}/${NOPE}") == "yes/${NOPE}"

# ===========================================================================
# build_child_env
# ===========================================================================

class TestBuildChildEnv:
    def test_includes_path(self) -> None:
        env = build_child_env(None)
        assert "PATH" in env

    def test_includes_declared_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_SECRET", "abc")
        env = build_child_env({"TOKEN": "${MY_SECRET}"})
        assert env["TOKEN"] == "abc"
        assert "PATH" in env

    def test_excludes_host_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret")
        env = build_child_env({"FOO": "bar"})
        assert "ANTHROPIC_API_KEY" not in env
        assert env["FOO"] == "bar"

    def test_empty_declared_env(self) -> None:
        env = build_child_env({})
        assert "PATH" in env
        assert len(env) == 1

# ===========================================================================
# load_config：解析 mcp_servers
# ===========================================================================

class TestLoadConfigMCP:
    def _write_config(self, tmp_path: Path, content: str) -> Path:
        p = tmp_path / "config.yaml"
        p.write_text(textwrap.dedent(content))
        return p

    def test_no_mcp_servers(self, tmp_path: Path) -> None:
        path = self._write_config(tmp_path, """\
            providers:
              - name: test
                protocol: openai
                base_url: http://localhost
                model: gpt-4o
        """)
        config = load_config(path)
        assert config.mcp_servers == []

    def test_stdio_server(self, tmp_path: Path) -> None:
        path = self._write_config(tmp_path, """\
            providers:
              - name: test
                protocol: openai
                base_url: http://localhost
                model: gpt-4o
            mcp_servers:
              github:
                command: npx
                args: ["-y", "@modelcontextprotocol/server-github"]
                env:
                  GITHUB_TOKEN: "${GITHUB_TOKEN}"
        """)
        config = load_config(path)
        assert len(config.mcp_servers) == 1
        srv = config.mcp_servers[0]
        assert srv.name == "github"
        assert srv.command == "npx"
        assert srv.is_stdio is True
        assert srv.args == ["-y", "@modelcontextprotocol/server-github"]

    def test_http_server(self, tmp_path: Path) -> None:
        path = self._write_config(tmp_path, """\
            providers:
              - name: test
                protocol: openai
                base_url: http://localhost
                model: gpt-4o
            mcp_servers:
              remote:
                url: "https://api.example.com/mcp"
                headers:
                  Authorization: "Bearer ${TOKEN}"
        """)
        config = load_config(path)
        srv = config.mcp_servers[0]
        assert srv.name == "remote"
        assert srv.url == "https://api.example.com/mcp"
        assert srv.is_stdio is False

    def test_both_command_and_url_errors(self, tmp_path: Path) -> None:
        path = self._write_config(tmp_path, """\
            providers:
              - name: test
                protocol: openai
                base_url: http://localhost
                model: gpt-4o
            mcp_servers:
              bad:
                command: npx
                url: "https://example.com"
        """)
        with pytest.raises(ConfigError, match="cannot have both"):
            load_config(path)

    def test_neither_command_nor_url_errors(self, tmp_path: Path) -> None:
        path = self._write_config(tmp_path, """\
            providers:
              - name: test
                protocol: openai
                base_url: http://localhost
                model: gpt-4o
            mcp_servers:
              bad:
                env:
                  FOO: bar
        """)
        with pytest.raises(ConfigError, match="must have either"):
            load_config(path)

# ===========================================================================
# MCPToolWrapper
# ===========================================================================

class TestMCPToolWrapper:
    def test_name_format(self) -> None:
        from mcp import types as mcp_types
        from mewcode.mcp.tool_wrapper import MCPToolWrapper
        from mewcode.mcp.client import MCPClient

        tool_def = mcp_types.Tool(
            name="search_issues",
            description="Search GitHub issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["repo"],
            },
        )
        mock_client = MagicMock(spec=MCPClient)
        wrapper = MCPToolWrapper("github", tool_def, mock_client)

        assert wrapper.name == "mcp__github__search_issues"
        assert wrapper.category == "command"
        assert wrapper.description == "Search GitHub issues"

    def test_get_schema_uses_original_input_schema(self) -> None:
        from mcp import types as mcp_types
        from mewcode.mcp.tool_wrapper import MCPToolWrapper

        input_schema = {
            "type": "object",
            "properties": {"q": {"type": "string"}},
            "required": ["q"],
        }
        tool_def = mcp_types.Tool(
            name="search",
            description="Search",
            inputSchema=input_schema,
        )
        mock_client = MagicMock()
        wrapper = MCPToolWrapper("srv", tool_def, mock_client)

        schema = wrapper.get_schema()
        assert schema["name"] == "mcp__srv__search"
        assert schema["input_schema"] == input_schema

# ===========================================================================
# _extract_text
# ===========================================================================

class TestExtractText:
    def test_text_content(self) -> None:
        from mcp import types as mcp_types
        from mewcode.mcp.tool_wrapper import _extract_text

        content = [
            mcp_types.TextContent(type="text", text="hello"),
            mcp_types.TextContent(type="text", text="world"),
        ]
        assert _extract_text(content) == "hello\nworld"

    def test_empty_content(self) -> None:
        from mewcode.mcp.tool_wrapper import _extract_text

        assert _extract_text([]) == "(no output)"

    def test_image_content(self) -> None:
        from mcp import types as mcp_types
        from mewcode.mcp.tool_wrapper import _extract_text

        content = [mcp_types.ImageContent(type="image", data="...", mimeType="image/png")]
        assert "[image: image/png]" in _extract_text(content)

# ===========================================================================
# MCPManager：部分失败容错
# ===========================================================================

class TestMCPManagerPartialFailure:
    @pytest.mark.asyncio
    async def test_single_server_failure_does_not_block_others(self) -> None:
        from mewcode.mcp.manager import MCPManager
        from mewcode.tools import ToolRegistry

        good_config = MCPServerConfig(
            name="good",
            command="echo",
            args=["hello"],
        )
        bad_config = MCPServerConfig(
            name="bad",
            command="nonexistent_command_xyz_12345",
        )

        manager = MCPManager()
        manager.load_configs([bad_config, good_config])

        registry = ToolRegistry()

        with patch("mewcode.mcp.manager.MCPClient") as MockClient:
            good_instance = AsyncMock()
            good_instance.is_alive = True

            from mcp import types as mcp_types
            good_instance.list_tools.return_value = [
                mcp_types.Tool(
                    name="test_tool",
                    description="A test",
                    inputSchema={"type": "object", "properties": {}},
                )
            ]

            bad_instance = AsyncMock()
            bad_instance.connect.side_effect = RuntimeError("command not found")

            def make_client(config: MCPServerConfig) -> AsyncMock:
                if config.name == "bad":
                    return bad_instance
                return good_instance

            MockClient.side_effect = make_client

            errors = await manager.register_all_tools(registry)

        assert len(errors) == 1
        assert "bad" in errors[0]
        assert registry.get("mcp__good__test_tool") is not None


class TestMCPToolResultFormatting:
    def test_structured_content_is_preserved(self) -> None:
        from mcp import types as mcp_types
        from mewcode.mcp.tool_wrapper import _format_mcp_result

        result = mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text='{"ok": true}')],
            structuredContent={"ok": True, "items": [1, 2]},
            isError=False,
        )

        formatted = _format_mcp_result(result)
        assert "structuredContent" in formatted
        assert '"items"' in formatted


class TestLocalMCPServerIntegration:
    @pytest.mark.asyncio
    async def test_local_stdio_server_lists_and_calls_tools(self, tmp_path: Path) -> None:
        from mewcode.mcp.client import MCPClient

        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "main.py").write_text(
            "def answer():\n    return 42\n",
            encoding="utf-8",
        )

        client = MCPClient(MCPServerConfig(
            name="local",
            command=sys.executable,
            args=["-m", "mewcode.mcp.local_server", "--root", str(tmp_path)],
        ))

        try:
            await client.connect()
            tools = await client.list_tools()
            names = {tool.name for tool in tools}
            assert {"fs_list", "fs_read", "code_search", "memory_set", "memory_get", "shell_exec"}.issubset(names)

            read_result = await client.call_tool("fs_read", {"path": "pkg/main.py"})
            assert not read_result.isError
            assert any("return 42" in getattr(block, "text", "") for block in read_result.content)

            search_result = await client.call_tool("code_search", {"pattern": "answer", "path": "."})
            assert not search_result.isError
            assert "pkg" in str(search_result.structuredContent)

            shell_result = await client.call_tool("shell_exec", {"command": "echo ok", "timeout": 5})
            assert not shell_result.isError
            assert "ok" in str(shell_result.structuredContent)

            blocked_shell = await client.call_tool("shell_exec", {"command": "echo ok > out.txt", "timeout": 5})
            assert "shell control operators are not allowed" in str(blocked_shell.structuredContent)

            dangerous_shell = await client.call_tool("shell_exec", {"command": "del README.md", "timeout": 5})
            assert "dangerous command token blocked" in str(dangerous_shell.structuredContent)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_local_server_blocks_path_escape(self, tmp_path: Path) -> None:
        from mewcode.mcp.client import MCPClient

        client = MCPClient(MCPServerConfig(
            name="local",
            command=sys.executable,
            args=["-m", "mewcode.mcp.local_server", "--root", str(tmp_path)],
        ))
        try:
            await client.connect()
            result = await client.call_tool("fs_read", {"path": "../outside.txt"})
            assert result.isError or "outside MCP root" in str(result.content)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_manager_registers_local_tools_and_wrapper_executes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from mewcode.mcp.manager import MCPManager
        from mewcode.tools import ToolRegistry

        (tmp_path / "README.md").write_text("hello from local mcp\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        manager = MCPManager()
        manager.load_configs([
            MCPServerConfig(
                name="local",
                command=sys.executable,
                args=["-m", "mewcode.mcp.local_server", "--root", str(tmp_path)],
            )
        ])
        registry = ToolRegistry()
        try:
            errors = await manager.register_all_tools(registry)
            assert errors == []
            tool = registry.get("mcp__local__fs_read")
            assert tool is not None

            result = await tool.execute(tool.params_model(path="README.md"))
            assert not result.is_error
            assert "hello from local mcp" in result.output
        finally:
            await manager.shutdown()
