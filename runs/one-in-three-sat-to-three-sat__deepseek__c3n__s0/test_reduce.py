"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce
from solvers import solve_one_in_three, solve_three_sat

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1

    # Both the source and the reduced instance must be valid.
    OneInThreeSat.validate(instance)
    reduced = reduce(instance)
    ThreeSat.validate(reduced)

    expected = solve_one_in_three(instance)
    actual = solve_three_sat(reduced)
    assert expected == actual, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} actual={actual}"
    )
    tests_passed += 1


def all_instances(m: int, max_clauses: int = 3):
    """Enumerate small 1-in-3-SAT instances over variables 1..m."""
    triples = list(itertools.combinations(range(1, m + 1), 3))
    for r in range(0, max_clauses + 1):
        for combo in itertools.combinations_with_replacement(triples, r):
            yield {"num_vars": m, "clauses": [list(t) for t in combo]}


def main() -> None:
    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})

    # Exhaustive small instances.
    for m in range(0, 5):
        for instance in all_instances(m, max_clauses=3):
            check(instance)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(300):
        m = rng.randint(3, 8)
        n = rng.randint(1, 8)
        clauses = []
        for _ in range(n):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
        check({"num_vars": m, "clauses": clauses})

    # Random instances with repeated clauses and unused variables.
    for _ in range(200):
        m = rng.randint(3, 7)
        n = rng.randint(1, 6)
        clauses = []
        for _ in range(n):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
        if clauses and rng.random() < 0.5:
            clauses.append(list(clauses[0]))
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
