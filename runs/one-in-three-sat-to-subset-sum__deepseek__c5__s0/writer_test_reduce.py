"""Tests for reduce.py: brute-force solvers + random/edge-case comparison."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


def solve_one_in_three(instance):
    """Brute force 1-in-3-SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(sum(1 for v in clause if bits[v - 1]) == 1 for clause in clauses):
            return True
    return False


def solve_subset_sum(instance):
    """Brute force Subset Sum via reachable-sum DP."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in instance["numbers"]:
        reachable |= {s + a for s in reachable}
    return target in reachable


def random_instance(rng):
    m = rng.randint(0, 6)
    n = rng.randint(0, 6)
    clauses = []
    for _ in range(n):
        if m < 3:
            break
        clause = rng.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(src, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        OneInThreeSat.validate(src)
        tgt = reduce(src)
        SubsetSum.validate(tgt)
        expected = solve_one_in_three(src)
        got = solve_subset_sum(tgt)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, src, tgt, expected, got))

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 1]]}, "small sat")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "repeated clause")
    check({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]}, "two disjoint")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "triple repeat")

    # Randomized tests.
    rng = random.Random(12345)
    for k in range(3000):
        check(random_instance(rng), f"random #{k}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for label, src, tgt, expected, got in failures[:10]:
        print("FAIL", label, src, tgt, expected, got)
    assert not failures, f"{len(failures)} failures"

    with open("verdict.json", "w") as fh:
        import json
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    print("verdict.json written")


if __name__ == "__main__":
    main()
