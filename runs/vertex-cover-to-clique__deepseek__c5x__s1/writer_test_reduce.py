"""Tests for the Vertex Cover -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import clique_yes, vertex_cover_yes

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = vertex_cover_yes(instance)
    got = clique_yes(reduced)
    assert expected == got, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main() -> None:
    # Exhaustive over all graphs for n = 0..4 and many k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -1})
    check({"n": 5, "edges": [[0, 1]], "k": 5})
    check({"n": 5, "edges": [[0, 1]], "k": 0})
    check({"n": 5, "edges": [[0, 1]], "k": 1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
