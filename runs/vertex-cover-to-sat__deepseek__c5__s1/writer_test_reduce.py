"""Tests comparing brute-force answers on Vertex Cover instances and their SAT reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_sat, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_vertex_cover(instance)
    actual = solve_sat(reduced)
    assert actual == expected, (
        f"MISMATCH for {instance}: source={expected}, reduced={actual}, "
        f"reduction={reduced}"
    )
    tests_passed += 1


def all_graphs(n: int):
    """All simple graphs on n labelled vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def exhaustive_small() -> None:
    # Exhaustive over all graphs with n <= 4 and a wide range of k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})


def random_tests() -> None:
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 7)
        possible = list(itertools.combinations(range(n), 2))
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})


def larger_random_tests() -> None:
    rng = random.Random(999)
    for _ in range(600):
        n = rng.randint(5, 10)
        possible = list(itertools.combinations(range(n), 2))
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        # Bias k toward small values so the cardinality encoding is exercised.
        k = rng.choice([0, 1, 2, 3, n - 1, n, n + 1, -1])
        check({"n": n, "edges": edges, "k": k})


def edge_cases() -> None:
    # No edges: yes for every k >= 0, no for k < 0.
    for k in range(-1, 5):
        check({"n": 4, "edges": [], "k": k})
    # k >= n is always yes.
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 10})
    # Triangle needs 2, so k=1 no and k=2 yes.
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    # n = 0 with no edges.
    for k in range(-1, 3):
        check({"n": 0, "edges": [], "k": k})
    # Single edge.
    for k in range(-1, 3):
        check({"n": 2, "edges": [[0, 1]], "k": k})
    # Reversed endpoint order.
    check({"n": 2, "edges": [[1, 0]], "k": 0})
    check({"n": 2, "edges": [[1, 0]], "k": 1})


def main() -> None:
    exhaustive_small()
    random_tests()
    larger_random_tests()
    edge_cases()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
