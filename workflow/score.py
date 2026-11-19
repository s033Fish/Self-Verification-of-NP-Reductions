"""Summarize runs per agent and condition against hidden-verifier verdicts.

Inputs:
  runs/<run_id>/result.json   written by `workflow generate`
  verdicts.json               {run_id: {"status": "correct"|"wrong"|"inconclusive", ...}},
                              written by `python -m benchmark.verify`

For each (agent, condition) it reports:
  incl       runs the verifier could not decide (excluded from the rates below)
  correct    share of decided runs the hidden verifier accepts, with a 95% bootstrap CI
  verified   runs whose verdict.json says verified (c3, c3n, c4, c5; a missing verdict
             counts as not verified)
  FP rate    among runs the agent marked verified, the share that are wrong
  MCC        agreement between "agent says verified" and "actually correct"
  tokens     mean prompt and completion tokens per run

For c4 (oracle feedback) a second table splits each run by whether the oracle
ever sent feedback (a counterexample on submit):
  feedback       runs that got at least one round of feedback, and mean rounds
  fixed          of those, the share the hidden verifier finally accepts
  claims after   of those, runs that end with verdict.json saying verified. The
                 runner clears verdict.json at every round, so each such claim
                 was made after the agent saw a counterexample
  FP after       of those claims, the share that are wrong
  FP no-fb       wrong-but-verified runs that never got feedback (the agent
                 claimed verified but never submitted, so the oracle never ran)

For c5 (independent tester, same model) and c5x (the other model as tester,
reviewing the same reduce.py files as c5) the main table grades the tester's
verdict, and rows are labelled by the WRITER's model. A
third table compares it with the writer's own verdict on the same reduce.py:
  writer ver / FP   runs the writer marked verified, and how many are wrong
  tester ver / FP   the same for the tester
  caught            wrong runs the writer verified and the tester rejected
  false alarms      correct runs the writer verified and the tester rejected
  agree %           runs where writer and tester gave the same verdict

c2 (best-of-k) is scored as pass@k: the k samples of one task, agent and seed
count as ONE run, correct if any sample is correct, wrong only if every sample
was decided wrong, inconclusive otherwise. Its tokens are the sum over the k
samples, so they compare directly with the other conditions' per-run cost.

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
VERIFYING_CONDITIONS = {"c3", "c3n", "c4", "c5", "c5x"}  # conditions that write verdict.json
ORACLE_CONDITIONS = {"c4"}  # conditions whose runs carry an oracle_log
TESTER_CONDITIONS = {"c5", "c5x"}  # graded by a separate tester (c5x: the other model)


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


def collapse_best_of_k(
    records: list[dict[str, Any]], verdicts: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Merge each c2 seed's k samples into one pass@k record and verdict."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    others = []
    for record in records:
        if record["condition"] == "c2" and record.get("sample") is not None:
            group_id = record["run_id"].rsplit("__k", 1)[0]
            groups[group_id].append(record)
        else:
            others.append(record)
    merged_verdicts = dict(verdicts)
    for group_id, samples in sorted(groups.items()):
        statuses = [verdicts.get(r["run_id"], {}).get("status") for r in samples]
        if "correct" in statuses:
            status = "correct"
        elif statuses and all(s == "wrong" for s in statuses):
            status = "wrong"
        else:
            status = "inconclusive"
        merged_verdicts[group_id] = {"status": status, "samples": statuses}
        others.append({
            **samples[0],
            "run_id": group_id,
            "sample": None,
            "samples": len(samples),
            "usage": [u for r in samples for u in (r.get("usage") or [])],
        })
    return others, merged_verdicts


def summarize(records: list[dict[str, Any]], verdicts: dict[str, Any]) -> list[dict[str, Any]]:
    rng = random.Random(0)
    records, verdicts = collapse_best_of_k(records, verdicts)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["agent"]["key"], record["condition"])].append(record)

    rows = []
    for (agent, condition), group in sorted(groups.items()):
        status = {r["run_id"]: verdicts.get(r["run_id"], {}).get("status") for r in group}
        # Only runs with a definite verdict are scored; inconclusive never counts as correct.
        scored = [r for r in group if status[r["run_id"]] in ("correct", "wrong")]
        is_correct = {r["run_id"]: status[r["run_id"]] == "correct" for r in scored}
        correct = [is_correct[r["run_id"]] for r in scored]
        # In conditions that ask for verdict.json, a missing or malformed verdict
        # means the agent did not claim its reduction works: count it as "not
        # verified" rather than dropping the run. Single-shot conditions make
        # no claim, so they have no verified column.
        if condition in VERIFYING_CONDITIONS:
            claimed = [{**r, "agent_verified": bool(r.get("agent_verified"))} for r in scored]
        else:
            claimed = []
        verified = [r for r in claimed if r["agent_verified"]]
        wrong_but_verified = [not is_correct[r["run_id"]] for r in verified]
        tp = sum(r["agent_verified"] and is_correct[r["run_id"]] for r in claimed)
        tn = sum(not r["agent_verified"] and not is_correct[r["run_id"]] for r in claimed)
        fp = sum(r["agent_verified"] and not is_correct[r["run_id"]] for r in claimed)
        fn = sum(not r["agent_verified"] and is_correct[r["run_id"]] for r in claimed)
        token_pairs = [tokens(r) for r in group]
        rows.append({
            "agent": agent,
            "condition": condition,
            "runs": len(group),
            "scored": len(scored),
            "inconclusive": sum(v == "inconclusive" for v in status.values()),
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


def feedback_rounds(record: dict[str, Any]) -> int:
    return sum(1 for entry in record.get("oracle_log") or [] if entry.get("feedback"))


def summarize_oracle(records: list[dict[str, Any]], verdicts: dict[str, Any]) -> list[dict[str, Any]]:
    """Split oracle-condition runs by whether they ever got feedback."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["condition"] in ORACLE_CONDITIONS:
            status = verdicts.get(record["run_id"], {}).get("status")
            if status in ("correct", "wrong"):
                groups[(record["agent"]["key"], record["condition"])].append(
                    {**record, "_correct": status == "correct"}
                )
    rows = []
    for (agent, condition), group in sorted(groups.items()):
        got = [r for r in group if feedback_rounds(r) > 0]
        claims_after = [r for r in got if r.get("agent_verified")]
        no_feedback_fp = [
            r for r in group
            if feedback_rounds(r) == 0 and r.get("agent_verified") and not r["_correct"]
        ]
        rows.append({
            "agent": agent,
            "condition": condition,
            "scored": len(group),
            "feedback_runs": len(got),
            "mean_rounds": (sum(feedback_rounds(r) for r in got) / len(got)) if got else math.nan,
            "fixed": (sum(r["_correct"] for r in got) / len(got)) if got else math.nan,
            "claims_after_feedback": len(claims_after),
            "fp_after_feedback": sum(not r["_correct"] for r in claims_after),
            "fp_without_feedback": len(no_feedback_fp),
            "fp_after_feedback_runs": [r["run_id"] for r in claims_after if not r["_correct"]],
        })
    return rows


def summarize_tester(records: list[dict[str, Any]], verdicts: dict[str, Any]) -> list[dict[str, Any]]:
    """Writer vs. tester verdicts on the same reduce.py (c5)."""
    groups: dict[tuple[str, str], list[tuple[bool, bool, bool]]] = defaultdict(list)
    for record in records:
        if record["condition"] not in TESTER_CONDITIONS:
            continue
        status = verdicts.get(record["run_id"], {}).get("status")
        if status in ("correct", "wrong"):
            groups[(record["agent"]["key"], record["condition"])].append((
                status == "correct",
                bool(record.get("writer_verified")),
                bool(record.get("agent_verified")),  # the tester's verdict
            ))
    rows = []
    for (agent, condition), group in sorted(groups.items()):
        rows.append({
            "agent": agent,
            "condition": condition,
            "scored": len(group),
            "writer_verified": sum(w for _, w, _ in group),
            "writer_fp": sum(w and not c for c, w, _ in group),
            "tester_verified": sum(t for _, _, t in group),
            "tester_fp": sum(t and not c for c, _, t in group),
            "caught": sum(w and not t and not c for c, w, t in group),
            "false_alarms": sum(w and not t and c for c, w, t in group),
            "agree": sum(w == t for _, w, t in group) / len(group),
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

    print(f"{'agent':9} {'cond':4} {'runs':>4} {'incl':>4} {'correct %':>17} "
          f"{'verified':>8} {'FP rate %':>17} {'MCC':>6} {'tok in':>8} {'tok out':>8}")
    for row in rows:
        low, high = row["correct_ci"]
        fp_low, fp_high = row["fp_rate_ci"]
        mcc_text = "   -  " if math.isnan(row["mcc"]) else f"{row['mcc']:6.2f}"
        print(
            f"{row['agent']:9} {row['condition']:4} {row['runs']:4d} {row['inconclusive']:4d} "
            f"{pct(row['correct'])} [{pct(low)},{pct(high)}] "
            f"{row['verified']:8d} {pct(row['fp_rate'])} [{pct(fp_low)},{pct(fp_high)}] "
            f"{mcc_text} {row['prompt_tokens']:8.0f} {row['completion_tokens']:8.0f}"
        )
    oracle_rows = summarize_oracle(records, verdicts)
    if oracle_rows:
        print(f"\n{'agent':9} {'cond':4} {'scored':>6} {'feedback':>8} {'rounds':>6} "
              f"{'fixed %':>7} {'claims after':>12} {'FP after':>8} {'FP no-fb':>8}")
        for row in oracle_rows:
            rounds = "  -   " if math.isnan(row["mean_rounds"]) else f"{row['mean_rounds']:6.1f}"
            print(
                f"{row['agent']:9} {row['condition']:4} {row['scored']:6d} "
                f"{row['feedback_runs']:8d} {rounds} {pct(row['fixed']):>7} "
                f"{row['claims_after_feedback']:12d} {row['fp_after_feedback']:8d} "
                f"{row['fp_without_feedback']:8d}"
            )
        for row in oracle_rows:
            for run_id in row["fp_after_feedback_runs"]:
                print(f"  verified after a counterexample, still wrong: {run_id}")
    tester_rows = summarize_tester(records, verdicts)
    if tester_rows:
        print(f"\n{'agent':9} {'cond':4} {'scored':>6} {'writer ver':>10} {'writer FP':>9} "
              f"{'tester ver':>10} {'tester FP':>9} {'caught':>6} {'false alarms':>12} {'agree %':>7}")
        for row in tester_rows:
            print(
                f"{row['agent']:9} {row['condition']:4} {row['scored']:6d} "
                f"{row['writer_verified']:10d} {row['writer_fp']:9d} "
                f"{row['tester_verified']:10d} {row['tester_fp']:9d} {row['caught']:6d} "
                f"{row['false_alarms']:12d} {pct(row['agree']):>7}"
            )
    if arguments.out:
        arguments.out.write_text(json.dumps(
            {"conditions": rows, "oracle": oracle_rows, "tester": tester_rows}, indent=2
        ) + "\n")