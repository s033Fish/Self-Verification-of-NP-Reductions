"""Tests comparing brute-force answers on Vertex Cover instances and their
reductions to Clique."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import clique_answer, vertex_cover_answer

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = vertex_cover_answer(instance)
    got = clique_answer(reduced)
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, reduced={reduced} target={got}"
    )
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main() -> None:
    # Exhaustive over all graphs for n = 0..5 and a range of k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -1})
    check({"n": 5, "edges": [[0, 1]], "k": 0})
    check({"n": 5, "edges": [[0, 1]], "k": 1})
    check({"n": 5, "edges": [[0, 1]], "k": 5})
    check({"n": 5, "edges": [[0, 1]], "k": 6})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")


if __name__ == "__main__":
    main()
