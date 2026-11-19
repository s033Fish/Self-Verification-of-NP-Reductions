"""Tests comparing brute-force answers on 3-SAT instances and their reductions."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce
from solvers import solve_three_sat, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance: dict, label: str = "") -> None:
    global tests_run, tests_passed
    tests_run += 1
    problems.ThreeSat.validate(instance)
    target = reduce(instance)
    problems.VertexCover.validate(target)
    expected = solve_three_sat(instance)
    got = solve_vertex_cover(target)
    assert expected == got, (
        f"MISMATCH {label}: source={instance} expected={expected} "
        f"target={target} got={got}"
    )
    tests_passed += 1


def all_clauses(num_vars: int):
    """All valid clauses: 3 literals, 3 distinct variables, no v and -v."""
    clauses = []
    for vars_ in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def main() -> None:
    rng = random.Random(12345)

    # Edge case: no clauses, various m (including m = 0).
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # Exhaustive: all formulas over m=3 variables with up to 2 clauses.
    pool3 = all_clauses(3)
    for r in range(0, 3):
        for combo in itertools.combinations(pool3, r):
            check({"num_vars": 3, "clauses": list(combo)}, f"exh3 r={r}")

    # All single clauses for m=4.
    pool4 = all_clauses(4)
    for clause in pool4:
        check({"num_vars": 4, "clauses": [clause]}, "single4")

    # Random instances for m = 3..5, with duplicates allowed.
    for _ in range(300):
        m = rng.randint(3, 5)
        pool = all_clauses(m)
        r = rng.randint(0, 6)
        clauses = [rng.choice(pool) for _ in range(r)]
        check({"num_vars": m, "clauses": clauses}, f"rand m={m}")

    # Structured satisfiable / unsatisfiable cases.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                      [1, -2, 3], [-1, 2, -3],
                                      [1, 2, -3], [-1, -2, 3],
                                      [1, -2, -3], [-1, 2, 3]]}, "all8")
    check({"num_vars": 3, "clauses": [[1, 2, 3]] * 5}, "dups")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4],
                                      [1, 3, 4], [2, 3, 4]]}, "struct")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
