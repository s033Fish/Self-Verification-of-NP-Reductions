"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import random
from itertools import combinations

from problems import ThreeColoring, IndependentSet
from reduce import reduce
from solvers import solve_three_coloring, solve_independent_set


def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(source: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(source)
        target = reduce(source)
        IndependentSet.validate(target)
        expected = solve_three_coloring(source)
        got = solve_independent_set(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((source, target, expected, got))

    # Exhaustive over all graphs with up to 4 vertices (2^6 = 64 graphs at n=4).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs with 5 and 6 vertices (reduced graphs have 15/18 nodes).
    rng = random.Random(12345)
    for n, count in ((5, 60), (6, 25)):
        for _ in range(count):
            check(random_graph(n, rng.uniform(0.1, 0.9), rng))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # K3, yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4, no
    check({"n": 5, "edges": []})  # no edges, yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:5]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
