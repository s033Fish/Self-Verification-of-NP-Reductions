"""Tests for reduce.py: compare brute-force answers on small instances."""

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three(instance):
    """True iff exactly one variable in every clause is true."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return True  # no assignment fails -> satisfiable (also covers m == 0, no clauses)


def solve_three_sat(instance):
    """True iff every clause has at least one true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return True


# ----------------------------------------------------------------------
# Instance generation

def random_source(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    n = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n):
        clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    instances = []

    # Edge cases
    instances.append({"num_vars": 0, "clauses": []})
    instances.append({"num_vars": 3, "clauses": []})
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3]]})
    instances.append({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3]]})
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})

    # Random small instances
    for _ in range(400):
        instances.append(random_source(rng))

    for src in instances:
        tests_run += 1
        problems.OneInThreeSat.validate(src)
        tgt = reduce(src)
        problems.ThreeSat.validate(tgt)

        expected = solve_one_in_three(src)
        got = solve_three_sat(tgt)
        if expected != got:
            print("MISMATCH")
            print("source:", src, "expected", expected)
            print("target:", tgt, "got", got)
            continue
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
