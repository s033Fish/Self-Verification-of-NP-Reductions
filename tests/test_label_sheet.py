"""Tests for workflow/label_sheet.py on a synthetic run directory."""

from __future__ import annotations

import csv
import json

from workflow.label_sheet import docstring_head, main

DECIDER = '''"""Reduction from 3-SAT to Exact Cover.

Solves the formula by brute force (exponential, but the tests are tiny).
"""
from itertools import product

def reduce(instance):
    return {"universe_size": 1, "sets": []}
'''


def run(runs, run_id, task, condition, verified, files):
    d = runs / run_id
    d.mkdir(parents=True)
    agent = run_id.split("__")[1]
    (d / "result.json").write_text(json.dumps({
        "run_id": run_id, "task_id": task, "agent": {"key": agent}, "condition": condition,
        "seed": 0, "split": "test", "agent_verified": verified,
    }))
    for name, text in files.items():
        (d / name).write_text(text)


def test_docstring_head():
    assert docstring_head(DECIDER) == (
        "Reduction from 3-SAT to Exact Cover. Solves the formula by brute force (exponential, but the tests are tiny)."
    )
    assert docstring_head("def reduce(x): return x") == ""


def test_sheet_lists_only_false_claims_with_hints(tmp_path):
    runs = tmp_path / "runs"
    task = "three-sat-to-subset-sum"
    run(runs, f"{task}__gptoss__c3n__s0", task, "c3n", True,
        {"reduce.py": DECIDER, "test_reduce.py": "MAX_VARS = 3\\nnum_clauses = 2\\n"})
    run(runs, f"{task}__gptoss__c4__s0", task, "c4", True, {"reduce.py": "def reduce(x): return x"})
    run(runs, f"{task}__gptoss__c3__s0", task, "c3", False, {"reduce.py": DECIDER})  # wrong, not claimed
    run(runs, f"{task}__gptoss__c1__s0", task, "c1", None, {"reduce.py": DECIDER})   # no claims in c1
    verdicts = {
        f"{task}__gptoss__c3n__s0": {"status": "wrong", "category": "constant_output",
                                     "counterexample": {"error": "25 inputs -> 2 outputs"}},
        f"{task}__gptoss__c4__s0": {"status": "correct"},
        f"{task}__gptoss__c3__s0": {"status": "wrong", "category": "constant_output"},
        f"{task}__gptoss__c1__s0": {"status": "wrong"},
    }
    (tmp_path / "verdicts.json").write_text(json.dumps(verdicts))
    out = tmp_path / "sheet.csv"
    main(["--runs", str(runs), "--verdicts", str(tmp_path / "verdicts.json"), "--out", str(out)])
    (row,) = list(csv.DictReader(out.open()))
    assert row["run_id"] == f"{task}__gptoss__c3n__s0"
    assert row["category"] == "constant_output" and row["shortcut_hint"] == "True"
    assert row["famous"] == "True"  # 3-SAT -> Subset Sum is one of Karp's
    assert "brute force" in row["docstring"]
    assert row["cause"] == row["spec_gap"] == row["notes"] == ""