from __future__ import annotations

from pathlib import Path

from mewcode.memory.instructions import load_instructions
from mewcode.skills.loader import SkillLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_harness_is_loaded_from_mewcode_instructions() -> None:
    instructions = load_instructions(str(PROJECT_ROOT))

    assert "MewCode Harness" in instructions
    assert "D:\\anconda\\envs\\MewCode\\python.exe" in instructions
    assert "不打印" in instructions
    assert "Skill 选择原则" in instructions


def test_project_skills_are_discoverable_and_actionable() -> None:
    loader = SkillLoader(str(PROJECT_ROOT))
    skills = loader.load_all()

    expected = {
        "agent-core",
        "tool-protocol",
        "context-memory",
        "feature-implementation",
        "bug-fix",
        "test",
        "review",
        "security-permission",
        "extension-integration",
        "multi-agent",
    }

    assert expected.issubset(skills)
    for name in expected:
        assert skills[name].is_directory is True
        assert skills[name].source_path is not None
        assert ".mewcode" in str(skills[name].source_path)

    assert "mewcode/agent.py" in skills["agent-core"].prompt_body
    assert "ToolResult" in skills["tool-protocol"].prompt_body
    assert "Function Calling" in skills["context-memory"].prompt_body
    assert "D:\\anconda\\envs\\MewCode\\python.exe" in skills["test"].prompt_body
    assert "tests\\verify_subagent.py" in skills["multi-agent"].prompt_body
    assert "Never print API keys" in skills["security-permission"].prompt_body
    assert skills["review"].mode == "fork"
    assert "actionable" in skills["review"].prompt_body
