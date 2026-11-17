"""Tests comparing brute-force answers on source instances and their reductions."""

from __future__ import annotations

import random

import problems
from reduce import reduce
from solvers import solve_three_coloring, solve_sat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    problems.ThreeColoring.validate(instance)
    out = reduce(instance)
    problems.Sat.validate(out)
    expected = solve_three_coloring(instance)
    got = solve_sat(out)
    assert expected == got, (
        f"mismatch on {instance}: 3-coloring={expected}, reduced SAT={got}, "
        f"reduction={out}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    # Exhaustive over every graph with 0..4 vertices.
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs (still small enough for brute force).
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 7)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        check({"n": n, "edges": edges})

    # Explicit edge cases from the docstrings.
    check({"n": 0, "edges": []})                       # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # triangle, yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4, no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5, yes

    # Structural checks on the reduction output.
    out = reduce({"n": 0, "edges": []})
    assert out == {"num_vars": 0, "clauses": []}
    out = reduce({"n": 2, "edges": [[0, 1]]})
    assert out["num_vars"] == 6
    # 2 vertices * (1 at-least-one + 3 at-most-one) + 1 edge * 3 colours
    assert len(out["clauses"]) == 2 * 4 + 3

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
