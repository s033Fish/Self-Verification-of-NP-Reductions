"""Tests for the 3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import random
from itertools import combinations

from problems import ThreeSat, ExactCover
from reduce import reduce
from solvers import solve_three_sat, solve_exact_cover

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    ExactCover.validate(out)
    a = solve_three_sat(instance)
    b = solve_exact_cover(out)
    assert a == b, (instance, out, a, b)
    tests_passed += 1


def random_instance(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        # clauses need m >= 3; only allow the empty-clause case
        return {"num_vars": m, "clauses": []}
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 7, "clauses": []})
    # Unsatisfiable: all 8 clauses over 3 vars.
    all_clauses = []
    for signs in [(a, b, c) for a in (1, -1) for b in (1, -1) for c in (1, -1)]:
        all_clauses.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    check({"num_vars": 3, "clauses": all_clauses})
    # Satisfiable simple.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # Variables not appearing.
    check({"num_vars": 10, "clauses": [[1, 2, 3]]})
    # Mixed signs.
    check({"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]})

    # Random tests.
    for _ in range(4000):
        check(random_instance(rng))

    # Exhaustive small: all formulas with m=3 over a subset of clauses.
    m = 3
    all_possible = []
    for vs in combinations(range(1, m + 1), 3):
        for signs in [(a, b, c) for a in (1, -1) for b in (1, -1) for c in (1, -1)]:
            all_possible.append([signs[0] * vs[0], signs[1] * vs[1], signs[2] * vs[2]])
    for _ in range(3000):
        k = rng.randint(0, 4)
        clauses = [rng.choice(all_possible) for _ in range(k)]
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
