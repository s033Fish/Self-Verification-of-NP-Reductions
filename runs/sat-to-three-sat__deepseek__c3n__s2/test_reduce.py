"""Tests for reduce.py: brute-force solvers + random comparison."""

import random
import sys

from problems import Sat, ThreeSat
from reduce import reduce


def solve(instance: dict) -> bool:
    """Brute-force CNF satisfiability solver (works for SAT and 3-SAT)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        good = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit)
                bit = (mask >> (var - 1)) & 1
                if (lit > 0 and bit == 1) or (lit < 0 and bit == 0):
                    satisfied = True
                    break
            if not satisfied:
                good = False
                break
        if good:
            return True
    return False


def random_sat_instance(rng, max_vars=5, max_clauses=7, max_len=5):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        k = rng.randint(0, max_len)
        if m == 0:
            clause = []
        else:
            clause = [rng.choice([-1, 1]) * rng.randint(1, m) for _ in range(k)]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(inst)
            out = reduce(inst)
            ThreeSat.validate(out)
            a = solve(inst)
            b = solve(out)
            if a == b:
                tests_passed += 1
            else:
                failures.append((label, inst, out, a, b))
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, repr(exc), None, None))

    # --- explicit edge cases -------------------------------------------
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 0, "clauses": [[]]}, "m=0 empty clause")
    check({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    check({"num_vars": 1, "clauses": [[]]}, "m=1 empty clause")
    check({"num_vars": 3, "clauses": []}, "m=3 no clauses")
    check({"num_vars": 1, "clauses": [[1]]}, "unit true")
    check({"num_vars": 1, "clauses": [[-1]]}, "unit false")
    check({"num_vars": 1, "clauses": [[1], [-1]]}, "contradiction")
    check({"num_vars": 2, "clauses": [[1, 2]]}, "two-literal")
    check({"num_vars": 2, "clauses": [[1, 2], [-1, -2]]}, "two 2-lit")
    check({"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]}, "unsat 2var")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "already 3-lit")
    check({"num_vars": 3, "clauses": [[1, -1, 2]]}, "tautology clause")
    check({"num_vars": 3, "clauses": [[1, 1, 2]]}, "duplicate literal")
    check({"num_vars": 3, "clauses": [[1, 1, 1]]}, "all duplicate")
    check({"num_vars": 4, "clauses": [[1, 2, 3, 4]]}, "4-lit")
    check({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]}, "5-lit")
    check({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]}, "two 5-lit")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 4, "clauses": [[1, 2, -1, 3], [-2, 4]]}, "mixed")
    check({"num_vars": 6, "clauses": [[1], [2, 3], [4, 5, 6], [1, 2, 3, 4, 5, 6]]}, "all lengths")

    # --- random tests ---------------------------------------------------
    for i in range(3000):
        inst = random_sat_instance(rng)
        check(inst, f"random {i}")

    # larger random instances
    for i in range(300):
        inst = random_sat_instance(rng, max_vars=8, max_clauses=12, max_len=8)
        check(inst, f"random-large {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
