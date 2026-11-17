"""Tests for benchmark/make_task.py. Run with: uv run pytest"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from benchmark.make_task import (
    bundle,
    check_bundle,
    dependency_order,
    load_bundle,
    load_pairs,
    module_name,
    write_task,
)
from benchmark.problems import PROBLEMS
from workflow.tasks import load_tasks

PAIRS = load_pairs()


def test_pairs_file_has_the_planned_split():
    assert len(PAIRS) == 40
    assert sum(p.famous for p in PAIRS) == 20
    assert sum(p.split == "dev" for p in PAIRS) == 8
    assert len({p.task_id for p in PAIRS}) == 40


def test_every_problem_appears_in_some_pair():
    used = {p.source for p in PAIRS} | {p.target for p in PAIRS}
    assert used == set(PROBLEMS)


def test_dependencies_come_before_their_users():
    order = dependency_order(["nae_three_sat"])
    assert order.index("base") < order.index("three_sat") < order.index("cnf_common")
    assert order[-1] == "nae_three_sat"


@pytest.mark.parametrize("pair", PAIRS, ids=lambda p: p.task_id)
def test_every_pair_bundles_and_matches_the_library(pair, tmp_path):
    task_dir = write_task(pair, tmp_path)  # write_task also runs check_bundle
    text = (task_dir / "inputs" / "problems.py").read_text()
    assert "from ." not in text  # no package-relative imports remain
    assert text.count("from __future__") == 1
    assert "exhaustive_scale" not in text  # the verifier's test scale stays hidden


def test_bundle_runs_without_the_benchmark_package(tmp_path):
    """Agents run problems.py in a bare sandbox: it must need only the
    standard library. -I isolates Python from this repo and its packages."""
    source, target = PROBLEMS["three_sat"], PROBLEMS["subset_sum"]
    (tmp_path / "problems.py").write_text(bundle(source, target))
    script = (
        "import random, problems\n"
        "x = problems.SOURCE.random_instance(random.Random(0), 4)\n"
        "problems.SOURCE.validate(x)\n"
        "print(problems.SOURCE.name, problems.TARGET.name, problems.SOURCE.is_yes(x))\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, '.')\n{script}"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.startswith("3-SAT Subset Sum")


def test_written_tasks_pass_the_workflow_validator(tmp_path):
    for pair in PAIRS[:5]:
        write_task(pair, tmp_path)
    loaded = load_tasks(tmp_path)
    assert {task.task_id for task, _ in loaded} == {p.task_id for p in PAIRS[:5]}
    task, _ = loaded[0]
    assert task.source_problem in task.instructions


def test_bundle_contains_both_docstrings(tmp_path):
    source, target = PROBLEMS["vertex_cover"], PROBLEMS["dominating_set"]
    path = tmp_path / "problems.py"
    path.write_text(bundle(source, target))
    module = load_bundle(path)
    assert module.SOURCE.__doc__ == source.__doc__
    assert module.TARGET.__doc__ == target.__doc__
    check_bundle(path, source, target)
    assert module_name(target) == "dominating_set"


def test_nosolver_bundle_has_specs_and_validate_only(tmp_path):
    """The no-solver setting must leave the agent nothing to solve with."""
    from benchmark.make_task import FORBIDDEN_IN_NOSOLVER, NOSOLVER_FILE

    pair = next(p for p in PAIRS if p.task_id == "three-sat-to-three-coloring")
    task_dir = write_task(pair, tmp_path)  # also runs check_nosolver_bundle
    text = (task_dir / "inputs" / NOSOLVER_FILE).read_text()
    assert not [name for name in FORBIDDEN_IN_NOSOLVER if name in text]
    script = (
        "import problems\n"
        "problems.SOURCE.validate({'num_vars': 3, 'clauses': [[1, -2, 3]]})\n"
        "problems.TARGET.validate({'n': 2, 'edges': [[0, 1]]})\n"
        "assert not hasattr(problems.SOURCE, 'is_yes')\n"
        "assert not hasattr(problems.TARGET, 'random_instance')\n"
        "try:\n"
        "    problems.TARGET.validate({'n': 2, 'edges': [[0, 0]]})\n"
        "    raise SystemExit('self-loop accepted')\n"
        "except problems.InvalidInstance:\n"
        "    print('ok')\n"
    )
    (tmp_path / "problems.py").write_text(text)
    result = subprocess.run(
        [sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, '.')\n{script}"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "ok"


def test_task_json_lists_only_the_agent_visible_file(tmp_path):
    pair = PAIRS[0]
    task_dir = write_task(pair, tmp_path)
    descriptor = json.loads((task_dir / "task.json").read_text())
    assert [item["name"] for item in descriptor["inputs"]] == ["problems.py"]