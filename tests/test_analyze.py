"""Tests for workflow/analyze.py on small synthetic runs."""

from __future__ import annotations

import json
import math
import random

import pytest

from workflow.analyze import (
    cluster_ci,
    fp_rate,
    holm,
    main,
    permutation_p,
    mcnemar_exact,
    outcomes,
    paired_table,
)

TASKS = ["sat-to-three-sat", "clique-to-sat"]  # one famous, one less common


def record(task, agent, condition, seed, verified=None, sample=None):
    run_id = f"{task}__{agent}__{condition}__s{seed}" + (f"__k{sample}" if sample is not None else "")
    return {
        "run_id": run_id, "task_id": task, "agent": {"key": agent}, "condition": condition,
        "seed": seed, "sample": sample, "split": "test", "agent_verified": verified,
        "usage": [{"prompt_tokens": 100, "completion_tokens": 10}],
    }


def test_mcnemar_exact():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(5, 0) == pytest.approx(2 / 32)
    assert mcnemar_exact(0, 10) == pytest.approx(2 / 1024)
    assert mcnemar_exact(3, 3) == 1.0


def test_cluster_ci_is_degenerate_for_constant_data():
    rows = [{"task": t, "correct": True} for t in TASKS for _ in range(3)]
    low, high = cluster_ci(rows, lambda r: sum(x["correct"] for x in r) / len(r), random.Random(0))
    assert low == high == 1.0


def test_cluster_ci_resamples_whole_tasks():
    # Task A always right, task B always wrong: every draw is 0, 1/2 or 1.
    rows = [{"task": "a", "correct": True}] * 3 + [{"task": "b", "correct": False}] * 3
    stat = lambda r: sum(x["correct"] for x in r) / len(r)  # noqa: E731
    low, high = cluster_ci(rows, stat, random.Random(0), samples=500)
    assert (low, high) == (0.0, 1.0)


def test_outcomes_collapse_pass_at_k_and_mark_false_claims():
    records = [record(TASKS[0], "a", "c2", 0, sample=k) for k in range(3)]
    records += [record(TASKS[0], "a", "c3n", 0, verified=True), record(TASKS[1], "a", "c3n", 0, verified=True)]
    verdicts = {r["run_id"]: {"status": "wrong"} for r in records}
    verdicts[records[1]["run_id"]] = {"status": "correct"}  # one of three c2 samples
    verdicts[records[4]["run_id"]] = {"status": "inconclusive"}
    rows = outcomes(records, verdicts)
    by_condition = {r["condition"]: r for r in rows}
    assert len(rows) == 2  # c2 merged; the inconclusive c3n run dropped
    assert by_condition["c2"]["correct"] is True and by_condition["c2"]["tokens"] == 330
    assert by_condition["c3n"]["false_claim"] is True
    assert by_condition["c2"]["false_claim"] is None
    assert fp_rate([by_condition["c3n"]]) == 1.0


def test_paired_comparison_counts_discordant_pairs():
    records, verdicts = [], {}
    for task in TASKS:
        for seed in range(3):
            for condition in ("c3n", "c4"):
                r = record(task, "a", condition, seed, verified=True)
                records.append(r)
                # c3n: wrong and verified (false claim) on every run; c4 only on seed 0.
                wrong = condition == "c3n" or seed == 0
                verdicts[r["run_id"]] = {"status": "wrong" if wrong else "correct"}
    rows = outcomes(records, verdicts)
    (row,) = [p for p in paired_table(rows, random.Random(0))
              if p["a"] == "c4" and p["b"] == "c3n" and p["outcome"] == "false_claim"]
    assert row["pairs"] == 6
    assert (row["only_a"], row["only_b"]) == (0, 4)
    assert row["difference"] == pytest.approx(-4 / 6)
    assert row["p_mcnemar"] == pytest.approx(2 / 16)


def test_end_to_end_writes_tables(tmp_path):
    runs = tmp_path / "runs"
    verdicts = {}
    for task in TASKS:
        for seed in range(3):
            for condition in ("c1", "c3n", "c5", "c5x"):
                r = record(task, "a", condition, seed, verified=condition != "c1")
                (runs / r["run_id"]).mkdir(parents=True)
                (runs / r["run_id"] / "result.json").write_text(json.dumps(r))
                verdicts[r["run_id"]] = {"status": "correct" if seed else "wrong"}
    (tmp_path / "verdicts.json").write_text(json.dumps(verdicts))
    main(["--runs", str(runs), "--verdicts", str(tmp_path / "verdicts.json"), "--out", str(tmp_path / "out")])
    text = (tmp_path / "out" / "analysis.md").read_text()
    assert "## Paired comparisons" in text and "c5x vs c5" in text
    data = json.loads((tmp_path / "out" / "analysis.json").read_text())
    c3n = next(e for e in data["main"] if e["condition"] == "c3n")
    assert c3n["runs"] == 6 and math.isclose(c3n["fp_rate"], 2 / 6)


def test_holm():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5]) == [0.5]
    assert holm([0.9, 0.9]) == [1.0, 1.0]


def test_permutation_p_separates_a_real_difference_from_none():
    tasks = [(f"t{i}", i < 8) for i in range(16)]
    stat = lambda r: sum(x["correct"] for x in r) / len(r)  # noqa: E731
    different = [{"task": t, "famous": f, "correct": f} for t, f in tasks for _ in range(3)]
    same = [{"task": t, "famous": f, "correct": i % 2 == 0} for i, (t, f) in enumerate(tasks) for _ in range(3)]
    assert permutation_p(different, stat, random.Random(0), samples=500) < 0.01
    assert permutation_p(same, stat, random.Random(0), samples=500) > 0.5