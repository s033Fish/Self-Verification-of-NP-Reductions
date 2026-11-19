"""Tests comparing brute-force answers on source instances and reductions."""

import random

import problems
from problems import IndependentSet, Clique
from reduce import reduce


def check(instance):
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)
    expected = IndependentSet.is_yes(instance)
    got = Clique.is_yes(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return 1


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances, including k = -1 and k = n + 1.
    for scale in range(0, 5):
        for instance in IndependentSet.enumerate_instances(scale):
            tests_run += 1
            check(instance)
            tests_passed += 1

    # Random instances, including edge-case k values.
    rng = random.Random(12345)
    for _ in range(3000):
        scale = rng.randint(0, 8)
        instance = IndependentSet.random_instance(rng, scale)
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Hand-picked edge cases.
    hand = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
    ]
    for instance in hand:
        tests_run += 1
        check(instance)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
