"""Brute-force / DPLL solvers and tests comparing 3-Coloring with its reduction."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_three_coloring(instance) -> bool:
    """Brute force over 3^n colourings (small n)."""
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance) -> bool:
    """Exact DPLL with unit propagation."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        clauses = list(clauses)
        # Unit propagation to fixpoint.
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    v = abs(lit)
                    val = lit > 0
                    if v in assignment:
                        if assignment[v] != val:
                            return False
                    else:
                        assignment[v] = val
                        changed = True
                new_clauses.append(tuple(unassigned))
            clauses = new_clauses
        if not clauses:
            return True
        # Branch on a variable from the first clause.
        v = abs(clauses[0][0])
        for val in (True, False):
            branch = dict(assignment)
            branch[v] = val
            if dpll(clauses, branch):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeColoring.validate(instance)
        target = reduce(instance)
        problems.ThreeSat.validate(target)
        expected = solve_three_coloring(instance)
        got = solve_three_sat(target)
        assert expected == got, (
            f"MISMATCH on {instance}: expected {expected}, got {got}, "
            f"reduced={target}"
        )
        tests_passed += 1

    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs (DPLL handles the larger formulas).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 10)
        p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        check(random_graph(n, p, rng))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})          # triangle: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]})  # K4: no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5: no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})    # C4: yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
