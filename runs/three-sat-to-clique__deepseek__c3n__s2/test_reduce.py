"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import Clique, ThreeSat
from reduce import reduce
from solvers import solve_clique, solve_three_sat

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_clique(reduced)
    assert got == expected, (
        f"MISMATCH source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    tests_passed += 1


def all_clauses(m: int):
    """All valid 3-literal clauses over variables 1..m."""
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def main() -> None:
    # --- Explicit edge cases -------------------------------------------------
    check({"num_vars": 0, "clauses": []})          # empty formula, m = 0
    check({"num_vars": 5, "clauses": []})          # empty formula, m > 0
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})  # trivially satisfiable
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    # Unsatisfiable: all 8 clauses over 3 vars.
    check({"num_vars": 3, "clauses": all_clauses(3)})
    # Repeated clause.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3]]})

    # --- Exhaustive small random sampling ------------------------------------
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(3, 6)
        pool = all_clauses(m)
        num_clauses = rng.randint(0, min(8, len(pool)))
        clauses = [list(rng.choice(pool)) for _ in range(num_clauses)]
        # Shuffle literals within clauses and clause order.
        for clause in clauses:
            rng.shuffle(clause)
        rng.shuffle(clauses)
        check({"num_vars": m, "clauses": clauses})

    # --- Structured satisfiable / unsatisfiable instances --------------------
    for m in range(3, 7):
        # Forced assignment: unit-like clauses (v1 v2 v3) etc. make it sat.
        clauses = []
        for v in range(1, m + 1):
            others = [x for x in range(1, m + 1) if x != v][:2]
            clauses.append([v, others[0], others[1]])
        check({"num_vars": m, "clauses": clauses})


    # --- Exhaustive: every formula over variables {1,2,3} --------------------
    pool3 = all_clauses(3)
    for r in range(len(pool3) + 1):
        for subset in itertools.combinations(pool3, r):
            check({"num_vars": 3, "clauses": [list(c) for c in subset]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
