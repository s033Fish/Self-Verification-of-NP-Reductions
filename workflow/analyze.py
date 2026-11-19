"""Paper analysis: main table, paired comparisons, famous vs. less common, figures.

    uv run python -m workflow.analyze                        # test split, writes analysis/
    uv run --with matplotlib python -m workflow.analyze      # also draws the figures

Reads the same inputs as `workflow score` (runs/*/result.json, verdicts.json)
and reuses its pass@k merge for c2. Differences from the scorer:

* Confidence intervals resample TASKS, not runs. The 3 seeds of one task are
  correlated (a hard pair tends to fail every seed), so resampling runs
  understates the uncertainty. Each bootstrap draw picks tasks with
  replacement and keeps all of their runs.
* Conditions are compared PAIRED: the same model, task and seed in both
  conditions. Correctness and "false claim" (verified AND wrong) are binary
  per run, so each comparison gets an exact McNemar test on the discordant
  pairs and a task-clustered CI for the difference in rates. The false-positive
  RATE (wrong among verified) has a different denominator in each condition,
  so it cannot be paired; the false-claim rate is its paired counterpart.
  c5 vs. c5x is the cleanest pair: the same reduce.py files, two testers.

Outputs in analysis/: analysis.md (all tables), analysis.json, and with
matplotlib, fig_fp_rate.pdf/.png and fig_correct_vs_tokens.pdf/.png.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from benchmark.make_task import load_pairs
from workflow.score import VERIFYING_CONDITIONS, collapse_best_of_k, load_runs, tokens

REPO = Path(__file__).resolve().parents[1]
CONDITION_ORDER = ("c1", "c2", "c3", "c3n", "c4", "c5", "c5x")
# Short two-line labels for figure axes.
CONDITION_TICKS = {
    "c3": "self-test\n+solvers",
    "c3n": "self-test",
    "c4": "oracle",
    "c5": "tester\n(same)",
    "c5x": "tester\n(other)",
}
CONDITION_LABELS = {
    "c1": "single shot",
    "c2": "pass@3",
    "c3": "self-test (solvers)",
    "c3n": "self-test (no solvers)",
    "c4": "oracle feedback",
    "c5": "same-model tester",
    "c5x": "other-model tester",
}
AGENT_LABELS = {"deepseek": "DeepSeek V4.1 Flash", "gptoss": "GPT-OSS 120B"}
# Reference palette, categorical slots 1-2 (validated: CVD dE 26.4). Orange is
# under 3:1 on white, so every figure also has a legend and direct labels.
AGENT_COLORS = {"deepseek": "#2a78d6", "gptoss": "#eb6834"}
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
BOOTSTRAP_SAMPLES = 2000

# (A, B, outcome): is A's rate different from B's on the same model/task/seed?
PAIRED_COMPARISONS = (
    ("c2", "c3n", "correct"),
    ("c3", "c3n", "correct"),
    ("c4", "c3n", "correct"),
    ("c3", "c3n", "false_claim"),
    ("c4", "c3n", "false_claim"),
    ("c5", "c3n", "false_claim"),
    ("c5x", "c5", "false_claim"),
)


# --- Per-run outcomes ----------------------------------------------------------


def outcomes(records: list[dict[str, Any]], verdicts: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per decided run (c2: per pass@k group), with famous/less common."""
    famous = {pair.task_id: pair.famous for pair in load_pairs()}
    records, verdicts = collapse_best_of_k(records, verdicts)
    rows = []
    for record in records:
        status = verdicts.get(record["run_id"], {}).get("status")
        if status not in ("correct", "wrong"):
            continue  # inconclusive or unverified runs are reported, not scored
        condition = record["condition"]
        correct = status == "correct"
        verifying = condition in VERIFYING_CONDITIONS
        verified = bool(record.get("agent_verified")) if verifying else None
        prompt, completion = tokens(record)
        rows.append({
            "run_id": record["run_id"],
            "agent": record["agent"]["key"],
            "condition": condition,
            "task": record["task_id"],
            "seed": record.get("seed"),
            "famous": famous.get(record["task_id"]),
            "correct": correct,
            "verified": verified,
            "false_claim": (verified and not correct) if verifying else None,
            "tokens": prompt + completion,
        })
    return rows


# --- Statistics ----------------------------------------------------------------


def _by_task(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["task"]].append(row)
    return groups


def cluster_ci(rows, statistic, rng: random.Random, samples: int = BOOTSTRAP_SAMPLES):
    """95% CI for statistic(rows), resampling tasks with replacement."""
    groups = list(_by_task(rows).values())
    if not groups:
        return (math.nan, math.nan)
    values = []
    for _ in range(samples):
        draw = [row for group in rng.choices(groups, k=len(groups)) for row in group]
        value = statistic(draw)
        if not math.isnan(value):
            values.append(value)
    if not values:
        return (math.nan, math.nan)
    values.sort()
    return values[int(0.025 * len(values))], values[max(int(0.975 * len(values)) - 1, 0)]


def rate(rows, key: str) -> float:
    values = [row[key] for row in rows if row[key] is not None]
    return sum(values) / len(values) if values else math.nan


def fp_rate(rows) -> float:
    """Wrong among verified."""
    claimed = [row for row in rows if row["verified"]]
    return sum(not row["correct"] for row in claimed) / len(claimed) if claimed else math.nan


def holm(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values, in the input order."""
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def permutation_p(rows, statistic, rng: random.Random, samples: int = BOOTSTRAP_SAMPLES) -> float:
    """Two-sided p for statistic(famous rows) - statistic(less common rows),
    shuffling which TASKS are famous (keeping how many are)."""
    groups = _by_task(rows)
    tasks = sorted(groups)
    labels = [groups[t][0]["famous"] for t in tasks]

    def difference(famous_tasks: set[str]) -> float:
        a = [r for t in tasks if t in famous_tasks for r in groups[t]]
        b = [r for t in tasks if t not in famous_tasks for r in groups[t]]
        return statistic(a) - statistic(b)

    observed = difference({t for t, f in zip(tasks, labels) if f})
    if math.isnan(observed):
        return math.nan
    hits = valid = 0
    for _ in range(samples):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        value = difference({t for t, f in zip(tasks, shuffled) if f})
        if math.isnan(value):
            continue
        valid += 1
        hits += abs(value) >= abs(observed) - 1e-12
    return (hits + 1) / (valid + 1) if valid else math.nan


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value for b and c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


# --- Tables --------------------------------------------------------------------


def main_table(rows, rng) -> list[dict[str, Any]]:
    table = []
    groups: dict[tuple[str, str], list] = defaultdict(list)
    for row in rows:
        groups[(row["agent"], row["condition"])].append(row)
    for agent in sorted({row["agent"] for row in rows}):
        for condition in CONDITION_ORDER:
            group = groups.get((agent, condition))
            if not group:
                continue
            verifying = condition in VERIFYING_CONDITIONS
            entry = {
                "agent": agent,
                "condition": condition,
                "runs": len(group),
                "tasks": len({row["task"] for row in group}),
                "correct": rate(group, "correct"),
                "correct_ci": cluster_ci(group, lambda r: rate(r, "correct"), rng),
                "mean_tokens": sum(row["tokens"] for row in group) / len(group),
            }
            if verifying:
                entry |= {
                    "verified": sum(bool(row["verified"]) for row in group),
                    "fp_rate": fp_rate(group),
                    "fp_rate_ci": cluster_ci(group, fp_rate, rng),
                    "false_claim": rate(group, "false_claim"),
                }
            table.append(entry)
    return table


def paired_table(rows, rng) -> list[dict[str, Any]]:
    index = {(row["agent"], row["condition"], row["task"], row["seed"]): row for row in rows}
    results = []
    for agent in sorted({row["agent"] for row in rows}):
        for a, b, outcome in PAIRED_COMPARISONS:
            pairs = []
            for (ag, cond, task, seed), row_a in index.items():
                if ag != agent or cond != a:
                    continue
                row_b = index.get((agent, b, task, seed))
                if row_b is None or row_a[outcome] is None or row_b[outcome] is None:
                    continue
                pairs.append({"task": task, "a": bool(row_a[outcome]), "b": bool(row_b[outcome])})
            if not pairs:
                continue
            only_a = sum(p["a"] and not p["b"] for p in pairs)
            only_b = sum(p["b"] and not p["a"] for p in pairs)

            def difference(draw):
                return (sum(p["a"] for p in draw) - sum(p["b"] for p in draw)) / len(draw) if draw else math.nan

            results.append({
                "agent": agent,
                "a": a,
                "b": b,
                "outcome": outcome,
                "pairs": len(pairs),
                "rate_a": sum(p["a"] for p in pairs) / len(pairs),
                "rate_b": sum(p["b"] for p in pairs) / len(pairs),
                "only_a": only_a,
                "only_b": only_b,
                "difference": difference(pairs),
                "difference_ci": cluster_ci(pairs, difference, rng),
                "p_mcnemar": mcnemar_exact(only_a, only_b),
            })
    # Holm over the comparisons of each model (the family the paper reports).
    for agent in {r["agent"] for r in results}:
        family = [r for r in results if r["agent"] == agent]
        for r, adjusted in zip(family, holm([r["p_mcnemar"] for r in family])):
            r["p_holm"] = adjusted
    return results


def famous_table(rows, rng) -> list[dict[str, Any]]:
    """Famous vs. less common, per model and condition: each half with a
    task-resampled CI, and a permutation p for the difference."""
    groups: dict[tuple, list] = defaultdict(list)
    for row in rows:
        if row["famous"] is not None:
            groups[(row["agent"], row["condition"])].append(row)
    table = []
    for (agent, condition), group in sorted(groups.items(), key=lambda kv: (kv[0][0], CONDITION_ORDER.index(kv[0][1]))):
        famous = [r for r in group if r["famous"]]
        common = [r for r in group if not r["famous"]]
        correct = lambda r: rate(r, "correct")  # noqa: E731
        entry = {
            "agent": agent, "condition": condition, "runs": (len(famous), len(common)),
            "correct": (correct(famous), correct(common)),
            "correct_ci": (cluster_ci(famous, correct, rng), cluster_ci(common, correct, rng)),
            "correct_p": permutation_p(group, correct, rng),
        }
        if condition in VERIFYING_CONDITIONS:
            entry |= {
                "fp_rate": (fp_rate(famous), fp_rate(common)),
                "fp_rate_ci": (cluster_ci(famous, fp_rate, rng), cluster_ci(common, fp_rate, rng)),
                "fp_rate_p": permutation_p(group, fp_rate, rng),
            }
        table.append(entry)
    return table


# --- Output --------------------------------------------------------------------


def pct(x: float) -> str:
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}"


def ci(pair) -> str:
    return f"[{pct(pair[0])}, {pct(pair[1])}]"


def markdown(main, paired, famous, excluded: int) -> str:
    lines = ["# Results (test split)", ""]
    lines += [f"{excluded} run(s) excluded as inconclusive or unverified.", ""]
    lines += ["## Main table (95% CIs resample tasks)", "",
              "| Model | Condition | Runs | Correct % [CI] | Verified | FP rate % [CI] | Mean tokens |",
              "|---|---|---|---|---|---|---|"]
    for e in main:
        fp = f"{pct(e['fp_rate'])} {ci(e['fp_rate_ci'])}" if "fp_rate" in e else "-"
        lines.append(
            f"| {AGENT_LABELS.get(e['agent'], e['agent'])} | {e['condition']} {CONDITION_LABELS[e['condition']]} "
            f"| {e['runs']} | {pct(e['correct'])} {ci(e['correct_ci'])} | {e.get('verified', '-')} "
            f"| {fp} | {e['mean_tokens'] / 1000:.0f}k |"
        )
    lines += ["", "## Paired comparisons (same model, task and seed)", "",
              "Difference = rate(A) - rate(B). McNemar's exact test on discordant pairs.", "",
              "Holm p: Holm-Bonferroni adjusted over the comparisons of each model.", "",
              "| Model | Outcome | A vs B | Pairs | A % | B % | Only A | Only B | Diff (pp) [CI] | p | Holm p |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in paired:
        lines.append(
            f"| {AGENT_LABELS.get(e['agent'], e['agent'])} | {e['outcome']} | {e['a']} vs {e['b']} | {e['pairs']} "
            f"| {pct(e['rate_a'])} | {pct(e['rate_b'])} | {e['only_a']} | {e['only_b']} "
            f"| {100 * e['difference']:+.1f} {ci(e['difference_ci'])} | {e['p_mcnemar']:.3g} | {e['p_holm']:.3g} |"
        )
    lines += ["", "## Famous vs. less common pairs", "",
              "Each half: 16 tasks x 3 seeds. CIs resample tasks; p: permutation test shuffling which tasks are famous.", "",
              "| Model | Condition | Correct % famous [CI] | Correct % less common [CI] | p | "
              "FP % famous [CI] | FP % less common [CI] | p |",
              "|---|---|---|---|---|---|---|---|"]

    def p_text(x):
        return "-" if x is None or math.isnan(x) else f"{x:.3g}"

    for e in famous:
        fp_cells = "| - | - | - |"
        if "fp_rate" in e:
            fp_cells = (f"| {pct(e['fp_rate'][0])} {ci(e['fp_rate_ci'][0])} "
                        f"| {pct(e['fp_rate'][1])} {ci(e['fp_rate_ci'][1])} | {p_text(e['fp_rate_p'])} |")
        lines.append(
            f"| {AGENT_LABELS.get(e['agent'], e['agent'])} | {e['condition']} "
            f"| {pct(e['correct'][0])} {ci(e['correct_ci'][0])} | {pct(e['correct'][1])} {ci(e['correct_ci'][1])} "
            f"| {p_text(e['correct_p'])} " + fp_cells
        )
    return "\n".join(lines) + "\n"


def figures(main, out: Path) -> list[Path]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping figures (run with `uv run --with matplotlib`)")
        return []
    plt.rcParams.update({
        "font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
        "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    })
    agents = sorted({e["agent"] for e in main})
    written = []

    # Figure 1: false-positive rate by condition (verifying conditions only).
    conditions = [c for c in CONDITION_ORDER if c in VERIFYING_CONDITIONS]
    fig, ax = plt.subplots(figsize=(3.3, 2.1))  # one ACL column
    width = 0.38
    for i, agent in enumerate(agents):
        xs, ys, lo, hi = [], [], [], []
        for j, condition in enumerate(conditions):
            e = next((e for e in main if e["agent"] == agent and e["condition"] == condition), None)
            if e is None or math.isnan(e["fp_rate"]):
                continue
            xs.append(j + (i - (len(agents) - 1) / 2) * width)
            ys.append(100 * e["fp_rate"])
            lo.append(100 * (e["fp_rate"] - e["fp_rate_ci"][0]))
            hi.append(100 * (e["fp_rate_ci"][1] - e["fp_rate"]))
        ax.bar(xs, ys, width=width - 0.04, color=AGENT_COLORS.get(agent), label=AGENT_LABELS.get(agent, agent),
               edgecolor="white", linewidth=1)
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK, elinewidth=0.8, capsize=2)
        for x, y in zip(xs, ys):
            if y == 0:  # a zero bar has no height: say so, so it does not read as missing
                ax.annotate("0", (x, 0), textcoords="offset points", xytext=(0, 2),
                            ha="center", fontsize=7, color=MUTED)
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels([f"{c}\n{CONDITION_TICKS[c]}" for c in conditions], fontsize=6.5)
    ax.set_ylabel("False-positive rate (%)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(agents))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        path = out / f"fig_fp_rate.{ext}"
        fig.savefig(path, dpi=200)
        written.append(path)
    plt.close(fig)

    # Figure 2: correctness vs. mean tokens per run, one point per condition.
    # c5x is left out: it re-tests c5's reductions, so its correctness equals
    # c5's and its tokens count only the tester.
    fig, ax = plt.subplots(figsize=(3.3, 2.4))  # one ACL column
    for agent in agents:
        points = [e for e in main if e["agent"] == agent and e["condition"] != "c5x"]
        xs = [e["mean_tokens"] / 1000 for e in points]
        ys = [100 * e["correct"] for e in points]
        ax.scatter(xs, ys, s=36, color=AGENT_COLORS.get(agent), label=AGENT_LABELS.get(agent, agent),
                   edgecolor="white", linewidth=1.5, zorder=3)
        for e, x, y in zip(points, xs, ys):
            ax.annotate(e["condition"], (x, y), textcoords="offset points", xytext=(4, 2),
                        fontsize=6.5, color=INK)
    ax.set_xlabel("Mean tokens per run (thousands)")
    ax.set_ylabel("Correct (%)")
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        path = out / f"fig_correct_vs_tokens.{ext}"
        fig.savefig(path, dpi=200)
        written.append(path)
    plt.close(fig)
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--runs", type=Path, default=REPO / "runs")
    parser.add_argument("--verdicts", type=Path, default=REPO / "verdicts.json")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--out", type=Path, default=REPO / "analysis")
    arguments = parser.parse_args(argv)

    data = json.loads(arguments.verdicts.read_text())
    verdicts = data.get("verdicts", data) if isinstance(data, dict) else data
    records = load_runs(arguments.runs, arguments.split)
    rows = outcomes(records, verdicts)
    merged, _ = collapse_best_of_k(records, verdicts)
    excluded = len(merged) - len(rows)

    rng = random.Random(0)
    main_rows = main_table(rows, rng)
    paired = paired_table(rows, rng)
    famous = famous_table(rows, rng)

    arguments.out.mkdir(parents=True, exist_ok=True)
    text = markdown(main_rows, paired, famous, excluded)
    (arguments.out / "analysis.md").write_text(text)
    (arguments.out / "analysis.json").write_text(json.dumps(
        {"main": main_rows, "paired": paired, "famous": famous, "excluded": excluded}, indent=2, default=str
    ) + "\n")
    print(text)
    for path in figures(main_rows, arguments.out):
        print("wrote", path.relative_to(REPO) if path.is_relative_to(REPO) else path)


if __name__ == "__main__":
    main()