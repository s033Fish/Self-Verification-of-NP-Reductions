"""Labeling sheet for the failure and spec-gap analysis.

    uv run python -m workflow.label_sheet                  # test split -> analysis/false_claims.csv

One row per FALSE CLAIM: a run whose verdict.json says verified but which the
hidden verifier judged wrong (c3, c3n, c4, c5, c5x; for c5/c5x the claim is the
tester's). Open the CSV in a spreadsheet and fill the three empty columns:

  cause      what is wrong with reduce.py:
               shortcut     - brute force / decides the instance (constant_output,
                              superpolynomial_time, solver_call, many blowups)
               blowup       - polynomial idea, exponential output
               gadget       - a construction that is wrong on some instances
               iff          - correct in one direction only
               edge_case    - wrong on k < 0, empty input, out-of-range target...
               encoding     - wrong format / indexing (0- vs 1-based, etc.)
               other
  spec_gap   which part of the full claim the agent's CHECK left out (can be
             several, separated by ;): poly_time, large_instances, no_instances,
             edge_cases, none (it checked the right thing and still missed)
  notes      anything worth quoting in the paper

The pre-filled columns are hints, not labels: the verifier's category and
error, the reduce.py docstring's first lines, whether reduce.py or the tests
mention brute force or running time, and the size settings the tests used.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from benchmark.make_task import load_pairs
from workflow.score import VERIFYING_CONDITIONS, load_runs

REPO = Path(__file__).resolve().parents[1]
SHORTCUT_CATEGORIES = {"constant_output", "superpolynomial_time", "solver_call"}
SHORTCUT_WORDS = re.compile(r"brute[- ]?force|itertools\.product|exponential|2\s*\*\*\s*\w+|1\s*<<\s*\w+", re.I)
TIMING_WORDS = re.compile(r"perf_counter|time\.time\(|timeit|polynomial", re.I)
SIZE_SETTINGS = re.compile(r"\b(max_\w+|num_\w+|n_\w+|size\w*|scale\w*)\s*[:=]\s*(?:int\s*=\s*)?(\d+)")
COLUMNS = (
    "run_id", "agent", "condition", "task", "famous", "seed", "category", "error",
    "shortcut_hint", "tests_time_hint", "test_size_settings", "docstring",
    "counterexample", "cause", "spec_gap", "notes",
)


def _read(path: Path) -> str:
    return path.read_text(errors="replace") if path.is_file() else ""


def docstring_head(code: str, lines: int = 4) -> str:
    match = re.search(r'^\s*[rRbB]?("""|\'\'\')(.*?)\1', code, re.S)
    text = match.group(2) if match else ""
    return " ".join(line.strip() for line in text.strip().splitlines()[:lines] if line.strip())


def row_for(record: dict[str, Any], verdict: dict[str, Any], run_dir: Path, famous: dict[str, bool]) -> dict[str, Any]:
    reduce_code = _read(run_dir / "reduce.py")
    tests = _read(run_dir / "test_reduce.py")
    example = verdict.get("counterexample") or {}
    category = verdict.get("category") or example.get("category") or ""
    settings = sorted({f"{k}={v}" for k, v in SIZE_SETTINGS.findall(tests)})[:8]
    return {
        "run_id": record["run_id"],
        "agent": record["agent"]["key"],
        "condition": record["condition"],
        "task": record["task_id"],
        "famous": famous.get(record["task_id"]),
        "seed": record.get("seed"),
        "category": category,
        "error": str(example.get("error") or "")[:200],
        "shortcut_hint": category in SHORTCUT_CATEGORIES or bool(SHORTCUT_WORDS.search(reduce_code)),
        "tests_time_hint": bool(TIMING_WORDS.search(tests)),
        "test_size_settings": "; ".join(settings),
        "docstring": docstring_head(reduce_code)[:400],
        "counterexample": json.dumps(example.get("source_instance"))[:200] if example.get("source_instance") is not None else "",
        "cause": "", "spec_gap": "", "notes": "",
    }


def false_claims(runs: Path, verdicts: dict[str, Any], split: str) -> list[dict[str, Any]]:
    famous = {pair.task_id: pair.famous for pair in load_pairs()}
    rows = []
    for record in load_runs(runs, split):
        if record["condition"] not in VERIFYING_CONDITIONS or not record.get("agent_verified"):
            continue
        verdict = verdicts.get(record["run_id"], {})
        if verdict.get("status") != "wrong":
            continue
        rows.append(row_for(record, verdict, runs / record["run_id"], famous))
    order = ("c3", "c3n", "c4", "c5", "c5x")
    return sorted(rows, key=lambda r: (r["agent"], order.index(r["condition"]) if r["condition"] in order else 9,
                                       r["task"], r["seed"] or 0))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--runs", type=Path, default=REPO / "runs")
    parser.add_argument("--verdicts", type=Path, default=REPO / "verdicts.json")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--out", type=Path, default=REPO / "analysis" / "false_claims.csv")
    arguments = parser.parse_args(argv)

    data = json.loads(arguments.verdicts.read_text())
    verdicts = data.get("verdicts", data) if isinstance(data, dict) else data
    rows = false_claims(arguments.runs, verdicts, arguments.split)
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    with arguments.out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    by_condition: dict[tuple[str, str], int] = {}
    for row in rows:
        by_condition[(row["agent"], row["condition"])] = by_condition.get((row["agent"], row["condition"]), 0) + 1
    print(f"{len(rows)} false claims -> {arguments.out}")
    for (agent, condition), count in sorted(by_condition.items()):
        hinted = sum(r["shortcut_hint"] for r in rows if r["agent"] == agent and r["condition"] == condition)
        print(f"  {agent:9s} {condition:4s} {count:3d}   shortcut hint: {hinted}")


if __name__ == "__main__":
    main()