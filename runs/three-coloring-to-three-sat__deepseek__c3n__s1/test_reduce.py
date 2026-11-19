"""Solvers and randomized/exhaustive tests for the 3-Coloring -> 3-SAT reduction.

The 3-colouring solver is a direct brute force over 3^n colourings.
The 3-SAT solver is a complete DPLL search (unit propagation + branching);
a plain 2^m enumeration is impossible on the reduced formulas because the
padding introduces O(n + |E|) helper variables.  The DPLL solver is itself
cross-checked against a naive 2^m enumeration on small random formulas.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written directly from the problem definitions.
# ----------------------------------------------------------------------


def solve_three_coloring(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_three_sat_bruteforce(instance: dict) -> bool:
    """Naive 2^m enumeration; only for tiny instances (used to check DPLL)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Complete DPLL solver with unit propagation."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        while True:
            unit = None
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        if assignment[var] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            assignment[abs(unit)] = unit > 0

        # Simplify clauses under current assignment.
        remaining = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if assignment[var] == (lit > 0):
                        satisfied = True
                        break
                else:
                    new_clause.append(lit)
            if not satisfied:
                remaining.append(tuple(new_clause))
        if not remaining:
            return True

        # Branch on the variable of the first literal.
        lit = remaining[0][0]
        var = abs(lit)
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(remaining, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng: random.Random, n: int, p: float) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def random_3sat(rng: random.Random, m: int, k: int) -> dict:
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeColoring.validate(instance)
        out = reduce(instance)
        problems.ThreeSat.validate(out)
        expected = solve_three_coloring(instance)
        got = solve_three_sat(out)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, out, expected, got))

    # First validate the DPLL solver against naive enumeration on small 3-SAT.
    rng0 = random.Random(999)
    for m in range(0, 9):
        for _ in range(30):
            f = random_3sat(rng0, m, rng0.randint(0, 12)) if m >= 3 else {"num_vars": m, "clauses": []}
            problems.ThreeSat.validate(f)
            a = solve_three_sat_bruteforce(f)
            b = solve_three_sat(f)
            tests_run += 1
            if a == b:
                tests_passed += 1
            else:
                failures.append(("dpll-check", f, None, a, b))

    # Exhaustive over all graphs with n = 0..4 (n=4 has 64 graphs, K4 is no).
    for n in range(5):
        for graph in all_graphs(n):
            check(graph, f"exhaustive n={n}")

    # Random graphs of larger sizes.
    rng = random.Random(12345)
    for n in range(5, 11):
        for _ in range(30):
            check(random_graph(rng, n, rng.choice([0.1, 0.3, 0.5, 0.8])), f"random n={n}")

    # Specific edge cases from the docstrings.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3 yes")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4 no")
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5 yes")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for label, inst, out, expected, got in failures[:5]:
            print("FAIL", label, inst, "expected", expected, "got", got)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
