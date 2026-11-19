"""Tests for reduce.py: brute-force solvers plus exhaustive small checks."""

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance):
    """Backtracking 3-SAT solver with unit propagation (exact)."""
    clauses = [list(c) for c in instance["clauses"]]

    def rec(clauses):
        while True:
            unit = None
            for c in clauses:
                if not c:
                    return False
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            lit = unit
            clauses = [[x for x in c if x != -lit] for c in clauses if lit not in c]
        if not clauses:
            return True
        lit = clauses[0][0]
        if rec([[x for x in c if x != -lit] for c in clauses if lit not in c]):
            return True
        return rec([[x for x in c if x != lit] for c in clauses if -lit not in c])

    return rec(clauses)


# ----------------------------------------------------------------------
# Helpers.

def all_graphs(n):
    """All simple undirected graphs on n vertices (as edge lists)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    problems.ThreeColoring.validate(instance)
    out = reduce(instance)
    problems.ThreeSat.validate(out)
    expected = solve_three_coloring(instance)
    got = solve_three_sat(out)
    assert got == expected, (instance, out, expected, got)
    TESTS_PASSED += 1


def main():
    # Exhaustive over all graphs with up to 6 vertices.
    for n in range(0, 7):
        for g in all_graphs(n):
            check(g)

    # Random graphs up to 9 vertices.
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        check({"n": n, "edges": edges})

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})          # triangle: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]})  # K4: no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # C4: yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5: yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [0, 2], [1, 3], [2, 4], [3, 0], [4, 1]]})  # K5: no
    # Empty-edge graphs of many sizes.
    for n in range(0, 11):
        check({"n": n, "edges": []})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
