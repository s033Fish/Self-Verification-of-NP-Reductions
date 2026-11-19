"""Independent verification of reduce.py (3-SAT -> NAE-3-SAT).

Brute-force solvers for both problems are written straight from the
docstrings.  We generate many small source instances (exhaustive for m=3,
random otherwise, plus edge cases), reduce each one, validate the result
against TARGET.validate, and compare the truth values.

Sizes are kept small because the reduction adds one variable per source
clause, and the brute-force NAE solver is exponential in the target's
variable count.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat, InvalidInstance
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def brute_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every 3-SAT clause."""
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
    return False


def brute_nae_three_sat(instance: dict) -> bool:
    """True iff some assignment makes every clause not-all-equal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            values = [(lit > 0) == bits[abs(lit) - 1] for lit in clause]
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_clauses(m: int):
    """All valid 3-literal clauses over variables 1..m (distinct vars)."""
    result = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            result.append([s * v for s, v in zip(signs, vars_)])
    return result


def random_instance(rng: random.Random, max_vars: int = 5, max_clauses: int = 4):
    m = rng.randint(0, max_vars)
    n = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        pool = all_clauses(m)
        for _ in range(n):
            clauses.append(list(rng.choice(pool)))
    return {"num_vars": m, "clauses": clauses}


def exhaustive_m3():
    """Every subset of the 8 clauses over variables {1,2,3}."""
    pool = all_clauses(3)
    for r in range(len(pool) + 1):
        for combo in itertools.combinations(pool, r):
            yield {"num_vars": 3, "clauses": [list(c) for c in combo]}


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(src, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(src)
        except InvalidInstance as exc:
            failures.append((label, src, f"invalid source: {exc}"))
            return
        tgt = reduce_mod.reduce(src)
        try:
            NaeThreeSat.validate(tgt)
        except InvalidInstance as exc:
            failures.append((label, src, f"invalid target: {exc} -> {tgt}"))
            return
        src_ans = brute_three_sat(src)
        tgt_ans = brute_nae_three_sat(tgt)
        if src_ans != tgt_ans:
            failures.append((label, src, f"mismatch src={src_ans} tgt={tgt_ans} -> {tgt}"))
            return
        tests_passed += 1

    # Edge cases: no clauses for m = 0..5.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []}, f"empty-m{m}")

    # Exhaustive over all clause subsets for m = 3 (256 instances).
    for src in exhaustive_m3():
        check(src, "exhaustive-m3")

    # Exhaustive over all clause subsets for m = 4 using a small pool.
    pool4 = all_clauses(4)
    rng = random.Random(999)
    for _ in range(600):
        n = rng.randint(0, 3)
        clauses = [list(rng.choice(pool4)) for _ in range(n)]
        check({"num_vars": 4, "clauses": clauses}, "m4")

    # Random small instances.
    rng = random.Random(12345)
    for i in range(4000):
        check(random_instance(rng), f"random-{i}")

    # Random instances with several clauses (target vars kept <= 10).
    for i in range(1000):
        m = rng.randint(3, 5)
        n = rng.randint(0, 10 - m)
        pool = all_clauses(m)
        clauses = [list(rng.choice(pool)) for _ in range(n)]
        check({"num_vars": m, "clauses": clauses}, f"stress-{i}")

    # Duplicate clauses explicitly.
    for i in range(300):
        m = rng.randint(3, 5)
        pool = all_clauses(m)
        base = rng.choice(pool)
        clauses = [list(base) for _ in range(rng.randint(1, 3))]
        check({"num_vars": m, "clauses": clauses}, f"dup-{i}")

    # Unsatisfiable sources: all 8 clauses over 3 vars, plus duplicates.
    check({"num_vars": 3, "clauses": [list(c) for c in all_clauses(3)]}, "unsat-all")
    check({"num_vars": 3, "clauses": [list(c) for c in all_clauses(3)] * 2}, "unsat-dup")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for label, src, msg in failures[:10]:
        print("FAIL", label, src, msg)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
