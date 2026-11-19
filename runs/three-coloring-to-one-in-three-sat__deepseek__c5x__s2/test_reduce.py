"""Automated tests for the reduction from ThreeColoring to OneInThreeSat.

The test suite enumerates all small graphs (up to 3 vertices) and checks
that the answer of the source problem matches the answer of the reduced
target problem.  It also validates that both instances conform to the
validation logic provided in ``problems.py``.

If all tests pass, the reduction is considered verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems
import reduce


def solve_three_coloring(instance: dict) -> bool:
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = [tuple(cl) for cl in instance["clauses"]]
    for mask in range(1 << m):
        ok = True
        for a, b, c in clauses:
            true_cnt = ((mask >> (a - 1)) & 1) + ((mask >> (b - 1)) & 1) + ((mask >> (c - 1)) & 1)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def enumerate_graphs(max_n: int = 3):
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices, 2))
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                yield {"n": n, "edges": [[u, v] for u, v in edges]}


def main() -> None:
    total = 0
    passed = 0
    for src in enumerate_graphs(3):
        total += 1
        problems.ThreeColoring.validate(src)
        src_ans = solve_three_coloring(src)
        tgt = reduce.reduce(src)
        problems.OneInThreeSat.validate(tgt)
        tgt_ans = solve_one_in_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch", src, src_ans, tgt_ans, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
