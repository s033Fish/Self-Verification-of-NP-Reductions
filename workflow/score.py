"""Summarize runs per agent and condition against hidden-verifier verdicts.

Inputs:
  runs/<run_id>/result.json   written by `workflow generate`
  verdicts.json               {run_id: {"correct": true|false, ...}}, written
                              by the hidden verifier (built in Week 1)

For each (agent, condition) it reports:
  correct    share of runs the hidden verifier accepts, with a 95% bootstrap CI
  FP rate    among runs the agent marked verified, the share that are wrong
  MCC        agreement between "agent says verified" and "actually correct"
  tokens     mean prompt and completion tokens per run

c2 samples are scored as individual runs; choose how best-of-k picks one
sample (e.g. random, or pass@k) before reporting it.

The MCC formula follows Assignment 2's `workflow/evaluate.py`.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from .tasks import REPO

BOOTSTRAP_SAMPLES = 2000


def mcc(tp: int, tn: int, fp: int, fn: int) -> float:
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return 0.0 if denominator == 0 else (tp * tn - fp * fn) / denominator


def bootstrap_ci(values: list[bool], rng: random.Random) -> tuple[float, float]:
    if not values:
        return (math.nan, math.nan)
    means = sorted(
        sum(rng.choices(values, k=len(values))) / len(values)
        for _ in range(BOOTSTRAP_SAMPLES)
    )
    return means[int(0.025 * BOOTSTRAP_SAMPLES)], means[int(0.975 * BOOTSTRAP_SAMPLES) - 1]


def tokens(record: dict[str, Any]) -> tuple[int, int]:
    prompt = completion = 0
    for usage in record.get("usage") or []:
        if isinstance(usage, dict):
            prompt += usage.get("prompt_tokens") or 0
            completion += usage.get("completion_tokens") or 0
    return prompt, completion


def load_runs(runs: Path, split: str) -> list[dict[str, Any]]:
    records = [json.loads(path.read_text()) for path in sorted(runs.glob("*/result.json"))]
    return [r for r in records if split == "all" or r.get("split") == split]


def summarize(records: list[dict[str, Any]], verdicts: dict[str, Any]) -> list[dict[str, Any]]:
    rng = random.Random(0)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["agent"]["key"], record["condition"])].append(record)

    rows = []
    for (agent, condition), group in sorted(groups.items()):
        scored = [r for r in group if r["run_id"] in verdicts]
        correct = [bool(verdicts[r["run_id"]]["correct"]) for r in scored]
        claimed = [r for r in scored if r.get("agent_verified") is not None]
        verified = [r for r in claimed if r["agent_verified"]]
        wrong_but_verified = [not verdicts[r["run_id"]]["correct"] for r in verified]
        tp = sum(r["agent_verified"] and verdicts[r["run_id"]]["correct"] for r in claimed)
        tn = sum(not r["agent_verified"] and not verdicts[r["run_id"]]["correct"] for r in claimed)
        fp = sum(r["agent_verified"] and not verdicts[r["run_id"]]["correct"] for r in claimed)
        fn = sum(not r["agent_verified"] and verdicts[r["run_id"]]["correct"] for r in claimed)
        token_pairs = [tokens(r) for r in group]
        rows.append({
            "agent": agent,
            "condition": condition,
            "runs": len(group),
            "scored": len(scored),
            "correct": sum(correct) / len(correct) if correct else math.nan,
            "correct_ci": bootstrap_ci(correct, rng),
            "verified": len(verified),
            "fp_rate": (sum(wrong_but_verified) / len(verified)) if verified else math.nan,
            "fp_rate_ci": bootstrap_ci(wrong_but_verified, rng),
            "mcc": mcc(tp, tn, fp, fn) if claimed else math.nan,
            "prompt_tokens": sum(p for p, _ in token_pairs) / len(group),
            "completion_tokens": sum(c for _, c in token_pairs) / len(group),
        })
    return rows


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="score runs against verdicts")
    parser.add_argument("--runs", type=Path, default=REPO / "runs")
    parser.add_argument("--verdicts", type=Path, default=REPO / "verdicts.json")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--out", type=Path, help="also write the table as JSON")
    arguments = parser.parse_args(argv)

    records = load_runs(arguments.runs, arguments.split)
    if not records:
        parser.error(f"no {arguments.split} runs under {arguments.runs}")
    verdicts = (
        json.loads(arguments.verdicts.read_text()) if arguments.verdicts.exists() else {}
    )
    if not verdicts:
        print(f"note: no verdicts at {arguments.verdicts}; only token counts are filled")
    rows = summarize(records, verdicts)

    def pct(value: float) -> str:
        return "  -  " if math.isnan(value) else f"{100 * value:5.1f}"

    print(f"{'agent':9} {'cond':4} {'runs':>4} {'correct %':>17} "
          f"{'verified':>8} {'FP rate %':>17} {'MCC':>6} {'tok in':>8} {'tok out':>8}")
    for row in rows:
        low, high = row["correct_ci"]
        fp_low, fp_high = row["fp_rate_ci"]
        mcc_text = "   -  " if math.isnan(row["mcc"]) else f"{row['mcc']:6.2f}"
        print(
            f"{row['agent']:9} {row['condition']:4} {row['runs']:4d} "
            f"{pct(row['correct'])} [{pct(low)},{pct(high)}] "
            f"{row['verified']:8d} {pct(row['fp_rate'])} [{pct(fp_low)},{pct(fp_high)}] "
            f"{mcc_text} {row['prompt_tokens']:8.0f} {row['completion_tokens']:8.0f}"
        )
    if arguments.out:
        arguments.out.write_text(json.dumps(rows, indent=2) + "\n")
