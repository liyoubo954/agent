# MewCode

MewCode 是一个基于 Python 的终端 AI 编程助手，面向本地代码仓库的阅读、修改、验证和协作开发场景。它提供交互式 TUI、非交互式命令执行、文件工具、Shell 工具、权限控制、会话管理、记忆、Skills、MCP、子 Agent、团队协作和 Git worktree 支持。

## 特性概览

- **终端交互**：基于 Textual 构建，支持连续对话、流式输出和斜杠命令。
- **一次性执行**：通过 `mewcode -p "..."` 在脚本或 CI 类场景中执行单次任务。
- **多 Provider 支持**：支持 `anthropic`、`openai` 和 `openai-compat` 协议。
- **内置代码工具**：提供文件读取、写入、编辑、搜索、路径匹配和 Shell 执行能力。
- **权限与沙箱**：结合权限模式、危险命令检测、路径规则和本地规则文件控制工具调用。
- **Skills 扩展**：通过 `SKILL.md` 描述可复用工作流，让 Agent 在特定任务中具备稳定操作策略。
- **MCP 集成**：支持 stdio 和 URL 形式的 MCP Server，并将外部能力注册为工具。
- **子 Agent 与团队协作**：支持后台任务、子 Agent、团队成员、消息通信和任务跟踪。
- **Worktree 隔离**：可为复杂任务创建隔离工作区，降低改动互相干扰的风险。
- **会话与记忆**：支持会话保存、恢复、压缩、项目说明和长期记忆。

## 环境要求

- Python `>= 3.11`
- 推荐使用虚拟环境、Conda 或 `uv`
- 至少配置一个可用的大模型 Provider

核心依赖见 [pyproject.toml](./pyproject.toml)，包括 `textual`、`anthropic`、`openai`、`pyyaml`、`pydantic`、`mcp` 和 `httpx`。

## 安装

进入项目目录：

```powershell
cd path\to\mewcode
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装项目：

```powershell
pip install -e .
```

使用 `uv` 时可以执行：

```powershell
uv sync
```

## 配置

MewCode 会按顺序读取以下配置文件：

1. `~/.mewcode/config.yaml`
2. 当前项目下的 `.mewcode/config.yaml`
3. 当前项目下的 `.mewcode/config.local.yaml`

后加载的项目级配置会补充或覆盖用户级配置。包含 API Key、本地路径或临时设置的配置文件不应提交到仓库。

### OpenAI 示例

```yaml
providers:
  - name: openai
    protocol: openai
    base_url: https://api.openai.com/v1
    model: gpt-4.1
    api_key: ${OPENAI_API_KEY}

permission_mode: default
```

### Anthropic 示例

```yaml
providers:
  - name: anthropic
    protocol: anthropic
    base_url: https://api.anthropic.com
    model: claude-sonnet-4
    api_key: ${ANTHROPIC_API_KEY}

permission_mode: default
```

### OpenAI 兼容接口示例

```yaml
providers:
  - name: local-compatible
    protocol: openai-compat
    base_url: http://localhost:8000/v1
    model: your-model-name
    api_key: ${OPENAI_API_KEY}
```

### 常用配置项

```yaml
permission_mode: default
enable_fork: false
enable_verification_agent: false
teammate_mode: ""
enable_coordinator_mode: false

worktree:
  symlink_directories:
    - node_modules
    - .venv
    - vendor
  stale_cleanup_interval: 3600
  stale_cutoff_hours: 24
```

`permission_mode` 支持：

- `default`
- `acceptEdits`
- `plan`
- `bypassPermissions`
- `custom`
- `dontAsk`

## 运行

交互式启动：

```powershell
mewcode
```

模块方式启动：

```powershell
python -m mewcode
```

指定权限模式：

```powershell
mewcode --mode plan
```

非交互模式：

```powershell
mewcode -p "阅读这个项目并总结主要模块"
```

保留终端 scrollback，不进入 alternate screen：

```powershell
$env:MEWCODE_NO_ALT_SCREEN = "1"
mewcode
```

## MCP 示例

仓库提供本地 MCP 配置示例：[examples/mcp-local-config.yaml](./examples/mcp-local-config.yaml)。

可将其中的 `mcp_servers` 合并到 `.mewcode/config.yaml`：

```yaml
mcp_servers:
  local:
    command: python
    args:
      - -m
      - mewcode.mcp.local_server
      - --root
      - <project-root>
    env:
      MEWCODE_MCP_ROOT: <project-root>
```

手动启动本地 MCP Server：

```powershell
python -m mewcode.mcp.local_server --root path\to\project
```

## 目录结构

```text
mewcode/
|-- mewcode/                  # 主包
|   |-- __main__.py           # CLI 入口
|   |-- app.py                # Textual 交互应用
|   |-- agent.py              # Agent 主循环与工具调用
|   |-- client.py             # 模型客户端适配
|   |-- config.py             # 配置加载与合并
|   |-- validator.py          # 配置校验
|   |-- commands/             # 斜杠命令
|   |-- tools/                # 内置工具
|   |-- permissions/          # 权限、规则和沙箱
|   |-- mcp/                  # MCP 客户端和本地 Server
|   |-- skills/               # Skills 解析、加载和执行
|   |-- agents/               # 子 Agent 定义、加载和跟踪
|   |-- teams/                # 团队协作、消息和共享任务
|   |-- worktree/             # Git worktree 管理
|   |-- memory/               # 记忆、会话和项目说明
|   |-- hooks/                # 生命周期 Hook
|   `-- context/              # 上下文管理
|-- tests/                    # 测试用例
|-- examples/                 # 示例配置
|-- pyproject.toml            # 项目元数据和依赖
|-- uv.lock                   # uv 锁文件
`-- MEWCODE.md                # 项目级开发说明
```

## 内置命令

交互式界面中可使用斜杠命令：

- `/help`：查看可用命令。
- `/clear`：清空当前对话显示或上下文。
- `/compact`：压缩当前会话上下文。
- `/do`：执行指定操作。
- `/mcp`：查看 MCP 状态。
- `/memory`：查看或管理记忆。
- `/permission`：查看或调整权限模式。
- `/plan`：进入计划模式。
- `/review`：进行代码审查。
- `/rewind`：回退会话。
- `/session`：管理会话。
- `/skill`：查看或加载 Skills。
- `/status`：查看当前状态。
- `/tasks`：查看后台任务。
- `/trace`：查看子 Agent 或团队任务轨迹。
- `/worktree`：管理任务工作区。

实际可用命令以运行时 `/help` 输出为准。

## 内置工具

默认基础工具：

- `ReadFile`：读取文件并返回带行号内容。
- `WriteFile`：写入文件。
- `EditFile`：编辑已有文件。
- `Bash`：执行 Shell 命令。
- `Glob`：按 glob 模式查找路径。
- `Grep`：按正则搜索文件内容。

按配置或上下文额外注册的工具包括 `ToolSearch`、`Agent`、`TeamCreate`、`TeamDelete`、`TaskCreate`、`TaskGet`、`TaskList`、`TaskUpdate`、`SendMessage`、`LoadSkill`、`EnterWorktree`、`ExitWorktree` 以及 MCP 工具。

## Skills 与 Agents

Skills 用于封装可复用工作流，内置 Skills 位于：

```text
mewcode/skills/builtins/
```

项目级和用户级扩展目录：

- `.mewcode/skills`
- `~/.mewcode/skills`

Agents 用于定义可复用子 Agent，内置 Agents 位于：

```text
mewcode/agents/builtins/
```

项目级和用户级扩展目录：

- `.mewcode/agents`
- `~/.mewcode/agents`

## 权限与安全

权限规则文件位置：

- 用户级：`~/.mewcode/permissions.yaml`
- 项目级：`.mewcode/permissions.yaml`
- 本地覆盖：`.mewcode/permissions.local.yaml`

权限系统会综合 `permission_mode`、危险命令检测、路径沙箱和规则文件判断工具调用是否允许。不要提交本地覆盖规则、API Key、会话文件、缓存或包含敏感信息的配置。

## 运行时数据

运行时状态默认位于 `.mewcode/`，常见内容包括：

- `.mewcode/debug.log`
- `.mewcode/sessions/`
- `.mewcode/plans/`
- `.mewcode/memories.md`
- `.mewcode/memory/`

这些内容通常属于本地运行状态，不应提交到远端仓库。

## 测试

运行全部测试：

```powershell
python -m pytest
```

运行指定测试文件：

```powershell
python -m pytest tests/test_agent.py
```

## 开发建议

- 修改 CLI 行为时优先查看 `mewcode/__main__.py`。
- 修改交互界面时优先查看 `mewcode/app.py`。
- 修改 Agent 执行流程时优先查看 `mewcode/agent.py`。
- 新增工具时参考 `mewcode/tools/`，并检查工具注册和权限影响。
- 新增命令时参考 `mewcode/commands/handlers/`。
- 修改配置字段时同步更新 `mewcode/config.py` 和 `mewcode/validator.py`。
- 涉及权限、文件写入、Shell 执行、上下文压缩或会话恢复的改动应补充测试。
