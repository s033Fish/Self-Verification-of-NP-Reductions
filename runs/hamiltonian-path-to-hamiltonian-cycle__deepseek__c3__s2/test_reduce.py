"""Tests for the Hamiltonian Path -> Hamiltonian Cycle reduction."""
import random

import problems
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

SOURCE = problems.SOURCE
TARGET = problems.TARGET

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, target={got}, reduced={reduced}"
    )
    tests_passed += 1


def main():
    # Exhaustive over every graph with up to 6 vertices.
    for instance in SOURCE.enumerate_instances(6):
        check(instance)

    # Random larger instances (still small enough for the brute-force solvers).
    rng = random.Random(12345)
    for _ in range(300):
        scale = rng.randint(0, 9)
        check(SOURCE.random_instance(rng, scale))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
