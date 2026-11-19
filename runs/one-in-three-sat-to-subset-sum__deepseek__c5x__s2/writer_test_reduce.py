"""Brute-force solvers and randomized equivalence tests for the reduction."""

import random
from itertools import product

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in product((False, True), repeat=m):
        if all(bits[a - 1] + bits[b - 1] + bits[c - 1] == 1 for a, b, c in clauses):
            return True
    return False


def solve_subset_sum(instance):
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for x in instance["numbers"]:
        reachable |= {s + x for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation.

def random_instance(rng):
    m = rng.randint(0, 6)
    clauses = []
    if m >= 3:
        n_clauses = rng.randint(0, 5)
        for _ in range(n_clauses):
            clause = rng.sample(range(1, m + 1), 3)
            clauses.append(clause)
            # occasionally duplicate a clause
            if rng.random() < 0.2:
                clauses.append(list(clause))
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Fixed edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
    ]

    instances = list(fixed)
    for _ in range(400):
        instances.append(random_instance(rng))

    for inst in instances:
        SOURCE.validate(inst)
        expected = solve_one_in_three_sat(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)
        got = solve_subset_sum(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, "reduced", reduced)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
