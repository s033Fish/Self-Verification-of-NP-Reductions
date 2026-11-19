"""Independent tests for reduce.py (1-in-3-SAT -> Subset Sum).

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare their answers on many small
source instances against the answers of the reduced target instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_one_in_three_sat(instance) -> bool:
    """Yes iff some assignment makes exactly one var true in every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """Yes iff some sub-list sums to target (each position used once)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


SOLVERS = {
    "OneInThreeSat": solve_one_in_three_sat,
    "SubsetSum": solve_subset_sum,
}


# ----------------------------------------------------------------------
# Instance generators for small source instances.

def random_source_instance(rng):
    m = rng.randint(0, 6)
    n = rng.randint(0, 5)
    clauses = []
    if m >= 3:
        for _ in range(n):
            clause = rng.sample(range(1, m + 1), 3)
            clauses.append(clause)
    # Occasionally duplicate a clause (allowed by the definition).
    if clauses and rng.random() < 0.3:
        clauses.append(list(rng.choice(clauses)))
    return {"num_vars": m, "clauses": clauses}


def explicit_source_instances():
    insts = []
    # No clauses, various m (including m = 0).
    for m in range(0, 6):
        insts.append({"num_vars": m, "clauses": []})
    # Single clause.
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3]]})
    # Two clauses sharing variables.
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    insts.append({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})
    insts.append({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]})
    # Unsatisfiable-ish structures.
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    insts.append({"num_vars": 5, "clauses": [[1, 2, 3], [1, 4, 5], [2, 4, 5]]})
    # Variables that never appear.
    insts.append({"num_vars": 6, "clauses": [[1, 2, 3]]})
    # Clause order / variable order permutations.
    insts.append({"num_vars": 3, "clauses": [[3, 1, 2]]})
    return insts


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            OneInThreeSat.validate(instance)
        except problems.InvalidInstance as exc:
            failures.append(f"{label}: source instance invalid: {exc}")
            return
        reduced = reduce(instance)
        try:
            SubsetSum.validate(reduced)
        except problems.InvalidInstance as exc:
            failures.append(f"{label}: reduced instance invalid: {exc}")
            return
        expected = solve_one_in_three_sat(instance)
        got = solve_subset_sum(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: source={instance} expected {expected}, "
                f"reduced={reduced} got {got}"
            )

    for i, inst in enumerate(explicit_source_instances()):
        check(inst, f"explicit[{i}]")

    rng = random.Random(12345)
    for i in range(3000):
        check(random_source_instance(rng), f"random[{i}]")


    # Exhaustive enumeration of small formulas: all multisets of up to 3
    # clauses, and all subsets of clauses, for m = 3,4,5.
    for m in range(3, 6):
        all_clauses = list(itertools.combinations(range(1, m + 1), 3))
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(all_clauses, r):
                check({"num_vars": m, "clauses": [list(c) for c in combo]},
                      f"exh-multiset-m{m}-r{r}")
        for r in range(0, len(all_clauses) + 1):
            for combo in itertools.combinations(all_clauses, r):
                check({"num_vars": m, "clauses": [list(c) for c in combo]},
                      f"exh-subset-m{m}-r{r}")

    # Larger random instances (m up to 9, n up to 8).
    rng2 = random.Random(999)
    for i in range(2000):
        m = rng2.randint(3, 9)
        n = rng2.randint(0, 8)
        clauses = [list(rng2.sample(range(1, m + 1), 3)) for _ in range(n)]
        check({"num_vars": m, "clauses": clauses}, f"large-random[{i}]")

    # Stress clause digits: one variable in many clauses.
    for i in range(500):
        m = rng2.randint(3, 5)
        n = rng2.randint(1, 12)
        clauses = [list(rng2.sample(range(1, m + 1), 3)) for _ in range(n)]
        check({"num_vars": m, "clauses": clauses}, f"stress[{i}]")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  " + f)
    else:
        print("all tests passed")
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
