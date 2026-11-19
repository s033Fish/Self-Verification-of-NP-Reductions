"""Brute-force solvers and tests for the 1-in-3-SAT -> 3-SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(1 for v in clause if bits[v - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                for l in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_1in3_instances(m, max_clauses):
    """All 1-in-3-SAT instances over variables 1..m with up to max_clauses."""
    triples = list(itertools.combinations(range(1, m + 1), 3))
    for k in range(0, max_clauses + 1):
        for chosen in itertools.combinations_with_replacement(triples, k):
            yield {"num_vars": m, "clauses": [list(t) for t in chosen]}


def random_1in3_instance(rng, m, max_clauses):
    triples = list(itertools.combinations(range(1, m + 1), 3))
    k = rng.randint(0, max_clauses) if triples else 0
    clauses = [list(rng.choice(triples)) for _ in range(k)] if triples else []
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        OneInThreeSat.validate(instance)
        reduced = reduce(instance)
        ThreeSat.validate(reduced)
        expected = solve_one_in_three(instance)
        got = solve_three_sat(reduced)
        if expected != got:
            raise AssertionError(
                f"MISMATCH source={instance} expected={expected} "
                f"reduced={reduced} got={got}"
            )
        tests_passed += 1

    # Exhaustive over small formulas.
    for m in (0, 1, 2, 3):
        for inst in all_1in3_instances(m, 2 if m <= 2 else 2):
            check(inst)

    # Random larger formulas.
    rng = random.Random(12345)
    for _ in range(300):
        m = rng.randint(3, 4)
        check(random_1in3_instance(rng, m, 3))

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})

    # Determinism / polynomial size sanity.
    inst = {"num_vars": 10, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    r1 = reduce(inst)
    r2 = reduce(inst)
    assert r1 == r2
    assert len(r1["clauses"]) == 7 * len(inst["clauses"])
    assert r1["num_vars"] == inst["num_vars"] + 3 * len(inst["clauses"])

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
