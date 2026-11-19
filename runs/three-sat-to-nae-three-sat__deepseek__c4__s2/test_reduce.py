"""Brute-force solvers and randomized tests for the 3-SAT -> NAE-3-SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def _lit_true(lit: int, assignment: dict) -> bool:
    return assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)]


def sat_solve(instance: dict) -> bool:
    """True iff some assignment makes every 3-SAT clause have a true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        a = {v: bits[v - 1] for v in range(1, m + 1)}
        if all(any(_lit_true(l, a) for l in c) for c in clauses):
            return True
    return False


def nae_solve(instance: dict) -> bool:
    """True iff some assignment makes every clause have a true and a false literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        a = {v: bits[v - 1] for v in range(1, m + 1)}
        ok = True
        for c in clauses:
            vals = [_lit_true(l, a) for l in c]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def random_sat_instance(rng: random.Random, max_vars: int = 5, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    k = rng.randint(0, max_clauses)
    if k > 0:
        m = max(m, 3)
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_sat_instances(max_vars: int = 4):
    """All 3-SAT instances with up to max_vars variables and up to 2 clauses."""
    for m in range(0, max_vars + 1):
        if m < 3:
            clause_pool = []
        else:
            clause_pool = []
            for vs in itertools.combinations(range(1, m + 1), 3):
                for signs in itertools.product([1, -1], repeat=3):
                    clause_pool.append([v * s for v, s in zip(vs, signs)])
        yield {"num_vars": m, "clauses": []}
        for c1 in clause_pool:
            yield {"num_vars": m, "clauses": [list(c1)]}
            for c2 in clause_pool:
                yield {"num_vars": m, "clauses": [list(c1), list(c2)]}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        out = reduce(instance)
        NaeThreeSat.validate(out)
        expected = sat_solve(instance)
        got = nae_solve(out)
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", instance, "->", out, "expected", expected, "got", got)

    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})

    # Exhaustive small instances.
    for inst in exhaustive_sat_instances(max_vars=4):
        check(inst)

    # Random instances.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_sat_instance(rng, max_vars=6, max_clauses=6))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
