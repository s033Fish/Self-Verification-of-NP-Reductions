"""Tests comparing brute-force answers on small 1-in-3-SAT instances."""

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ---------------------------------------------------------------- solvers
def solve_one_in_three_sat(instance):
    """Brute force over all assignments of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            true_count = sum(1 for var in clause if bits[var - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    """Brute force over all sub-lists."""
    numbers = instance["numbers"]
    target = instance["target"]
    for mask in range(1 << len(numbers)):
        total = 0
        for i, number in enumerate(numbers):
            if mask & (1 << i):
                total += number
        if total == target:
            return True
    return False


# ---------------------------------------------------------------- helpers
def all_instances(max_vars, max_clauses):
    """Enumerate small valid instances (variable order normalised)."""
    for num_vars in range(0, max_vars + 1):
        if num_vars < 3:
            # A formula with clauses needs m >= 3, so only the empty
            # clause list is valid here.
            yield {"num_vars": num_vars, "clauses": []}
            continue
        clause_choices = list(itertools.combinations(range(1, num_vars + 1), 3))
        for num_clauses in range(0, max_clauses + 1):
            for clauses in itertools.product(clause_choices, repeat=num_clauses):
                yield {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


def random_instance(rng, max_vars, max_clauses):
    num_vars = rng.randint(0, max_vars)
    if num_vars < 3:
        return {"num_vars": num_vars, "clauses": []}
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause = rng.sample(range(1, num_vars + 1), 3)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        OneInThreeSat.validate(instance)
        reduced = reduce(instance)
        SubsetSum.validate(reduced)
        expected = solve_one_in_three_sat(instance)
        got = solve_subset_sum(reduced)
        assert got == expected, (instance, reduced, expected, got)
        tests_passed += 1

    # Exhaustive small instances.
    for instance in all_instances(max_vars=4, max_clauses=3):
        check(instance)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(300):
        check(random_instance(rng, max_vars=7, max_clauses=5))

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4], [1, 3, 4]]})

    # A few known satisfiable / unsatisfiable formulas.
    # Exactly-one-of-three on x1,x2,x3 plus its negation-like constraints:
    # (x1,x2,x3) and (x1,x2,x4) and (x1,x3,x4) and (x2,x3,x4) is unsat.
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
