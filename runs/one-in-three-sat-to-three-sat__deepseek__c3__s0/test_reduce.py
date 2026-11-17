"""Tests for the 1-in-3-SAT -> 3-SAT reduction in reduce.py."""

import random

import problems
from reduce import reduce

SOURCE = problems.SOURCE
TARGET = problems.TARGET


def check(instance):
    """Validate source, reduce, validate target, compare yes/no."""
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    return SOURCE.is_yes(instance), TARGET.is_yes(out)


def main():
    tests_run = 0
    tests_passed = 0

    def record(ok):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            raise AssertionError("mismatch")

    # 1) Exhaustive over all distinct-clause 1-in-3-SAT formulas up to 4 vars.
    for instance in SOURCE.enumerate_instances(4):
        src, tgt = check(instance)
        record(src == tgt)

    # 2) Random instances across many scales.
    rng = random.Random(12345)
    for scale in range(0, 13):
        for _ in range(200):
            instance = SOURCE.random_instance(rng, scale)
            src, tgt = check(instance)
            record(src == tgt)

    # 3) Hand-picked edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        # Two clauses sharing two variables: unsat-ish / sat cases.
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        # Variables not all used.
        {"num_vars": 7, "clauses": [[1, 2, 3]]},
        {"num_vars": 7, "clauses": [[5, 6, 7]]},
    ]
    for instance in edge_cases:
        src, tgt = check(instance)
        record(src == tgt)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
