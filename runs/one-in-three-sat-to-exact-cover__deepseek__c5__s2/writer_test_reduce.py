"""Brute-force solvers and randomized tests for the 1-in-3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------- brute-force solvers -----------------------------

def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one variable true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for (a, b, c) in clauses:
            s = bits[a - 1] + bits[b - 1] + bits[c - 1]
            if s != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """True iff some pairwise-disjoint chosen sets cover the whole universe."""
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    full = (1 << u) - 1
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    # Backtracking over set indices; prune with memo on covered mask.
    seen = set()

    def rec(covered: int) -> bool:
        if covered == full:
            return True
        if covered in seen:
            return False
        seen.add(covered)
        for mask in masks:
            if mask and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ----------------------------- test helpers -----------------------------

def random_source_instance(rng: random.Random):
    m = rng.randint(0, 6)
    if m == 0:
        n_clauses = 0
    else:
        n_clauses = rng.randint(0, 7)
    clauses = []
    for _ in range(n_clauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append(vs)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        OneInThreeSat.validate(instance)
        expected = solve_one_in_three_sat(instance)
        target = reduce(instance)
        ExactCover.validate(target)
        got = solve_exact_cover(target)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, target, got))

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "no clauses m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "dup clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "triple dup")
    # (x1,x2,x3) and (x1,x2,x4): x1 true, others false works.
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}, "shared var")
    # Unsatisfiable: x1 must be the one true in both, forcing x2=x3=x4 false,
    # but clause 2 needs one of x2,x3,x4 true.
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]}, "unsat 4")
    # Variables that never appear.
    check({"num_vars": 10, "clauses": [[1, 2, 3]]}, "unused vars")

    # Randomized tests.
    for i in range(4000):
        inst = random_source_instance(rng)
        check(inst, f"random {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for label, inst, exp, tgt, got in failures[:5]:
        print("FAIL", label, inst, "expected", exp, "got", got)
    assert not failures, "some tests failed"


if __name__ == "__main__":
    main()
