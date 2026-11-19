"""Tests for the Independent Set -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_independent_set, solve_clique

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_independent_set(instance)
    got = solve_clique(reduced)
    assert got == expected, (
        f"mismatch on {instance}: source={expected}, reduced={reduced}, target={got}"
    )
    TESTS_PASSED += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield edges


def main() -> None:
    # Exhaustive over all graphs for n = 0..5 and all k in -2..n+2.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random larger graphs with random k.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    # Specific edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 5, "edges": [], "k": 5})          # no edges: yes
    check({"n": 5, "edges": [], "k": 6})          # k > n: no
    check({"n": 5, "edges": [], "k": -1})         # k <= 0: yes
    complete = [[u, v] for u in range(4) for v in range(u + 1, 4)]
    check({"n": 4, "edges": complete, "k": 2})    # complete: IS only size 1
    check({"n": 4, "edges": complete, "k": 1})
    check({"n": 4, "edges": complete, "k": 0})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
