"""Tests for the Exact Cover -> SAT reduction."""

import random

import problems
from problems import ExactCover, Sat
from reduce import reduce


def check(instance):
    """Return (source_yes, target_yes) for one source instance."""
    reduced = reduce(instance)
    ExactCover.validate(instance)
    Sat.validate(reduced)
    return ExactCover.is_yes(instance), Sat.is_yes(reduced)


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src, tgt = check(instance)
        if src == tgt:
            tests_passed += 1
        else:
            print(f"FAIL {label}: source={src} target={tgt} instance={instance} "
                  f"reduced={reduce(instance)}")

    # 1. Exhaustive enumeration of all set systems up to scale 3.
    for instance in ExactCover.enumerate_instances(3):
        run(instance, "enumerate3")

    # 2. Exhaustive enumeration up to scale 4 (65536 systems) -- good coverage.
    count = 0
    for instance in ExactCover.enumerate_instances(4):
        run(instance, "enumerate4")
        count += 1
        if count >= 20000:
            break

    # 3. Random instances across many scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            instance = ExactCover.random_instance(rng, scale)
            run(instance, f"random scale={scale}")

    # 4. Hand-crafted edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 1, 2, 3]]},
        {"universe_size": 4, "sets": [[0], [1], [2], [3], [0, 1], [2, 3]]},
        {"universe_size": 5, "sets": [[0, 1, 2], [3, 4], [0, 3], [1, 4], [2]]},
        {"universe_size": 3, "sets": [[0, 1], [0, 1], [2]]},
        {"universe_size": 3, "sets": [[], [0], [1], [2]]},
    ]
    for instance in edge_cases:
        run(instance, "edge")

    # 5. Larger random instances where brute force is still feasible.
    rng = random.Random(999)
    for scale in range(6, 13):
        for _ in range(40):
            instance = ExactCover.random_instance(rng, scale)
            run(instance, f"larger scale={scale}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    run_count, pass_count = main()
    assert run_count == pass_count, "some tests failed"
    print("ALL TESTS PASSED")
