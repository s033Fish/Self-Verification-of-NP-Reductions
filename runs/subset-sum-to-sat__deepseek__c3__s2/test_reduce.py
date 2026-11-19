"""Tests: compare brute-force solvers on source instances and reductions."""

import random
import sys

from problems import SubsetSum, Sat
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    SubsetSum.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)  # must be a valid Sat instance
    expected = SubsetSum.is_yes(instance)
    got = Sat.is_yes(reduced)
    if expected != got:
        FAILURES.append((instance, expected, got))
        return False
    TESTS_PASSED += 1
    return True


def main():
    ok = True

    # 1. Exhaustive small instances.
    for scale in range(5):
        for instance in SubsetSum.enumerate_instances(scale):
            ok &= check(instance)

    # 2. Random instances at several scales.
    rng = random.Random(12345)
    for scale in range(0, 11):
        for _ in range(200):
            instance = SubsetSum.random_instance(rng, scale)
            ok &= check(instance)

    # 3. Explicit edge cases.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -5},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [5], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [2, 2, 2], "target": 4},
        {"numbers": [2, 2, 2], "target": 5},
        {"numbers": [10**18, 1], "target": 10**18 + 1},
        {"numbers": [10**18, 1], "target": 10**18},
        {"numbers": [10**18, 1], "target": 10**18 + 2},
        {"numbers": [7, 7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7, 7], "target": 22},
    ]
    for instance in edge:
        ok &= check(instance)

    for inst, exp, got in FAILURES[:10]:
        print("MISMATCH", inst, "expected", exp, "got", got)
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    return 0 if ok and TESTS_RUN == TESTS_PASSED else 1


if __name__ == "__main__":
    sys.exit(main())
