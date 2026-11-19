"""Tests for reduce.py: compare SAT brute force with Independent Set brute force."""

import random

import problems
from problems import Sat, IndependentSet
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Sat.validate(instance)
    target = reduce(instance)
    # The reduction must produce a valid target instance.
    IndependentSet.validate(target)
    expected = Sat.is_yes(instance)
    got = IndependentSet.is_yes(target)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} got={got} target={target}"
    )
    tests_passed += 1


def main():
    # Exhaustive over all formulas with num_vars <= 2 (clauses distinct, each
    # variable used at most once per clause), including empty clauses.
    for instance in Sat.enumerate_instances(2):
        check(instance)

    # Random small instances across many scales.
    rng = random.Random(12345)
    for scale in range(0, 7):
        for _ in range(300):
            check(Sat.random_instance(rng, scale))

    # Hand-crafted edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},              # yes
        {"num_vars": 0, "clauses": [[]]},            # no
        {"num_vars": 3, "clauses": []},              # yes
        {"num_vars": 3, "clauses": [[]]},            # no
        {"num_vars": 1, "clauses": [[1]]},           # yes
        {"num_vars": 1, "clauses": [[-1]]},          # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},     # no
        {"num_vars": 1, "clauses": [[1, -1]]},       # yes
        {"num_vars": 2, "clauses": [[1, 1], [-1]]},  # no
        {"num_vars": 2, "clauses": [[1, 1]]},        # yes
        {"num_vars": 2, "clauses": [[1], [2], [-1, -2]]},  # yes
        {"num_vars": 2, "clauses": [[1], [2], [-1], [-2]]},  # no
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2], [-3]]},  # yes
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
