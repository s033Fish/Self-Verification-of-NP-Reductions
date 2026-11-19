"""Tests for the Vertex Cover -> Set Cover reduction in reduce.py.

Compares problems.VertexCover.is_yes on small source instances against
problems.SetCover.is_yes on the reduced instances, and validates both.
"""

from __future__ import annotations

import random

import problems
from problems import SetCover, VertexCover
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    SetCover.validate(reduced)
    expected = VertexCover.is_yes(instance)
    got = SetCover.is_yes(reduced)
    assert expected == got, (
        f"mismatch: source={instance} source_yes={expected} "
        f"reduced={reduced} reduced_yes={got}"
    )
    tests_passed += 1


def main() -> None:
    # 1. Exhaustive small instances (all graphs up to 4 vertices, k in -1..n+1).
    for instance in VertexCover.enumerate_instances(4):
        check(instance)

    # 2. Random instances across several scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(400):
            check(VertexCover.random_instance(rng, scale))

    # 3. Explicit edge cases.
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 5})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 100})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": -100})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1})
    check({"n": 5, "edges": [[0, 1], [2, 3], [4, 0]], "k": 2})

    # 4. Larger random instances to exercise the solvers more.
    for _ in range(200):
        check(VertexCover.random_instance(rng, 12))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
