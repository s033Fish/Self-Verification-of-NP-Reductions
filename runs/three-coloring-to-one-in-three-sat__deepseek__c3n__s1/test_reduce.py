"""Tests for the 3-Coloring -> 1-in-3-SAT reduction.

Contains independent exact solvers for both problems (written from the
problem definitions) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers
# ----------------------------------------------------------------------

def solve_three_coloring(instance) -> bool:
    """Try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat_naive(instance) -> bool:
    """Try all 2^m assignments (only for tiny m)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all((bits[a - 1] + bits[b - 1] + bits[c - 1]) == 1
               for a, b, c in clauses):
            return True
    return False


def solve_one_in_three_sat(instance) -> bool:
    """Exact backtracking solver for positive 1-in-3-SAT.

    Assigns variables one at a time, propagating forced values:
      * a clause with >= 2 true variables is violated;
      * a clause with exactly 1 true variable forces its other two false;
      * a clause with 0 true and 1 unassigned forces that variable true;
      * a clause with 0 true and 0 unassigned is violated.
    Each branch works on its own copy of the assignment so that forced values
    are correctly undone on backtracking.
    """
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def propagate(assign):
        """Return the propagated assignment, or None on contradiction."""
        assign = list(assign)
        changed = True
        while changed:
            changed = False
            for a, b, c in clauses:
                vals = (assign[a], assign[b], assign[c])
                t = sum(1 for v in vals if v is True)
                if t > 1:
                    return None
                if t == 1:
                    for x, v in zip((a, b, c), vals):
                        if v is None:
                            assign[x] = False
                            changed = True
                else:  # t == 0
                    unassigned = [x for x, v in zip((a, b, c), vals)
                                  if v is None]
                    if len(unassigned) == 0:
                        return None
                    if len(unassigned) == 1:
                        assign[unassigned[0]] = True
                        changed = True
        return assign

    def rec(assign):
        assign = propagate(assign)
        if assign is None:
            return False
        var = None
        for v in range(1, m + 1):
            if assign[v] is None:
                var = v
                break
        if var is None:
            return True
        for val in (True, False):
            branch = list(assign)
            branch[var] = val
            if rec(branch):
                return True
        return False

    return rec([None] * (m + 1))


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance, naive=False):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(instance)
        reduced = reduce(instance)
        OneInThreeSat.validate(reduced)
        expected = solve_three_coloring(instance)
        got = solve_one_in_three_sat(reduced)
        assert got == expected, (
            f"MISMATCH on {instance}: expected {expected}, got {got}, "
            f"reduced={reduced}"
        )
        if naive:
            naive_got = solve_one_in_three_sat_naive(reduced)
            assert naive_got == expected, (
                f"NAIVE MISMATCH on {instance}: expected {expected}, "
                f"got {naive_got}"
            )
        tests_passed += 1

    # Exhaustive: every graph on 0..5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, naive=(n <= 3))

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        check(random_graph(n, p, rng))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})       # K3: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # C4: yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                             [1, 2], [1, 3], [2, 3]]})        # K4: no
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4],
                             [1, 2], [1, 3], [1, 4],
                             [2, 3], [2, 4], [3, 4]]})        # K5: no
    check({"n": 6, "edges": [[i, j] for i in range(6)
                             for j in range(i + 1, 6)]})      # K6: no
    check({"n": 8, "edges": [[i, (i + 1) % 8] for i in range(8)]})  # C8: yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
