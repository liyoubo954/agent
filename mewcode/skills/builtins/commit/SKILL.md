---
name: commit
description: 分析 git diff 并生成规范的 commit
allowedTools:
  - Bash
  - ReadFile
  - Grep
mode: inline
---

# 任务

你需要帮助用户创建一个清晰、可审查的 Git commit。

## 步骤

1. 运行 `git status` 查看当前变更状态。
2. 运行 `git diff` 和 `git diff --staged` 查看具体变更内容。
3. 分析变更，确定 commit 类型和范围：
   - `feat`：新功能。
   - `fix`：修复 bug。
   - `docs`：文档变更。
   - `refactor`：重构。
   - `test`：测试。
   - `chore`：构建、工具或维护变更。
4. 生成 commit message，格式为 `type(scope): description`。
5. 逐个添加相关文件，不要添加 `.env`、credentials、密钥、缓存或本地配置文件。
6. 执行 `git commit -m "生成的 message"`。
7. 如果用户提供了额外说明，将其纳入 commit message。
8. 如果变更覆盖超过 10 个文件，建议拆分为多个 commit，除非用户明确要求一次提交。

## 注意事项

- 不要默认使用 `git add -A` 或 `git add .`，优先逐个添加相关文件。
- commit message 使用英文。
- description 不超过 72 个字符。
- 提交前确认工作区中没有误加入敏感文件。

$ARGUMENTS
