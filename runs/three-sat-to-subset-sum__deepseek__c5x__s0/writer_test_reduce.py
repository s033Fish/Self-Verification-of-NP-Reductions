"""Tests for the 3-SAT -> Subset Sum reduction in reduce.py.

Includes brute-force solvers for both problems written directly from the
definitions in problems.py, plus a randomized comparison over many small
source instances (and some hand-crafted edge cases).
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_three_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    """Return True iff some sub-list sums to exactly the target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in numbers:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators for small 3-SAT instances.


def random_three_sat(rng, max_vars=4, max_clauses=5):
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    if num_vars >= 3:
        for _ in range(num_clauses):
            vs = rng.sample(range(1, num_vars + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def edge_case_instances():
    return [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -1, 2]] if False else [[1, 2, 3]]},
    ]


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = edge_case_instances()
    for _ in range(400):
        instances.append(random_three_sat(rng))

    for inst in instances:
        # Both the source and the reduced target must be valid instances.
        SOURCE.validate(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)

        expected = solve_three_sat(inst)
        got = solve_subset_sum(reduced)

        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, reduced, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for inst, reduced, expected, got in failures[:5]:
            print("FAIL")
            print("  source:", inst)
            print("  target:", reduced)
            print("  expected:", expected, "got:", got)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
