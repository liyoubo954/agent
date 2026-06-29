# MewCode 项目开发说明

@include .mewcode/harness.md

## 项目事实

- 本项目是一个 Python 终端 AI 编程助手。
- 主包：`mewcode`。
- CLI 入口：`python -m mewcode`。
- 安装后的命令：`mewcode`。
- 推荐测试命令：`python -m pytest`。

## 架构边界

改动应尽量保持在现有架构内：

- Agent 主循环与模型协议。
- 工具注册、工具执行和工具结果处理。
- 上下文管理、压缩、会话恢复和记忆。
- 权限模式、规则引擎、危险命令检测和路径沙箱。
- Skills、MCP、子 Agent、团队协作、Hooks、Commands 和 Worktree。

不要为了追随其它工具的功能形态而引入无关能力。新增功能应能在现有模块、配置、工具或测试中找到合理位置。

## 安全要求

- 不要打印、提交或暴露 API Key、Token、凭据和私有本地路径。
- 不要提交 `.mewcode/config.yaml`、`.mewcode/config.local.yaml`、会话文件、缓存和本地覆盖规则。
- 涉及 Shell、文件写入、权限、沙箱、MCP 或外部命令的改动必须优先考虑误用风险。

## 开发约定

- 优先复用现有模块边界和命名风格。
- 修改配置行为时，同步检查 `mewcode/config.py` 和 `mewcode/validator.py`。
- 修改命令行为时，同步检查 `mewcode/commands/handlers/` 和 `/help` 输出。
- 修改工具行为时，同步检查 `mewcode/tools/__init__.py`、工具 schema 和权限影响。
- 修改 Agent 行为时，补充或更新 `tests/` 下的聚焦测试。
- 修改 Skills 或 Agents 文档时，确保 frontmatter 可被解析器加载。
