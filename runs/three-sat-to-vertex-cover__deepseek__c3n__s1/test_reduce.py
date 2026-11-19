"""Tests for reduce.py: compare brute-force answers on small 3-SAT instances."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce
from solvers import solve_three_sat, solve_vertex_cover

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_vertex_cover(reduced)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    TESTS_PASSED += 1


def all_clauses(num_vars: int) -> list[list[int]]:
    """All valid 3-literal clauses (3 distinct variables) over 1..num_vars."""
    clauses = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    return clauses


def main() -> None:
    # Edge cases: empty formula.
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []})

    # Every single clause and every pair of clauses for m = 3, 4.
    for m in (3, 4):
        clauses = all_clauses(m)
        for c in clauses:
            check({"num_vars": m, "clauses": [c]})
        for c1, c2 in itertools.combinations(clauses, 2):
            check({"num_vars": m, "clauses": [c1, c2]})
        rng = random.Random(1234 + m)
        for _ in range(200):
            k = rng.randint(0, 4)
            formula = [list(rng.choice(clauses)) for _ in range(k)]
            check({"num_vars": m, "clauses": formula})

    # Duplicate clauses and unused variables.
    check({"num_vars": 5, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, 6]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 4]]})
    # Fully unsatisfiable 3-variable formula (all 8 clauses).
    check({"num_vars": 3, "clauses": all_clauses(3)})

    # Random formulas over varying m.
    rng = random.Random(99)
    for _ in range(1500):
        m = rng.randint(0, 6)
        if m < 3:
            formula = []
        else:
            pool = all_clauses(m)
            k = rng.randint(0, min(6, len(pool)))
            formula = [list(rng.choice(pool)) for _ in range(k)]
        check({"num_vars": m, "clauses": formula})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
