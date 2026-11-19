"""Tests comparing brute-force Partition and SubsetSum on reductions."""

from __future__ import annotations

import random

from problems import Partition, SubsetSum
from reduce import reduce


def check(instance: dict) -> bool:
    Partition.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = Partition.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    assert expected == got, (
        f"mismatch for {instance}: Partition={expected}, "
        f"reduced={reduced}, SubsetSum={got}"
    )
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances (values 0..3, lengths up to 6).
    for scale in range(0, 7):
        for instance in Partition.enumerate_instances(scale):
            tests_run += 1
            if check(instance):
                tests_passed += 1

    # Random instances across several scales and seeds.
    for seed in range(50):
        rng = random.Random(seed)
        for scale in range(0, 13):
            instance = Partition.random_instance(rng, scale)
            tests_run += 1
            if check(instance):
                tests_passed += 1

    # Explicit edge cases.
    edge_cases = [
        {"numbers": []},                 # empty: yes
        {"numbers": [0]},                # zero: yes
        {"numbers": [0, 0, 0]},          # zeros: yes
        {"numbers": [1]},                # odd total: no
        {"numbers": [1, 2]},             # odd total: no
        {"numbers": [2, 2]},             # yes
        {"numbers": [1, 1, 1, 1]},       # yes
        {"numbers": [3, 1, 1, 1]},       # yes (3 vs 1+1+1)
        {"numbers": [5, 5, 5]},          # odd total: no
        {"numbers": [10**18, 10**18]},   # large values: yes
        {"numbers": [10**18 + 1, 10**18]},  # large odd total: no
    ]
    for instance in edge_cases:
        tests_run += 1
        if check(instance):
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
