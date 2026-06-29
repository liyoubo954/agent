# MewCode

MewCode 是一个基于 Python 的终端 AI 编程助手。它提供交互式 TUI、一次性命令执行、文件读写、代码搜索、Shell 执行、权限控制、会话管理、记忆、Skills、MCP 工具接入、子代理和团队协作等能力，适合在本地代码仓库中辅助阅读、修改、测试和维护代码。

## 主要功能

- 终端交互界面：基于 Textual 构建，可在终端中进行连续对话和代码操作。
- 非交互模式：通过 `mewcode -p "..."` 执行一次性任务并把结果输出到标准输出。
- 多模型接入：支持 `anthropic`、`openai` 和 `openai-compat` 协议。
- 本地工具：内置文件读取、文件写入、文件编辑、内容搜索、路径匹配和 Shell 执行工具。
- 权限系统：支持多种权限模式，并可通过规则文件控制命令和文件访问行为。
- MCP 支持：可以通过 stdio 或 URL 接入外部 MCP Server，并自动注册 MCP 工具。
- Skills 机制：支持内置 Skills，也支持项目级和用户级 Skills 扩展。
- 子代理与团队协作：支持后台子代理、任务管理、消息通信、trace 跟踪和 team 模式。
- Worktree 支持：可以为任务创建隔离工作区，并复用指定目录的软链接。
- 会话与记忆：支持会话保存、压缩、回退、项目说明加载和记忆文件。

## 环境要求

- Python `>= 3.11`
- 推荐使用虚拟环境或 Conda 环境
- 至少配置一个可用的大模型 Provider

项目依赖见 [pyproject.toml](./pyproject.toml)，主要包括：

- `textual`
- `anthropic`
- `openai`
- `pyyaml`
- `pydantic`
- `mcp`
- `httpx`

## 安装

进入项目目录：

```powershell
cd E:\Agent_learning\mewcode-python
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

如果使用 `uv`：

```powershell
uv sync
```

## 配置

MewCode 启动时会按顺序读取配置：

1. `~/.mewcode/config.yaml`
2. 当前项目下的 `.mewcode/config.yaml`
3. 当前项目下的 `.mewcode/config.local.yaml`

后面的项目级配置可以覆盖或补充前面的用户级配置。`config.yaml` 通常不应该提交到 Git，因为其中可能包含 API Key。本仓库已在 `.gitignore` 中忽略 `config.yaml` 和 `.mewcode/`。

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

### 常用配置字段

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

`permission_mode` 可选值：

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

或直接使用模块方式运行：

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

在不使用终端 alternate screen 的情况下运行：

```powershell
$env:MEWCODE_NO_ALT_SCREEN = "1"
mewcode
```

## MCP 配置

仓库中提供了一个本地 MCP 配置示例：[examples/mcp-local-config.yaml](./examples/mcp-local-config.yaml)。

可将其中的 `mcp_servers` 配置合并到 `.mewcode/config.yaml`：

```yaml
mcp_servers:
  local:
    command: D:\anconda\envs\MewCode\python.exe
    args:
      - -m
      - mewcode.mcp.local_server
      - --root
      - E:\Agent_learning\mewcode-python
    env:
      MEWCODE_MCP_ROOT: E:\Agent_learning\mewcode-python
```

本地 MCP Server 入口：

```powershell
python -m mewcode.mcp.local_server --root E:\Agent_learning\mewcode-python
```

## 项目结构

```text
mewcode-python/
├── mewcode/                    # 主包
│   ├── __main__.py             # CLI 入口
│   ├── app.py                  # Textual 交互式应用
│   ├── agent.py                # Agent 主循环与工具调用流程
│   ├── client.py               # 大模型客户端适配
│   ├── config.py               # 配置加载与合并
│   ├── validator.py            # 配置校验
│   ├── commands/               # 斜杠命令
│   ├── tools/                  # 内置工具
│   ├── permissions/            # 权限检查、规则和沙箱
│   ├── mcp/                    # MCP 客户端和本地 MCP Server
│   ├── skills/                 # Skills 解析、加载和执行
│   ├── agents/                 # 子代理定义、加载、trace 和任务管理
│   ├── teams/                  # 团队协作、消息和共享任务
│   ├── worktree/               # Git worktree 管理
│   ├── memory/                 # 记忆、会话和项目说明
│   ├── hooks/                  # 生命周期 Hook
│   └── context/                # 上下文管理
├── tests/                      # 测试用例
├── examples/                   # 示例配置
├── pyproject.toml              # 项目元数据和依赖
├── uv.lock                     # uv 锁文件
└── MEWCODE.md                  # 项目内给助手读取的开发说明
```

## 内置命令

交互式界面中可以使用斜杠命令。常见命令包括：

- `/help`：查看可用命令。
- `/clear`：清空当前对话显示或上下文。
- `/compact`：压缩当前会话上下文。
- `/do`：执行指定操作。
- `/mcp`：查看 MCP 相关状态。
- `/memory`：查看或管理记忆。
- `/permission`：查看或调整权限模式。
- `/plan`：进入计划模式。
- `/review`：进行代码审查。
- `/rewind`：回退会话。
- `/session`：管理会话。
- `/skill`：查看或加载 Skills。
- `/status`：查看当前状态。
- `/tasks`：查看后台任务。
- `/trace`：查看子代理或团队任务轨迹。
- `/worktree`：管理任务工作区。

实际可用命令以运行时 `/help` 输出为准。

## 内置工具

默认注册的基础工具：

- `ReadFile`：读取文件并返回带行号内容。
- `WriteFile`：写入文件。
- `EditFile`：编辑已有文件。
- `Bash`：执行 Shell 命令。
- `Glob`：按 glob 模式查找路径。
- `Grep`：按正则搜索文件内容。

在不同配置下还会注册：

- `ToolSearch`：搜索延迟加载工具。
- `Agent`：启动子代理。
- `TeamCreate` / `TeamDelete`：创建或删除团队。
- `TaskCreate` / `TaskGet` / `TaskList` / `TaskUpdate`：团队任务管理。
- `SendMessage`：团队成员消息通信。
- `LoadSkill`：加载 Skill。
- `EnterWorktree` / `ExitWorktree`：进入或退出任务 worktree。
- MCP 工具：按 `mcp__<server>__<tool>` 形式注册。

## Skills

MewCode 会加载内置 Skills，并支持项目级和用户级 Skills：

- 项目级：`.mewcode/skills`
- 用户级：`~/.mewcode/skills`

Skill 通常包含 `SKILL.md`，用于描述触发条件、操作流程和可选工具。项目中已有内置示例位于：

```text
mewcode/skills/builtins/
```

## Agents 与团队协作

项目支持内置子代理，也支持自定义代理：

- 项目级代理：`.mewcode/agents`
- 用户级代理：`~/.mewcode/agents`
- 内置代理：`mewcode/agents/builtins`

启用 `enable_fork` 后，Agent 工具可以派生后台子代理。启用 `teammate_mode: in-process` 后，可以创建同进程团队成员，并通过共享任务和消息机制协作。

## 权限与安全

权限规则文件位置：

- 用户级：`~/.mewcode/permissions.yaml`
- 项目级：`.mewcode/permissions.yaml`
- 本地覆盖：`.mewcode/permissions.local.yaml`

权限系统会结合当前 `permission_mode`、危险命令检测、路径沙箱和规则文件判断工具调用是否允许。建议不要把本地覆盖规则和包含敏感信息的配置提交到仓库。

## 会话、记忆和项目说明

运行时会在 `.mewcode/` 下保存会话、日志和临时状态，例如：

- `.mewcode/debug.log`
- `.mewcode/sessions/`
- `.mewcode/plans/`
- `.mewcode/memories.md`
- `.mewcode/memory/`

项目说明文件可放在：

- 当前项目：`.mewcode/MEWCODE.md`
- 用户目录：`~/.mewcode/MEWCODE.md`

仓库根目录的 [MEWCODE.md](./MEWCODE.md) 是给开发者和助手阅读的项目说明。

## 测试

运行全部测试：

```powershell
pytest
```

或：

```powershell
python -m pytest
```

运行单个测试文件：

```powershell
python -m pytest tests/test_agent.py
```

## 开发建议

- 修改 CLI 行为时优先查看 `mewcode/__main__.py`。
- 修改交互界面时优先查看 `mewcode/app.py`。
- 修改 Agent 执行流程时优先查看 `mewcode/agent.py`。
- 新增工具时参考 `mewcode/tools/` 下已有工具，并在注册逻辑中加入。
- 新增命令时参考 `mewcode/commands/handlers/`。
- 修改配置字段时同步更新 `mewcode/config.py` 和 `mewcode/validator.py`。
- 涉及权限、文件写入、Shell 执行的改动应补充测试。

## Git 忽略说明

当前 `.gitignore` 会忽略以下常见本地文件：

- `config.yaml`
- `.mewcode/`
- `.venv/`
- `.venvs/`
- `.pytest_cache/`
- `.tmp/`
- `.uv-cache/`
- `__pycache__/`
- `*.pyc`
- `.idea/`
- `.vscode/`
- 构建产物目录

这样可以避免把 API Key、本地会话、缓存、虚拟环境和 IDE 配置提交到远端。

## 当前状态

该项目已推送到 GitHub 仓库：

```text
https://github.com/liyoubo954/agent
```
