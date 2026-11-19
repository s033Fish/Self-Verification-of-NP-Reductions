"""Tests for the Vertex Cover -> Independent Set reduction.

We brute-force both problems on many small instances and check that
reduce(instance) has the same answer as instance.
"""

from __future__ import annotations

import itertools

import problems
from reduce import reduce
from solvers import independent_set_yes, vertex_cover_yes

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1

    # Both the source and the produced target must be valid instances.
    problems.VertexCover.validate(instance)
    reduced = reduce(instance)
    problems.IndependentSet.validate(reduced)

    source_answer = vertex_cover_yes(instance)
    target_answer = independent_set_yes(reduced)
    assert source_answer == target_answer, (
        f"MISMATCH on {instance}: source={source_answer}, "
        f"reduced={reduced}, target={target_answer}"
    )
    tests_passed += 1


def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def main() -> None:
    # Exhaustive: all graphs on up to 5 vertices, all k in a wide range.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Some larger random-ish structured cases.
    import random

    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
