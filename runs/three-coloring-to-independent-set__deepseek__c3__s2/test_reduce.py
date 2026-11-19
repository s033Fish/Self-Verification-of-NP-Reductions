"""Tests for the 3-Coloring -> Independent Set reduction."""
import random
import sys

from problems import ThreeColoring, IndependentSet
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(instance)
    # Output must be a valid target instance.
    IndependentSet.validate(out)
    expected = ThreeColoring.is_yes(instance)
    got = IndependentSet.is_yes(out)
    assert got == expected, (
        f"mismatch for {instance}: source={expected}, target={got}, reduced={out}"
    )
    tests_passed += 1


def main():
    # 1. Exhaustive: every graph on 0..6 vertices.
    for instance in ThreeColoring.enumerate_instances(6):
        check(instance)
    print(f"exhaustive up to n=6 done: {tests_passed}/{tests_run}")

    # 2. Random instances at various scales.
    rng = random.Random(12345)
    for scale in range(0, 13):
        for _ in range(200):
            instance = ThreeColoring.random_instance(rng, scale)
            check(instance)
    print(f"random done: {tests_passed}/{tests_run}")

    # 3. Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},                       # yes
        {"n": 1, "edges": []},                       # yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, # triangle, yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]},  # K4, no
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5, yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # C4, yes
    ]
    for instance in edge_cases:
        check(instance)
    print(f"edge cases done: {tests_passed}/{tests_run}")

    assert tests_run == tests_passed, f"{tests_run - tests_passed} tests failed"
    print(f"ALL {tests_passed} TESTS PASSED")


if __name__ == "__main__":
    main()
