"""Tests for reduce.py: compare brute-force solvers on many small instances."""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_clique(instance: dict) -> bool:
    """Yes iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Backtracking search over assignments; yes iff some assignment works."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Empty clause => immediately unsatisfiable.
    for clause in clauses:
        if not clause:
            return False

    def rec(var: int, assignment: dict) -> bool:
        if var > m:
            return True
        for value in (False, True):
            assignment[var] = value
            # Check clauses that are already fully assigned and false.
            ok = True
            for clause in clauses:
                unassigned = False
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned = True
                if not satisfied and not unassigned:
                    ok = False
                    break
            if ok and rec(var + 1, assignment):
                return True
        del assignment[var]
        return False

    return rec(1, {})


# ----------------------------------------------------------------------
# Test harness.

TESTS_RUN = 0
TESTS_PASSED = 0


def check(source_instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1

    Clique.validate(source_instance)
    target = reduce(source_instance)
    Sat.validate(target)

    expected = solve_clique(source_instance)
    got = solve_sat(target)

    assert got == expected, (
        f"MISMATCH for {source_instance}: clique={expected}, sat={got}, "
        f"reduction={target}"
    )
    TESTS_PASSED += 1


def main() -> None:
    rng = random.Random(12345)

    # --- Exhaustive: all graphs on n = 0..3, all k in a wide range ----
    for n in range(0, 4):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(p) for idx, p in enumerate(all_pairs) if mask >> idx & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # --- Random graphs, n = 4..6 -------------------------------------
    for _ in range(300):
        n = rng.randint(4, 6)
        all_pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in all_pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # --- Specific edge cases -----------------------------------------
    check({"n": 0, "edges": [], "k": 0})       # k<=0 yes
    check({"n": 0, "edges": [], "k": 1})       # k>n no
    check({"n": 5, "edges": [], "k": 1})       # k=1 yes
    check({"n": 5, "edges": [], "k": 2})       # no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 4})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3})  # path, no triangle
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})  # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})  # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4})  # no
    check({"n": 6, "edges": [], "k": 0})       # k<=0 yes
    check({"n": 6, "edges": [], "k": 7})       # k>n no

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
