"""Independent checks of reduce.py: brute-force solvers + tests.

We implement brute-force solvers for both SOURCE (positive 1-in-3-SAT) and
TARGET (Exact Cover) straight from the definitions in problems.py, then
compare answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import OneInThreeSat, ExactCover, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the documented definitions)

def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one var true in every clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[i] is value of variable i+1
        ok = True
        for (a, b, c) in clauses:
            cnt = int(bits[a - 1]) + int(bits[b - 1]) + int(bits[c - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """True iff some subcollection of sets is disjoint with union = universe."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    n = len(sets)
    for mask in range(1 << n):
        covered = 0
        good = True
        for i in range(n):
            if mask & (1 << i):
                s = 0
                for e in sets[i]:
                    s |= 1 << e
                if covered & s:  # overlap -> not disjoint
                    good = False
                    break
                covered |= s
        if good and covered == full:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance: dict, label: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    src_ans = solve_one_in_three_sat(instance)
    red = reduce(instance)
    # reduced instance must be a valid TARGET instance
    try:
        ExactCover.validate(red)
    except InvalidInstance as exc:
        failures.append(f"{label}: reduce produced invalid target instance: {exc}")
        return
    tgt_ans = solve_exact_cover(red)
    if src_ans == tgt_ans:
        tests_passed += 1
    else:
        failures.append(
            f"{label}: source={src_ans} target={tgt_ans} instance={instance} reduced={red}"
        )


def all_clause_subsets(m: int):
    triples = list(itertools.combinations(range(1, m + 1), 3))
    for r in range(len(triples) + 1):
        for combo in itertools.combinations(triples, r):
            yield [list(t) for t in combo]


def main() -> None:
    rng = random.Random(12345)

    # Exhaustive over all sets of distinct clauses for m = 0..5.
    for m in range(0, 6):
        for clauses in all_clause_subsets(m):
            check({"num_vars": m, "clauses": clauses}, f"exhaustive m={m}")

    # Exhaustive with duplicate clauses (multiplicity 0..2) for m = 4.
    m = 4
    triples = [list(t) for t in itertools.combinations(range(1, m + 1), 3)]
    for counts in itertools.product(range(3), repeat=len(triples)):
        clauses = []
        for t, c in zip(triples, counts):
            clauses.extend([t] * c)
        check({"num_vars": m, "clauses": clauses}, "duplicates m=4")

    # Random instances with larger m, duplicates and unused variables.
    for _ in range(3000):
        m = rng.randint(0, 8)
        nclauses = rng.randint(0, 12)
        clauses = []
        for _ in range(nclauses):
            if m < 3:
                break
            clauses.append(rng.sample(range(1, m + 1), 3))
        check({"num_vars": m, "clauses": clauses}, "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(" ", f)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
