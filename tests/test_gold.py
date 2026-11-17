"""Gold reductions validate the verifier, and the verifier validates them.

  benchmark/gold/<task_id>.py                 must be judged correct
  benchmark/gold/broken/<task_id>__<name>.py  must be judged wrong

Stubs that still raise NotImplementedError are skipped, so this file can be
run while the gold reductions are being written. To see a single verdict in
full:

  uv run python -m benchmark.verify --reduce benchmark/gold/<task_id>.py --task <task_id>

Run with: uv run pytest tests/test_gold.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from benchmark.make_task import load_pairs, write_task
from benchmark.problems import PROBLEMS
from benchmark.verify import Settings, verify_reduction

GOLD = Path(__file__).resolve().parents[1] / "benchmark" / "gold"
PAIRS = {pair.task_id: pair for pair in load_pairs()}
SETTINGS = Settings()  # the real settings: gold must pass what agents face

GOLD_FILES = sorted(GOLD.glob("*.py"))
BROKEN_FILES = sorted((GOLD / "broken").glob("*.py"))


@pytest.fixture(scope="module")
def tasks(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("tasks")
    for pair in PAIRS.values():
        write_task(pair, root)
    return root


def verdict_for(reduce_file: Path, task_id: str, tasks: Path):
    if task_id not in PAIRS:
        pytest.fail(f"{reduce_file.name}: {task_id!r} is not a task in pairs.json")
    pair = PAIRS[task_id]
    return verify_reduction(
        reduce_file,
        tasks / task_id / "inputs" / "problems.py",
        PROBLEMS[pair.source],
        PROBLEMS[pair.target],
        SETTINGS,
        seed=task_id,
    )


def is_stub(path: Path) -> bool:
    return "raise NotImplementedError" in path.read_text()


@pytest.mark.parametrize("path", GOLD_FILES, ids=lambda p: p.stem)
def test_gold_reduction_is_correct(path, tasks):
    if is_stub(path):
        pytest.skip("not written yet")
    verdict = verdict_for(path, path.stem, tasks)
    assert verdict.status == "correct", (
        f"{verdict.status} ({verdict.category}): {verdict.counterexample}"
    )


@pytest.mark.parametrize("path", BROKEN_FILES, ids=lambda p: p.stem)
def test_broken_reduction_is_caught(path, tasks):
    task_id = path.stem.split("__")[0]
    verdict = verdict_for(path, task_id, tasks)
    assert verdict.status == "wrong", (
        f"the verifier missed this bug: status {verdict.status}"
    )


def test_every_dev_task_has_a_gold_file():
    dev = {task_id for task_id, pair in PAIRS.items() if pair.split == "dev"}
    present = {path.stem for path in GOLD_FILES}
    assert dev <= present, f"missing gold files: {sorted(dev - present)}"