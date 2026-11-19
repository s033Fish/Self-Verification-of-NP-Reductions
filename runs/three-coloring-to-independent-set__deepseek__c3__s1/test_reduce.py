"""Tests for reduce.py: compare brute-force answers on source and reduction."""

from __future__ import annotations

import random

import problems
from problems import ThreeColoring, IndependentSet
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    target = reduce(instance)
    IndependentSet.validate(target)
    expected = ThreeColoring.is_yes(instance)
    got = IndependentSet.is_yes(target)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"MISMATCH source={instance} expected={expected} "
            f"target={target} got={got}"
        )


def main():
    # 1. Exhaustive over all graphs on 0..5 vertices.
    for scale in range(0, 6):
        for instance in ThreeColoring.enumerate_instances(scale):
            check(instance)
    print(f"exhaustive scale<=5: {tests_run} run, {tests_passed} passed")

    # 2. Random small graphs, various sizes and edge probabilities.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
        edges = [
            [u, v]
            for u in range(n)
            for v in range(u + 1, n)
            if rng.random() < p
        ]
        check({"n": n, "edges": edges})
    print(f"after random: {tests_run} run, {tests_passed} passed")

    # 3. Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # K4 is not 3-colourable.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})
    # Odd cycle C5 is not 3-colourable? C5 IS 3-colourable. Use C5 yes.
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})
    # K5 is not 3-colourable.
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})
    print(f"after edge cases: {tests_run} run, {tests_passed} passed")

    # 4. Larger random instances (still brute-forceable, up to ~11 vertices).
    rng = random.Random(999)
    for _ in range(300):
        n = rng.randint(8, 11)
        p = rng.choice([0.15, 0.3, 0.45, 0.6])
        edges = [
            [u, v]
            for u in range(n)
            for v in range(u + 1, n)
            if rng.random() < p
        ]
        check({"n": n, "edges": edges})
    print(f"after larger random: {tests_run} run, {tests_passed} passed")

    assert tests_run == tests_passed
    print(f"ALL PASS: {tests_passed}/{tests_run}")


if __name__ == "__main__":
    main()
