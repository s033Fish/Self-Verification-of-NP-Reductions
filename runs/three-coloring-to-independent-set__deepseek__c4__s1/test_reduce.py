"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, IndependentSet
from reduce import reduce
from solvers import solve_three_coloring, solve_independent_set

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    expected = solve_three_coloring(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    got = solve_independent_set(reduced)
    assert got == expected, (
        f"mismatch on {instance}: source={expected}, reduced={got}, "
        f"reduced_instance={reduced}"
    )
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        check({"n": n, "edges": edges})

    # A few structured cases.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4
    check({"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]})  # K3
    check({"n": 0, "edges": []})
    check({"n": 5, "edges": []})  # edgeless

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
