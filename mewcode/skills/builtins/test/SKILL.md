---
name: test
description: 运行项目测试并分析结果
allowedTools:
  - Bash
  - ReadFile
  - Grep
  - Glob
mode: inline
---

# 任务

你需要运行项目的测试套件并分析结果。

## 步骤

1. 检测项目类型，按优先级查找：
   - `pyproject.toml` 或 `setup.py`：Python 项目，优先使用 `python -m pytest`
   - `go.mod`：Go 项目，使用 `go test ./...`
   - `package.json`：Node.js 项目，使用 `npm test`
   - `Cargo.toml`：Rust 项目，使用 `cargo test`
2. 运行对应测试命令，捕获完整输出。
3. 分析测试结果：
   - 如果全部通过，报告通过数量和覆盖率信息，如果可用。
   - 如果存在失败，区分代码问题和测试问题。
4. 对每个失败测试说明：
   - 失败位置，包括文件名和测试名。
   - 失败类型，是代码 bug、测试 bug 还是环境问题。
   - 具体修复建议。
5. 如果全部通过，检查是否存在明显缺失的测试场景：
   - 边界值。
   - 错误路径。
   - 空输入。
   - 极端值。

$ARGUMENTS
