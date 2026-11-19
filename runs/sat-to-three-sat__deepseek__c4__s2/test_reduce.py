"""Tests comparing brute-force SAT answers with brute-force 3-SAT answers
on the reductions produced by reduce.py."""

import itertools
import random

import problems
from reduce import reduce


def sat_solve(instance):
    """Brute-force solver for the SAT source problem."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) is true iff bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_solve(instance):
    """Brute-force solver for the 3-SAT target problem."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def check(instance):
    problems.SOURCE.validate(instance)
    reduced = reduce(instance)
    problems.TARGET.validate(reduced)
    expected = sat_solve(instance)
    got = three_sat_solve(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def random_instance(rng, max_vars=4, max_clauses=5, max_len=5):
    m = rng.randint(0, max_vars)
    n = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0

    # Fixed edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 2, "clauses": [[1, 2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},
        {"num_vars": 3, "clauses": [[1, 1, 2]]},          # duplicate literal
        {"num_vars": 3, "clauses": [[1, -1, 2]]},          # tautology
        {"num_vars": 3, "clauses": [[1, -1]]},             # tautology len 2
        {"num_vars": 3, "clauses": [[1, 1, 1]]},           # all same
        {"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]},
        {"num_vars": 2, "clauses": [[1], [2], [-1, -2]]},
        {"num_vars": 3, "clauses": [[1], [2], [3], [-1, -2, -3]]},
    ]
    for inst in fixed:
        check(inst)
        tests_run += 1
        tests_passed += 1

    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_instance(rng)
        check(inst)
        tests_run += 1
        tests_passed += 1

    # Larger random instances with more variables / longer clauses.
    rng = random.Random(999)
    for _ in range(300):
        inst = random_instance(rng, max_vars=6, max_clauses=8, max_len=8)
        check(inst)
        tests_run += 1
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
