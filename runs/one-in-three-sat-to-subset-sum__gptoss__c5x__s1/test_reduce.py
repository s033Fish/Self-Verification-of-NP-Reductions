"""Independent verification of reduce.py for OneInThreeSat -> SubsetSum.

We implement our own brute-force solvers from the problem definitions and
compare their answers against the answers of the reduced instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one variable true per clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True  # empty formula is satisfiable for any m, including 0
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """True iff some sub-list (each position at most once) sums to target."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(source_instance: dict, label: str = "") -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    try:
        expected = solve_one_in_three_sat(source_instance)
        reduced = reduce(source_instance)
        # The reduction must produce a valid target instance.
        SubsetSum.validate(reduced)
        got = solve_subset_sum(reduced)
    except Exception as exc:  # noqa: BLE001
        FAILURES.append((label, source_instance, f"exception: {exc!r}"))
        return
    if expected == got:
        TESTS_PASSED += 1
    else:
        FAILURES.append((label, source_instance, f"expected {expected}, got {got}, reduced={reduced}"))


def random_instance(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    n_clauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(n_clauses):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


def main() -> int:
    # --- Deterministic edge cases -------------------------------------
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 1, "clauses": []}, "no clauses m=1")
    check({"num_vars": 5, "clauses": []}, "no clauses m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "triple clause")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}, "shared vars")
    check({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]}, "disjoint clauses")
    check({"num_vars": 6, "clauses": [[1, 2, 3], [1, 4, 5], [2, 4, 6], [3, 5, 6]]}, "unsat-ish")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]}, "4 vars all triples")
    # unused variable mixed with used ones
    check({"num_vars": 7, "clauses": [[1, 2, 3], [1, 2, 4]]}, "unused vars")
    # all clauses identical over many variables
    check({"num_vars": 3, "clauses": [[1, 2, 3]] * 5}, "many duplicate clauses")

    # --- Exhaustive small instances -----------------------------------
    # all clauses over variables 1..m for m = 3,4,5, up to a few clauses
    for m in (3, 4, 5):
        all_clauses = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        for r in range(0, 4):
            for combo in itertools.combinations(all_clauses, r):
                check({"num_vars": m, "clauses": [list(c) for c in combo]}, f"exhaustive m={m} r={r}")

    # --- Randomized tests ---------------------------------------------
    rng = random.Random(12345)
    for _ in range(4000):
        inst = random_instance(rng, max_vars=6, max_clauses=6)
        check(inst, "random small")

    for _ in range(1500):
        inst = random_instance(rng, max_vars=9, max_clauses=10)
        check(inst, "random medium")

    # --- Report --------------------------------------------------------
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED} failures={len(FAILURES)}")
    for label, inst, msg in FAILURES[:20]:
        print(f"FAIL [{label}] {inst}: {msg}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
