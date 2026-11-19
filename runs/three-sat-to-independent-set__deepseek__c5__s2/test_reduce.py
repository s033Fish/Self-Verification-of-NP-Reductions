"""Independent tests for reduce.py: 3-SAT -> Independent Set.

Brute-force solvers are written directly from the problem definitions in
problems.py.  We compare solver answers on many small source instances with
solver answers on their reductions.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) has value bits[v-1]
        if all(
            any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(v not in adj[u] for u, v in itertools.combinations(combo, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Test helpers
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    # Source instance must be valid.
    problems.ThreeSat.validate(instance)
    expected = solve_three_sat(instance)
    reduced = reduce(instance)
    # Reduction must produce a valid target instance.
    problems.IndependentSet.validate(reduced)
    got = solve_independent_set(reduced)
    if got != expected:
        raise AssertionError(
            f"MISMATCH source={instance!r} expected={expected} "
            f"reduced={reduced!r} got={got}"
        )
    TESTS_PASSED += 1


def random_3sat(num_vars: int, num_clauses: int, rng: random.Random) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_edge_cases() -> None:
    # No clauses, any m including 0 -> yes.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []})

    # Single clause, satisfiable.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 5, "clauses": [[1, -2, 3]]})

    # Unsatisfiable: all 8 clauses over 3 vars.
    all_clauses = [
        [a, b, c]
        for a in (1, -1)
        for b in (2, -2)
        for c in (3, -3)
    ]
    check({"num_vars": 3, "clauses": all_clauses})

    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, 3]]})

    # Variables not all appearing.
    check({"num_vars": 4, "clauses": [[1, 2, 3]]})
    check({"num_vars": 6, "clauses": [[4, 5, 6]]})

    # Unsatisfiable 2-clause-ish example.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                      [1, 2, -3], [-1, -2, 3],
                                      [1, -2, 3], [-1, 2, -3],
                                      [1, -2, -3], [-1, 2, 3]]})


def test_exhaustive_small() -> None:
    # Exhaustively test all formulas with up to 2 clauses over 3 variables
    # (literal choices 6 per clause, order-insensitive but that's fine).
    literals = [1, -1, 2, -2, 3, -3]
    clause_options = []
    for combo in itertools.combinations(literals, 3):
        # keep only clauses on 3 distinct variables
        if len({abs(x) for x in combo}) == 3:
            clause_options.append(list(combo))
    for c1 in clause_options:
        check({"num_vars": 3, "clauses": [c1]})
        for c2 in clause_options:
            check({"num_vars": 3, "clauses": [c1, c2]})


def test_random() -> None:
    rng = random.Random(12345)
    for _ in range(1500):
        num_vars = rng.randint(0, 6)
        max_clauses = 0 if num_vars < 3 else 6
        num_clauses = rng.randint(0, max_clauses)
        if num_vars < 3 and num_clauses > 0:
            num_clauses = 0
        check(random_3sat(num_vars, num_clauses, rng))


def test_reduction_shape() -> None:
    # Structural sanity: n == 3 * #clauses, k == #clauses.
    global TESTS_RUN, TESTS_PASSED
    rng = random.Random(999)
    for _ in range(200):
        inst = random_3sat(rng.randint(3, 6), rng.randint(0, 5), rng)
        TESTS_RUN += 1
        red = reduce(inst)
        assert red["n"] == 3 * len(inst["clauses"]), red
        assert red["k"] == len(inst["clauses"]), red
        assert len(red["edges"]) == len(set(map(frozenset, red["edges"]))), red
        problems.IndependentSet.validate(red)
        TESTS_PASSED += 1


def main() -> None:
    test_edge_cases()
    test_exhaustive_small()
    test_random()
    test_reduction_shape()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
