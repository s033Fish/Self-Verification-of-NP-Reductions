"""Tests for the parts of the agent runner that run without Modal.

Run with: uv run pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "infrastructure"))
from agent_runner import recover_tool_call, runs_code, task_prompt  # noqa: E402


@pytest.mark.parametrize(
    "command",
    [
        "python test_reduce.py",
        "python3 -c 'print(1)'",
        "cd /tmp && python x.py",
        "ls; python3.12 run.py",
        "pytest -q",
        "pip install numpy",
        "cat <<'EOF' > t.py\nprint(1)\nEOF\npython t.py",
        "echo hi | python -",
    ],
)
def test_running_code_is_detected(command):
    assert runs_code(command)


@pytest.mark.parametrize(
    "command",
    [
        "cat problems.py",
        "grep -n 'def is_yes' problems.py",
        "cat <<'EOF' > reduce.py\n# a python reduction\npython = 3\ndef reduce(x):\n    return x\nEOF",
        "cat <<EOF > reduce.py\nimport json\nEOF",
        "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
        "sed -n '1,40p' problems.py",
    ],
)
def test_reading_and_writing_are_allowed(command):
    assert not runs_code(command)


def test_prompt_names_the_workspace_and_includes_the_spec():
    task = {"task_id": "t", "instructions": "do it", "inputs": [{"name": "problems.py"}],
            "spec": "SOURCE = A\nYes iff ..."}
    prompt = task_prompt(task, "c1", "/tmp/reduction-abc")
    assert "WORKING DIRECTORY: /tmp/reduction-abc" in prompt
    assert "SOURCE = A" in prompt
    assert "do not run, execute or test any code" in prompt


def test_unknown_condition_is_rejected():
    with pytest.raises(NotImplementedError):
        task_prompt({"task_id": "t", "instructions": "x"}, "c9")


def test_nosolver_prompt_says_there_are_no_solvers():
    task = {"task_id": "t", "instructions": "do it", "inputs": [{"name": "problems.py"}],
            "spec": "SOURCE = A", "solvers_provided": False}
    prompt = task_prompt(task, "c3n", "/tmp/w")
    assert "NO solvers" in prompt
    assert "write your own brute-force solvers" in prompt
    assert "is_yes(instance)" not in prompt


def test_solver_prompt_mentions_the_solvers():
    task = {"task_id": "t", "instructions": "do it", "inputs": [{"name": "problems.py"}],
            "spec": "SOURCE = A", "solvers_provided": True}
    prompt = task_prompt(task, "c3", "/tmp/w")
    assert "is_yes(instance)" in prompt
    assert "NO solvers" not in prompt


@pytest.mark.parametrize("condition", ["c1", "c3", "c3n"])
def test_every_prompt_says_how_to_finish(condition):
    task = {"task_id": "t", "instructions": "do it", "inputs": [{"name": "problems.py"}]}
    prompt = task_prompt(task, condition, "/tmp/w")
    assert prompt.rstrip().endswith("echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")


@pytest.mark.parametrize(
    "content, command",
    [
        ('{"command": "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"}',
         "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"),
        ('{\n  "command": "python test_reduce.py"\n}', "python test_reduce.py"),
        ("echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\n", "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"),
        ("All tests pass. The reduction is in reduce.py.", None),
        ('{"command": "ls", "cwd": "/tmp"}', None),
        ('{"command": 3}', None),
        ("```bash\nls\n```", None),
        ("ls -la", None),
        ("", None),
    ],
    ids=["json-submit", "json-other", "bare-submit", "prose", "extra-key", "not-str",
         "code-block", "bare-other", "empty"],
)
def test_recover_tool_call(content, command):
    assert recover_tool_call({"role": "assistant", "content": content}) == command


def test_real_tool_calls_are_left_alone():
    message = {"content": '{"command": "ls"}', "tool_calls": [{"id": "x"}]}
    assert recover_tool_call(message) is None