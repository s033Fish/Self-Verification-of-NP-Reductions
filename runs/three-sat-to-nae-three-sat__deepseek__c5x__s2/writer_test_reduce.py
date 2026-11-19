"""Tests for reduce.py: compare brute-force answers on 3-SAT and its reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def sat_solve(instance) -> bool:
    """3-SAT: yes iff some assignment makes every clause have a true literal."""
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


def nae_solve(instance) -> bool:
    """NAE-3-SAT: yes iff every clause has a true and a false literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = [(lit > 0) == bits[abs(lit) - 1] for lit in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation helpers.

def all_clauses(m):
    """All valid 3-SAT clauses over variables 1..m (order-normalised)."""
    out = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, combo)])
    return out


def random_instance(rng, max_m=5, max_clauses=6):
    m = rng.randint(0, max_m)
    clauses = []
    if m >= 3:
        pool = all_clauses(m)
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(list(rng.choice(pool)))
    return {"num_vars": m, "clauses": clauses}


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(inst)
        except InvalidInstance as exc:
            failures.append(f"source invalid {inst}: {exc}")
            return
        red = reduce(inst)
        try:
            NaeThreeSat.validate(red)
        except InvalidInstance as exc:
            failures.append(f"target invalid for {inst}: {red}: {exc}")
            return
        a = sat_solve(inst)
        b = nae_solve(red)
        if a != b:
            failures.append(f"MISMATCH {inst} -> {red}: sat={a} nae={b}")
        else:
            tests_passed += 1

    # 1. Edge cases: no clauses, m = 0..6.
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []})

    # 2. Exhaustive: every single clause for m = 3, 4.
    for m in (3, 4):
        for c in all_clauses(m):
            check({"num_vars": m, "clauses": [c]})

    # 3. Exhaustive: all pairs of clauses for m = 3.
    pool3 = all_clauses(3)
    for c1 in pool3:
        for c2 in pool3:
            check({"num_vars": 3, "clauses": [c1, c2]})

    # 4. Exhaustive: all subsets of clauses for m = 3 is too many; use
    #    triples drawn from a reduced pool plus random sampling.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_instance(rng, max_m=5, max_clauses=7))

    # 5. Random instances with duplicated clauses and unused variables.
    for _ in range(1000):
        m = rng.randint(3, 6)
        pool = all_clauses(m)
        k = rng.randint(1, 5)
        chosen = [list(rng.choice(pool)) for _ in range(k)]
        if chosen and rng.random() < 0.5:
            chosen.append(list(rng.choice(chosen)))
        check({"num_vars": m, "clauses": chosen})

    # 6. Structured: unsatisfiable and satisfiable small formulas.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3],
                                      [1, -2, -3], [-1, 2, 3], [-1, 2, -3],
                                      [-1, -2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})

    # 7. Larger random stress instances (up to 8 vars, up to 12 clauses).
    for _ in range(1500):
        m = rng.randint(3, 8)
        pool = all_clauses(m)
        chosen = [list(rng.choice(pool)) for _ in range(rng.randint(1, 12))]
        check({"num_vars": m, "clauses": chosen})

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = run_tests()
    print(f"tests_run={run} tests_passed={passed} failures={len(fails)}")
    for f in fails[:20]:
        print("FAIL:", f)
    assert not fails, "some tests failed"
    print("ALL TESTS PASSED")
