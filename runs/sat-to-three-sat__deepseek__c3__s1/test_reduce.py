"""Tests for the SAT -> 3-SAT reduction in reduce.py."""

import random

import problems
from problems import Sat, ThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(instance)
    ThreeSat.validate(out)  # must be a well-formed 3-SAT instance
    expected = Sat.is_yes(instance)
    got = ThreeSat.is_yes(out)
    assert got == expected, (instance, out, expected, got)
    tests_passed += 1


def test_enumerated():
    # Exhaustive over all small SAT instances (num_vars <= 2).
    for instance in Sat.enumerate_instances(2):
        check(instance)


def test_random():
    rng = random.Random(12345)
    for scale in range(0, 7):
        for _ in range(120):
            check(Sat.random_instance(rng, scale))


def test_edge_cases():
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 0, "clauses": [[]]})
    check({"num_vars": 3, "clauses": []})
    check({"num_vars": 3, "clauses": [[]]})
    check({"num_vars": 1, "clauses": [[1]]})
    check({"num_vars": 1, "clauses": [[-1]]})
    check({"num_vars": 1, "clauses": [[1], [-1]]})
    check({"num_vars": 2, "clauses": [[1, 2]]})
    check({"num_vars": 2, "clauses": [[1, -1]]})  # tautology
    check({"num_vars": 2, "clauses": [[1, 1, 2]]})  # repeated literal
    check({"num_vars": 2, "clauses": [[1, -1, 2], [1], [-2]]})
    # Long clauses.
    check({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]})
    check({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]})
    check({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-1], [-2], [-3], [-4], [-5], [-6]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4], [1, -2, 3, -4]]})


def test_unsat():
    # Pigeonhole-ish / simple contradictions.
    check({"num_vars": 2, "clauses": [[1], [-1]]})
    check({"num_vars": 3, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]})
    check({"num_vars": 2, "clauses": [[]]})


if __name__ == "__main__":
    test_enumerated()
    test_random()
    test_edge_cases()
    test_unsat()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    print("ALL TESTS PASSED")
