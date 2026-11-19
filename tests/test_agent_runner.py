"""Tests for the parts of the agent runner that run without Modal.

Run with: uv run pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "infrastructure"))
from agent_runner import (  # noqa: E402
    MAX_ORACLE_ROUNDS,
    oracle_feedback,
    recover_tool_call,
    run_oracle_process,
    runs_code,
    task_prompt,
    review_prompt,
)

REPO = Path(__file__).resolve().parents[1]


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


@pytest.mark.parametrize("condition", ["c1", "c3", "c3n", "c4", "c5"])
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


# --- c4: the oracle ---------------------------------------------------------------


def test_c4_prompt_explains_the_oracle_without_solvers():
    task = {"task_id": "t", "instructions": "do it", "inputs": [], "solvers_provided": False}
    prompt = task_prompt(task, "c4", "/tmp/w")
    assert "oracle" in prompt and "counterexample" in prompt
    assert f"at most {MAX_ORACLE_ROUNDS} times" in prompt
    assert "NO solvers" in prompt


@pytest.mark.parametrize("status", ["correct", "inconclusive", "oracle_error"])
def test_only_wrong_verdicts_block_the_submit(status):
    assert oracle_feedback({"status": status}, 1) is None


def test_wrong_answer_feedback_shows_the_counterexample():
    verdict = {
        "status": "wrong",
        "category": "wrong_answer_no_to_yes",
        "counterexample": {
            "category": "wrong_answer_no_to_yes",
            "source_instance": {"n": 2, "edges": [[0, 1]], "k": 2},
            "expected": False,
            "got": True,
            "target_instance": {"n": 2, "edges": [[0, 1]], "k": 1},
        },
    }
    text = oracle_feedback(verdict, 2)
    assert f"round 2 of {MAX_ORACLE_ROUNDS}" in text
    assert "NOT submitted" in text
    assert '{"n":2,"edges":[[0,1]],"k":2}' in text
    assert "Its answer is no" in text and "whose answer is yes" in text
    assert "verdict.json has been cleared" in text


@pytest.mark.parametrize(
    "category, phrase",
    [
        ("crash", "raised an error"),
        ("timeout", "took too long"),
        ("malformed_output", "invalid target instance"),
        ("solver_call", "brute-force solver"),
        ("blowup", "not polynomial"),
        ("constant_output", "decides the answer itself"),
        ("superpolynomial_time", "faster than any polynomial"),
        ("no_reduce_file", "not found"),
    ],
)
def test_feedback_names_each_failure(category, phrase):
    verdict = {
        "status": "wrong",
        "category": category,
        "counterexample": {"category": category, "source_instance": {"n": 1}, "error": "boom"},
    }
    assert phrase in oracle_feedback(verdict, 1)


def test_long_instances_are_truncated():
    huge = {"numbers": list(range(5000)), "target": 1}
    verdict = {
        "status": "wrong",
        "category": "crash",
        "counterexample": {"category": "crash", "source_instance": huge, "error": "x"},
    }
    text = oracle_feedback(verdict, 1)
    assert "(truncated)" in text and len(text) < 3000


DECIDER = """
from itertools import product

def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    sat = any(
        all(any(values[abs(l) - 1] == (l > 0) for l in clause) for clause in clauses)
        for values in product((False, True), repeat=m)
    )
    return {"universe_size": 1, "sets": [[0]] if sat else []}
"""


@pytest.fixture(scope="module")
def exact_cover_task(tmp_path_factory):
    from benchmark.make_task import Pair, write_task

    root = tmp_path_factory.mktemp("tasks")
    write_task(Pair("three_sat", "exact_cover", famous=False, split="dev"), root)
    return root / "three-sat-to-exact-cover"


def test_oracle_process_catches_a_decider(exact_cover_task):
    from benchmark.problems import PROBLEMS

    request = {
        "reduce_py": DECIDER,
        "problems_py": (exact_cover_task / "inputs" / "problems_nosolver.py").read_bytes(),
        "source": PROBLEMS["three_sat"].name,
        "target": PROBLEMS["exact_cover"].name,
        "seed": "three-sat-to-exact-cover:oracle",
    }
    verdict = run_oracle_process(request, package_root=str(REPO))
    assert verdict["status"] == "wrong", verdict
    assert verdict["category"] == "constant_output"
    assert "decides the answer itself" in oracle_feedback(verdict, 1)


def test_oracle_process_reports_its_own_failures(exact_cover_task):
    request = {
        "reduce_py": DECIDER,
        "problems_py": b"",
        "source": "no such problem",
        "target": "no such problem",
        "seed": "s",
    }
    verdict = run_oracle_process(request, package_root=str(REPO))
    assert verdict["status"] == "oracle_error"
    assert oracle_feedback(verdict, 1) is None  # the submit goes through


# --- c5: the independent tester ---------------------------------------------------


def test_c5_writer_gets_the_c3n_instruction():
    task = {"task_id": "t", "instructions": "do it", "inputs": [], "solvers_provided": False}
    assert task_prompt(task, "c5", "/w") == task_prompt(task, "c3n", "/w")


def test_tester_prompt_has_the_definitions_but_not_the_request():
    task = {"task_id": "t", "instructions": "SECRET WRITER REQUEST", "spec": "SOURCE = X\nTARGET = Y"}
    prompt = review_prompt(task, "/review")
    assert "SOURCE = X" in prompt and "/review" in prompt
    assert "SECRET WRITER REQUEST" not in prompt
    assert "do not change reduce.py" in prompt
    assert "polynomial time" in prompt and "NO solvers" in prompt
    assert prompt.rstrip().endswith("echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")