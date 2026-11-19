"""Brute-force solvers and randomized tests for the 1-in-3-SAT -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_one_in_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for var in clause if bits[var - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    reachable = {0}
    for number in instance["numbers"]:
        new = set()
        for value in reachable:
            new.add(value + number)
        reachable |= new
        if target in reachable:
            return True
    return target in reachable


# ----------------------------------------------------------------------
# Tests.

def check(instance: dict) -> bool:
    OneInThreeSat.validate(instance)
    expected = solve_one_in_three_sat(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    got = solve_subset_sum(reduced)
    assert expected == got, (
        f"MISMATCH: instance={instance} expected={expected} got={got} "
        f"reduced={reduced}"
    )
    return expected


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # --- deterministic edge cases ---
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 1, "clauses": []})
    run({"num_vars": 5, "clauses": []})
    run({"num_vars": 3, "clauses": [[1, 2, 3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 1]]})
    # unsatisfiable: every pair must have exactly one true but 3 clauses force
    # contradictions
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    run({"num_vars": 6, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})

    # --- randomized tests ---
    rng = random.Random(12345)
    for _ in range(2000):
        m = rng.randint(0, 7)
        if m == 0:
            clauses = []
        else:
            n = rng.randint(0, 6)
            clauses = []
            for _ in range(n):
                if m < 3:
                    break
                clause = rng.sample(range(1, m + 1), 3)
                clauses.append(clause)
        instance = {"num_vars": m, "clauses": clauses}
        run(instance)

    # exhaustive over all formulas with m=3, up to 3 clauses (clauses from all
    # 3-subsets of {1,2,3}, i.e. only one possible clause, repeated)
    for n in range(0, 4):
        run({"num_vars": 3, "clauses": [[1, 2, 3]] * n})

    # exhaustive over all formulas with m=4 and up to 2 clauses
    triples = list(itertools.combinations(range(1, 5), 3))
    for n in range(0, 3):
        for combo in itertools.combinations_with_replacement(triples, n):
            run({"num_vars": 4, "clauses": [list(c) for c in combo]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
