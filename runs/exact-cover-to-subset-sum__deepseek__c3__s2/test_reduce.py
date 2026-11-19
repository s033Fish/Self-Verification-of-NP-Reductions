import random

import problems
from problems import ExactCover, SubsetSum
from reduce import reduce


def check(instance):
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = ExactCover.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    assert got == expected, (instance, reduced, expected, got)
    return True


def main():
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive small instances (all collections of subsets, u <= 3).
    for instance in ExactCover.enumerate_instances(3):
        tests_run += 1
        check(instance)
        tests_passed += 1

    # 2. Random instances over a range of scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            instance = ExactCover.random_instance(rng, scale)
            ExactCover.validate(instance)
            tests_run += 1
            check(instance)
            tests_passed += 1

    # 3. Hand-made edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[], []]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2], [0], [1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        {"universe_size": 4, "sets": [[0, 1, 2, 3]]},
        {"universe_size": 4, "sets": [[0, 1, 2], [3], [0], [1, 2, 3]]},
        {"universe_size": 5, "sets": [[0, 1], [2, 3], [4], [0], [1, 2, 3, 4]]},
    ]
    for instance in edge_cases:
        ExactCover.validate(instance)
        tests_run += 1
        check(instance)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
