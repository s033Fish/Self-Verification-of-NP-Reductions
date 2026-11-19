"""Brute-force solvers and randomized tests for the SAT -> 3-SAT reduction."""

import itertools
import random

import problems
from reduce import reduce


def sat_solve(instance):
    """Brute-force SAT solver following the SOURCE definition."""
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


def three_sat_solve(instance):
    """Brute-force 3-SAT solver following the TARGET definition."""
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


def random_sat_instance(rng, max_vars=4, max_clauses=5, max_len=4):
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


def check(instance, tests):
    tests[0] += 1
    problems.Sat.validate(instance)
    out = reduce(instance)
    problems.ThreeSat.validate(out)
    expected = sat_solve(instance)
    got = three_sat_solve(out)
    if expected != got:
        raise AssertionError(
            f"MISMATCH on {instance!r}: source={expected}, reduced={got}, out={out!r}"
        )
    tests[1] += 1


def main():
    tests = [0, 0]

    # Hand-picked edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},          # tautology
        {"num_vars": 2, "clauses": [[1, 2]]},
        {"num_vars": 2, "clauses": [[1], [2]]},
        {"num_vars": 2, "clauses": [[1, 1, 1]]},        # duplicates
        {"num_vars": 2, "clauses": [[1, -1, 2]]},       # tautology + dup
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]},
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-6, -5, -4, -3, -2, -1]]},
        {"num_vars": 3, "clauses": [[1, 2], [3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [1], [-1]]},  # unsat
        {"num_vars": 2, "clauses": [[1], [-1], [2]]},           # unsat
    ]
    for inst in fixed:
        check(inst, tests)

    # Randomized tests.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_sat_instance(rng), tests)

    # Larger random instances (up to 6 vars, longer clauses).
    for _ in range(1500):
        check(random_sat_instance(rng, max_vars=6, max_clauses=6, max_len=6), tests)

    # Exhaustive-ish: all clause sets over 2 vars with clauses up to len 3.
    lits = [1, -1, 2, -2]
    pool = [[]] + [[a] for a in lits] + [[a, b] for a in lits for b in lits] + \
           [[a, b, c] for a in lits for b in lits for c in lits]
    for _ in range(3000):
        n = rng.randint(0, 4)
        inst = {"num_vars": 2, "clauses": [rng.choice(pool) for _ in range(n)]}
        check(inst, tests)

    print(f"tests_run={tests[0]} tests_passed={tests[1]}")
    assert tests[0] == tests[1]
    return tests


if __name__ == "__main__":
    main()
