"""Brute-force solvers and randomized tests for the 3-SAT -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_three_sat(instance):
    """Try every assignment of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = {v + 1: bits[v] for v in range(num_vars)}
        if all(
            any(assignment[abs(lit)] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_subset_sum(instance):
    """Dynamic programming over reachable sums."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in instance["numbers"]:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation.


def random_three_sat(rng, max_vars=5, max_clauses=6):
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    if num_clauses > 0 and num_vars < 3:
        num_vars = 3
    clauses = []
    for _ in range(num_clauses):
        variables = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Hand-picked edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 4], [1, -3, -4]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, 2, -3], [-1, -2, 3]]},
    ]

    instances = list(edge_cases)
    for _ in range(400):
        instances.append(random_three_sat(rng))

    for instance in instances:
        SOURCE.validate(instance)
        expected = solve_three_sat(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        got = solve_subset_sum(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("  source:", instance)
            print("  expected:", expected)
            print("  reduced:", reduced)
            print("  got:", got)
            raise SystemExit(1)

    print(f"all {tests_run} tests passed")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
