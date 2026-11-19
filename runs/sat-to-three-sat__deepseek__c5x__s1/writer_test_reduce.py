"""Tests for reduce.py: brute-force solvers + randomized equivalence checks."""

import itertools
import random

from problems import Sat, ThreeSat
from reduce import reduce


def solve_cnf(instance):
    """Brute-force solver for both SAT and 3-SAT instance formats."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def random_sat_instance(rng, max_vars=4, max_clauses=4, max_len=4):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        k = rng.randint(0, max_len)
        clause = []
        for _ in range(k):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0

    def check(cond, msg):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            print("FAIL:", msg)

    # Hand-picked edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 2, "clauses": [[1]]},
        {"num_vars": 2, "clauses": [[-1]]},
        {"num_vars": 2, "clauses": [[1], [-1]]},
        {"num_vars": 2, "clauses": [[1, 2]]},
        {"num_vars": 2, "clauses": [[1, -1]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
        {"num_vars": 5, "clauses": [[1, 1, 2, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, -1]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, -1]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [1], [-1]]},
    ]
    for inst in edge:
        Sat.validate(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        check(solve_cnf(inst) == solve_cnf(red), f"edge mismatch {inst} -> {red}")

    # Randomized tests (small enough that brute force over the reduced
    # formula's fresh variables stays cheap).
    rng = random.Random(12345)
    for _ in range(600):
        inst = random_sat_instance(rng)
        Sat.validate(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        check(solve_cnf(inst) == solve_cnf(red), f"mismatch {inst} -> {red}")

    # Slightly larger source instances, but avoid too many empty clauses.
    rng2 = random.Random(999)
    for _ in range(200):
        inst = random_sat_instance(rng2, max_vars=5, max_clauses=3, max_len=5)
        Sat.validate(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        check(solve_cnf(inst) == solve_cnf(red), f"mismatch {inst} -> {red}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
