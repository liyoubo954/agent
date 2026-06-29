---
name: commit
description: 基于当前仓库变更创建清晰、安全、可审查的 Git commit。适用于用户要求提交、生成提交信息、暂存变更、总结 diff、创建检查点等场景。会检查 git 状态和 diff，避免提交密钥、本地配置、缓存和无关文件，并生成规范的提交信息。
allowedTools:
  - Bash
  - ReadFile
  - Grep
mode: inline
---

# 提交助手

创建一个聚焦、可审查、符合用户意图和实际 diff 的提交。

## 流程

1. 检查仓库状态。
   - 运行 `git status --short --branch`。
   - 根据需要运行 `git diff --stat`、`git diff`、`git diff --staged`。
2. 确定提交范围。
   - 只包含与用户请求相关的文件。
   - 保留无关本地改动，不要顺手提交。
   - 不要暂存密钥、凭据、本地配置、缓存、虚拟环境或生成噪声。
3. 判断提交类型。
   - `feat`：新增功能。
   - `fix`：修复缺陷。
   - `docs`：文档变更。
   - `test`：测试变更。
   - `refactor`：不改变行为的重构。
   - `chore`：维护、工具、元数据或依赖类变更。
4. 编写提交信息。
   - 优先使用 `type(scope): summary`。
   - summary 使用英文，控制在 72 个字符以内。
   - 只有当原因或风险无法从 diff 看出时，才添加提交正文。
5. 谨慎暂存。
   - 优先显式指定文件路径。
   - 只有在确认 diff 完全同属一个范围时，才使用宽泛暂存。
6. 创建提交并报告结果。
   - 说明提交 hash 和 message。
   - 如有故意保留的未提交文件，需要明确说明。

## 安全要求

- 如果 diff 中出现明显密钥、私有路径或敏感配置，停止并报告。
- 如果仓库存在混杂改动导致提交范围不明确，先向用户说明。
- 不要 amend、rebase、reset、force-push 或改写历史，除非用户明确要求。

$ARGUMENTS
