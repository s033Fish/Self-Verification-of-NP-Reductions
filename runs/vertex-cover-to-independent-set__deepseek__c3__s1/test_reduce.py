"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # The reduction must produce a valid target instance.
    TARGET.validate(reduced)
    src = SOURCE.is_yes(instance)
    tgt = TARGET.is_yes(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    tests_passed += 1


def main():
    # 1. Exhaustive: every graph on 0..4 vertices, every k from -1 to n+1.
    for instance in SOURCE.enumerate_instances(4):
        check(instance)

    # 2. Random instances at several scales, including edge-case k values.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            check(SOURCE.random_instance(rng, scale))

    # 3. Explicit edge cases.
    explicit = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 3},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 100},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": -1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 5},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
    ]
    for instance in explicit:
        SOURCE.validate(instance)
        check(instance)

    # 4. The reduction must not mutate its input.
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}
    snapshot = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}
    reduce(inst)
    assert inst == snapshot, inst

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
