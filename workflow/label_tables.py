"""Tables from the hand-labeled false claims (failure causes and spec gaps).

    uv run python -m workflow.label_tables analysis/false_claims_labeled.csv

Reads the CSV that workflow.label_sheet writes, once its `cause` and
`spec_gap` columns are filled in (see label_sheet.py for the labels), and
prints Markdown tables: cause by condition, spec gap by condition, cause by
famous / less common pair, and how often a shortcut's docstring admits it.
Also writes them to analysis/label_tables.md next to the CSV.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

CONDITIONS = ("c3", "c3n", "c4", "c5", "c5x")
CAUSES = ("shortcut", "blowup", "gadget", "iff", "edge_case", "encoding", "other")
GAPS = ("poly_time", "large_instances", "no_instances", "edge_cases", "none")
AGENT_LABELS = {"deepseek": "DeepSeek", "gptoss": "GPT-OSS"}


def gaps(row: dict[str, str]) -> list[str]:
    return [g.strip() for g in row["spec_gap"].split(";") if g.strip()]


def table(title: str, header: list[str], body: list[list[object]]) -> str:
    lines = [f"## {title}", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in body]
    return "\n".join(lines) + "\n"


def tables(rows: list[dict[str, str]]) -> str:
    unlabeled = [r["run_id"] for r in rows if not r["cause"]]
    if unlabeled:
        raise SystemExit(f"{len(unlabeled)} rows have no cause yet, e.g. {unlabeled[0]}")
    groups = sorted({(r["agent"], r["condition"]) for r in rows},
                    key=lambda g: (g[0] != "gptoss", CONDITIONS.index(g[1]) if g[1] in CONDITIONS else 9))
    causes = [c for c in CAUSES if any(r["cause"] == c for r in rows)]
    out = [f"# False claims: causes and spec gaps ({len(rows)} claims)", ""]

    body = []
    for agent, condition in groups:
        group = [r for r in rows if r["agent"] == agent and r["condition"] == condition]
        count = Counter(r["cause"] for r in group)
        body.append([AGENT_LABELS.get(agent, agent), condition, len(group)] + [count.get(c, 0) for c in causes])
    total = Counter(r["cause"] for r in rows)
    body.append(["**all**", "", len(rows)] + [f"**{total.get(c, 0)}**" for c in causes])
    out.append(table("Cause by condition", ["Model", "Condition", "Claims"] + causes, body))

    body = []
    present = [g for g in GAPS if any(g in gaps(r) for r in rows)]
    for agent, condition in groups:
        group = [r for r in rows if r["agent"] == agent and r["condition"] == condition]
        body.append([AGENT_LABELS.get(agent, agent), condition, len(group)]
                    + [sum(g in gaps(r) for r in group) for g in present])
    body.append(["**all**", "", len(rows)] + [f"**{sum(g in gaps(r) for r in rows)}**" for g in present])
    out.append(table("What the agent's check left out (spec gap; a claim can have several)",
                     ["Model", "Condition", "Claims"] + present, body))

    body = []
    for famous, label in (("True", "famous"), ("False", "less common")):
        group = [r for r in rows if r["famous"] == famous]
        count = Counter(r["cause"] for r in group)
        body.append([label, len(group)] + [count.get(c, 0) for c in causes])
    out.append(table("Cause by pair type (all claims)", ["Pairs", "Claims"] + causes, body))

    shortcuts = [r for r in rows if r["cause"] == "shortcut"]
    if shortcuts and "admits" in rows[0]:
        admitted = sum(r["admits"] == "True" for r in shortcuts)
        out.append(f"Shortcuts whose docstring admits the brute force or the small-instance assumption: "
                   f"{admitted} of {len(shortcuts)}.\n")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("csv", type=Path, help="the labeled false_claims CSV")
    arguments = parser.parse_args(argv)
    rows = list(csv.DictReader(arguments.csv.open()))
    text = tables(rows)
    (arguments.csv.parent / "label_tables.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()