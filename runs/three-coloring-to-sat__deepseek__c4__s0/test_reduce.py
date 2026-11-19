"""Tests comparing brute-force answers on small 3-coloring instances with
the answers on their reductions."""
from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce
from solvers import solve_three_coloring, solve_sat

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    src = solve_three_coloring(instance)
    tgt = solve_sat(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    # Edge cases
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # K4 must be no
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})

    # Exhaustive over all graphs up to 4 vertices
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs up to 6 vertices
    rng = random.Random(12345)
    for _ in range(200):
        n = rng.randint(0, 6)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        check({"n": n, "edges": edges})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
