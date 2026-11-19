"""Tests for reduce.py: compare brute-force answers on source and reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce
from solvers import solve_one_in_three, solve_subset_sum

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    OneInThreeSat.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = solve_one_in_three(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (
        f"MISMATCH on {instance}: source={expected}, reduced={got}, "
        f"reduction={reduced}"
    )
    TESTS_PASSED += 1


def all_clauses(m: int) -> list[list[int]]:
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


def main() -> None:
    # ---- Edge cases -------------------------------------------------
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})
    # Variables that never appear.
    check({"num_vars": 10, "clauses": [[1, 2, 3]]})

    # ---- Exhaustive over all subsets of clauses for m = 3, 4 --------
    for m in (3, 4):
        universe = all_clauses(m)
        for r in range(0, len(universe) + 1):
            for combo in itertools.combinations(universe, r):
                check({"num_vars": m, "clauses": [list(c) for c in combo]})

    # ---- Random tests -------------------------------------------------
    rng = random.Random(12345)
    for _ in range(4000):
        m = rng.randint(3, 8)
        n = rng.randint(0, 7)
        clauses = []
        for _ in range(n):
            clause = rng.sample(range(1, m + 1), 3)
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses})

    # ---- Random tests with unused variables ---------------------------
    for _ in range(1500):
        m = rng.randint(3, 9)
        used = rng.sample(range(1, m + 1), 3)
        n = rng.randint(1, 6)
        clauses = []
        for _ in range(n):
            clause = rng.sample(used, 3) if len(used) >= 3 else used
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses})

    # ---- Random tests with duplicate clauses --------------------------
    for _ in range(1500):
        m = rng.randint(3, 7)
        base = [rng.sample(range(1, m + 1), 3) for _ in range(rng.randint(1, 3))]
        clauses = [list(rng.choice(base)) for _ in range(rng.randint(0, 8))]
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
