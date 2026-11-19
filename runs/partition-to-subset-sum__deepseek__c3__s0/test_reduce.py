"""Tests for the Partition -> Subset Sum reduction in reduce.py."""

from __future__ import annotations

import random

from problems import SOURCE, TARGET
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)  # reduction must produce a valid target instance
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected != got:
        raise AssertionError(
            f"mismatch for {instance!r}: reduced={reduced!r}, "
            f"source={expected}, target={got}"
        )
    TESTS_PASSED += 1


def main():
    # 1. Exhaustive small instances (values 0..3, lengths up to 6).
    for instance in SOURCE.enumerate_instances(6):
        check(instance)

    # 2. Random instances at several scales, both yes and no.
    rng = random.Random(12345)
    for scale in range(0, 13):
        for _ in range(300):
            check(SOURCE.random_instance(rng, scale))

    # 3. Explicit edge cases.
    edge_cases = [
        {"numbers": []},                 # empty: yes
        {"numbers": [0]},                # yes
        {"numbers": [0, 0, 0]},          # yes
        {"numbers": [1]},                # odd total: no
        {"numbers": [1, 2]},             # odd total: no
        {"numbers": [2, 2]},             # yes
        {"numbers": [1, 1, 1, 1]},       # yes
        {"numbers": [1, 1, 1]},          # odd: no
        {"numbers": [3, 1, 1, 1]},       # yes (3 vs 1+1+1)
        {"numbers": [5, 5, 5, 5]},       # yes
        {"numbers": [1000000000000, 1000000000000]},  # yes, big ints
        {"numbers": [10 ** 30, 1]},      # odd total: no
        {"numbers": [0, 7, 7]},          # yes
        {"numbers": [2, 4, 6]},          # yes (6 vs 2+4)
        {"numbers": [2, 4, 7]},          # odd: no
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
