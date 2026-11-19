"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

from itertools import combinations

from problems import IndependentSet, VertexCover
from reduce import reduce
from solvers import solve_independent_set, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance) -> None:
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    src = solve_independent_set(instance)
    tgt = solve_vertex_cover(reduced)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt} inst={instance} red={reduced}"
    tests_passed += 1


def all_graphs(n):
    """All simple graphs on n vertices, as edge lists."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield edges


def main() -> None:
    # Exhaustive over all graphs with n = 0..4 and all relevant k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # A few larger random-ish structured cases.
    import random
    random.seed(12345)
    for _ in range(300):
        n = random.randint(5, 8)
        possible = list(combinations(range(n), 2))
        edges = [list(e) for e in possible if random.random() < 0.4]
        k = random.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # Edge cases explicitly.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 5, "edges": [], "k": 5})
    check({"n": 5, "edges": [], "k": -3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
