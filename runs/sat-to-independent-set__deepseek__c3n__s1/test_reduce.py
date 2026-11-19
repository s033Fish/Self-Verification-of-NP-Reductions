"""Tests for the SAT -> Independent Set reduction.

Contains brute-force solvers for both problems (from the definitions in
problems.py) and compares them on many small source instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def sat_solve(instance):
    """Brute force SAT: try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[i-1] is the value of variable i
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def independent_set_solve(instance):
    """Brute force Independent Set: try every subset of vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if not any(u in s and v in s for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    problems.SOURCE.validate(instance)
    reduced = reduce(instance)
    problems.TARGET.validate(reduced)
    expected = sat_solve(instance)
    got = independent_set_solve(reduced)
    if expected == got:
        tests_passed += 1
    else:
        failures.append((label, instance, reduced, expected, got))


def random_cnf(num_vars, num_clauses, max_len=3, rng=None):
    rng = rng or random
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            v = rng.randint(1, num_vars) if num_vars > 0 else 0
            if v == 0:
                continue
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []}, "empty formula")
    check({"num_vars": 0, "clauses": [[]]}, "empty clause only")
    check({"num_vars": 3, "clauses": []}, "no clauses")
    check({"num_vars": 1, "clauses": [[1], [-1]]}, "contradiction")
    check({"num_vars": 1, "clauses": [[1, 1], [1]]}, "repeated literals")
    check({"num_vars": 1, "clauses": [[1, -1]]}, "tautology clause")
    check({"num_vars": 2, "clauses": [[1, -1], [2, -2]]}, "two tautologies")
    check({"num_vars": 2, "clauses": [[1], [2]]}, "unit clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "3sat")
    check({"num_vars": 2, "clauses": [[1, 2], [1, 2]]}, "duplicate clause")
    check({"num_vars": 4, "clauses": [[1, -2], [-1, 2], [3, 4], [-3, -4]]}, "mixed")

    # Exhaustive small instances.
    rng = random.Random(12345)
    for num_vars in range(0, 4):
        for num_clauses in range(0, 4):
            for _ in range(60):
                check(
                    random_cnf(num_vars, num_clauses, max_len=3, rng=rng),
                    f"random m={num_vars} c={num_clauses}",
                )

    # A few larger random instances (still brute-forceable).
    for _ in range(40):
        check(random_cnf(5, 5, max_len=3, rng=rng), "random m=5 c=5")
    for _ in range(20):
        check(random_cnf(6, 4, max_len=4, rng=rng), "random m=6 c=4")

    # Larger clauses (longer than 3) and many repeats.
    for _ in range(30):
        check(random_cnf(4, 3, max_len=6, rng=rng), "long clauses")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for label, instance, reduced, expected, got in failures:
        print("FAIL", label, instance, "->", reduced, "expected", expected, "got", got)

    import json

    verdict = {
        "verified": tests_run > 0 and tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
