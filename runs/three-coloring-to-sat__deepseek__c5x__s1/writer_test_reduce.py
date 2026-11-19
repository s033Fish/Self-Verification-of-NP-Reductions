"""Tests for the 3-Coloring -> SAT reduction.

Includes independent brute-force solvers for both problems (written from the
definitions in problems.py) and compares answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of the reduction)

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable. Exhaustive over 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff the CNF is satisfiable. DPLL with unit propagation."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        new_clauses = []
        for clause in clauses:
            remaining = []
            satisfied = False
            for lit in clause:
                v = abs(lit)
                if v in assignment:
                    if assignment[v] == (lit > 0):
                        satisfied = True
                        break
                else:
                    remaining.append(lit)
            if satisfied:
                continue
            if not remaining:
                return False  # empty clause -> conflict
            new_clauses.append(remaining)

        if not new_clauses:
            return True

        # unit propagation
        for clause in new_clauses:
            if len(clause) == 1:
                lit = clause[0]
                v = abs(lit)
                val = lit > 0
                if v in assignment and assignment[v] != val:
                    return False
                assignment = dict(assignment)
                assignment[v] = val
                return dpll(new_clauses, assignment)

        # choose a variable from the shortest clause
        shortest = min(new_clauses, key=len)
        v = abs(shortest[0])
        for val in (True, False):
            assignment = dict(assignment)
            assignment[v] = val
            if dpll(new_clauses, assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = solve_three_coloring(instance)
        got = solve_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, reduced, got))

    # Exhaustive over all graphs with n = 0..4
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, f"all_graphs n={n}")

    # Random graphs n = 5..8
    rng = random.Random(12345)
    for n in range(5, 9):
        for _ in range(300):
            p = rng.choice([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
            check(random_graph(n, p, rng), f"random n={n}")

    # Explicit edge cases from the docstrings
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 2, "edges": [[0, 1]]}, "n=2 edge")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]}, "C4")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5")

    # Sanity check the SAT solver itself on hand-made formulas
    sat_cases = [
        ({"num_vars": 0, "clauses": []}, True),
        ({"num_vars": 1, "clauses": [[]]}, False),
        ({"num_vars": 1, "clauses": [[1]]}, True),
        ({"num_vars": 1, "clauses": [[1], [-1]]}, False),
        ({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]}, True),
        ({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]}, False),
        ({"num_vars": 3, "clauses": [[1, 1, 2], [-1], [-2]]}, False),
    ]
    for inst, expected in sat_cases:
        tests_run += 1
        Sat.validate(inst)
        got = solve_sat(inst)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(("sat_sanity", inst, expected, None, got))

    # Sanity check the 3-coloring solver itself
    tc_cases = [
        ({"n": 0, "edges": []}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, True),
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, False),
    ]
    for inst, expected in tc_cases:
        tests_run += 1
        ThreeColoring.validate(inst)
        got = solve_three_coloring(inst)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(("tc_sanity", inst, expected, None, got))

    for label, instance, expected, reduced, got in failures[:5]:
        print("FAIL", label, "expected", expected, "got", got)
        print("  source:", instance)
        if reduced is not None:
            print("  reduced:", reduced)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
