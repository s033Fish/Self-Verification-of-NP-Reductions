"""Tests comparing brute-force solvers on source instances and reductions."""

from __future__ import annotations

import random

import problems
from reduce import reduce

SOURCE = problems.VertexCover
TARGET = problems.DominatingSet


def check(instance):
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert expected == got, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Exhaustive small instances (graphs up to 4 vertices, k from -1 to n+1).
    for scale in range(0, 5):
        for instance in SOURCE.enumerate_instances(scale):
            run(instance)

    # Random instances over a range of scales.
    rng = random.Random(12345)
    for scale in range(0, 8):
        for _ in range(300):
            run(SOURCE.random_instance(rng, scale))

    # Explicit edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 0, "edges": [], "k": 5})
    run({"n": 5, "edges": [], "k": 0})
    run({"n": 5, "edges": [], "k": 4})
    run({"n": 5, "edges": [], "k": -3})
    run({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0})
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})
    run({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3})
    run({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2})
    run({"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 4})
    run({"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 5})
    run({"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": -1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
