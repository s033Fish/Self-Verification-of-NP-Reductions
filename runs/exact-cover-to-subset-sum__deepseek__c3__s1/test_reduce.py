"""Tests for the Exact Cover -> Subset Sum reduction."""
import random

import problems
from problems import ExactCover, SubsetSum
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = ExactCover.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    if expected == got:
        tests_passed += 1
        return True
    print("MISMATCH")
    print("  source :", instance)
    print("  reduced:", reduced)
    print("  expected:", expected, "got:", got)
    return False


def main():
    # 1. Exhaustive over all set systems with universe size <= 3 (256 instances).
    for instance in ExactCover.enumerate_instances(3):
        check(instance)

    # 2. Random instances across scales, including planted covers.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            instance = ExactCover.random_instance(rng, scale)
            check(instance)

    # 3. Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[], [0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0, 1], [2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3]]},
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [0, 3]]},
        {"universe_size": 5, "sets": [[0, 1, 2], [3, 4], [0], [1, 2, 3, 4]]},
    ]
    for instance in edge_cases:
        check(instance)

    # 4. Larger random instances to stress the no-carry property.
    for scale in range(10, 25):
        for _ in range(50):
            check(ExactCover.random_instance(rng, scale))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run == tests_passed


if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
