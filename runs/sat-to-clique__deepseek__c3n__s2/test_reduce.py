"""Tests for the SAT -> Clique reduction in reduce.py.

Includes brute-force solvers for both problems (written from the
definitions in problems.py) and compares them on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) has value bits[v-1]
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: dict) -> bool:
    """True iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def check(instance: dict) -> None:
    """Validate, reduce, validate the result, and compare answers."""
    Sat.validate(instance)
    target = reduce(instance)
    Clique.validate(target)
    expected = solve_sat(instance)
    got = solve_clique(target)
    assert got == expected, (
        f"mismatch on {instance!r}: SAT={expected}, Clique={got}, "
        f"reduced={target!r}"
    )


TESTS_RUN = 0
TESTS_PASSED = 0


def run(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    check(instance)
    TESTS_PASSED += 1


# ----------------------------------------------------------------------
# Deterministic edge cases
# ----------------------------------------------------------------------


def test_edge_cases() -> None:
    # no clauses -> satisfiable; k = 0 -> yes
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 3, "clauses": []})
    # empty clause -> unsatisfiable
    run({"num_vars": 0, "clauses": [[]]})
    run({"num_vars": 2, "clauses": [[1], []]})
    # single unit clauses
    run({"num_vars": 1, "clauses": [[1]]})
    run({"num_vars": 1, "clauses": [[-1]]})
    run({"num_vars": 1, "clauses": [[1], [-1]]})
    # tautological clause
    run({"num_vars": 1, "clauses": [[1, -1]]})
    # repeated literals / repeated clauses
    run({"num_vars": 2, "clauses": [[1, 1], [1, 1]]})
    run({"num_vars": 2, "clauses": [[1, 2], [1, 2]]})
    # unused variables
    run({"num_vars": 5, "clauses": [[1], [2]]})
    # a classic unsatisfiable 2-CNF
    run({"num_vars": 2, "clauses": [[1, 2], [1, -2], [-1, 2], [-1, -2]]})


# ----------------------------------------------------------------------
# Exhaustive small instances
# ----------------------------------------------------------------------


def all_clauses(num_vars: int, max_len: int) -> list[list[int]]:
    lits = [v for v in range(1, num_vars + 1)] + [-v for v in range(1, num_vars + 1)]
    result: list[list[int]] = [[]]
    for length in range(1, max_len + 1):
        result.extend([list(c) for c in itertools.combinations(lits, length)])
    return result


def test_exhaustive() -> None:
    # every formula over up to 2 variables with up to 2 clauses of length <= 2
    pool = all_clauses(2, 2)
    for c1 in pool:
        for c2 in pool:
            run({"num_vars": 2, "clauses": [c1, c2]})
    # single clauses over 3 variables, length <= 3
    for c in all_clauses(3, 3):
        run({"num_vars": 3, "clauses": [c]})


# ----------------------------------------------------------------------
# Random small instances
# ----------------------------------------------------------------------


def random_instance(rng: random.Random) -> dict:
    num_vars = rng.randint(0, 4)
    num_clauses = rng.randint(0, 5)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if num_vars == 0:
                break
            v = rng.randint(1, num_vars)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def test_random() -> None:
    rng = random.Random(12345)
    for _ in range(3000):
        run(random_instance(rng))


def main() -> None:
    test_edge_cases()
    test_exhaustive()
    test_random()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED

    import json

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": True,
                "tests_run": TESTS_RUN,
                "tests_passed": TESTS_PASSED,
            },
            fh,
        )


if __name__ == "__main__":
    main()
