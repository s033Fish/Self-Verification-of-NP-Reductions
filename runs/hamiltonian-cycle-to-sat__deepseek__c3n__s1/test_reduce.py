"""Tests comparing brute-force answers for Hamiltonian Cycle and SAT.

The SAT solver is a small DPLL implementation (with unit propagation) so
that the reduced formulas (which have n^2 variables) can be decided.
"""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def hamiltonian_brute(instance):
    """Exhaustive search over cyclic orderings starting at vertex 0."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if (a, b) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def _clause_state(clause, assignment):
    """Return (satisfied, unassigned_literals)."""
    unassigned = []
    for lit in clause:
        var = abs(lit)
        val = assignment.get(var)
        if val is None:
            unassigned.append(lit)
        elif (lit > 0) == val:
            return True, []
    return False, unassigned


def sat_solve(instance):
    """DPLL satisfiability check."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]
    return _dpll(clauses, {})


def _dpll(clauses, assignment):
    assignment = dict(assignment)
    while True:
        unit = None
        all_satisfied = True
        for clause in clauses:
            satisfied, unassigned = _clause_state(clause, assignment)
            if satisfied:
                continue
            all_satisfied = False
            if not unassigned:
                return False  # conflict
            if len(unassigned) == 1:
                unit = unassigned[0]
                break
        if all_satisfied:
            return True
        if unit is None:
            break
        var = abs(unit)
        assignment[var] = unit > 0

    # Choose an unassigned variable that appears in some unsatisfied clause.
    chosen = None
    for clause in clauses:
        satisfied, unassigned = _clause_state(clause, assignment)
        if satisfied:
            continue
        for lit in unassigned:
            if abs(lit) not in assignment:
                chosen = abs(lit)
                break
        if chosen is not None:
            break
    if chosen is None:
        return True

    for value in (True, False):
        branch = dict(assignment)
        branch[chosen] = value
        if _dpll(clauses, branch):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators


def all_graphs(n):
    """All simple undirected graphs on n vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = hamiltonian_brute(instance)
        got = sat_solve(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, got))

    # Edge cases n = 0, 1, 2.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 2, "edges": []}, "n=2 no edge")
    check({"n": 2, "edges": [[0, 1]]}, "n=2 one edge")

    # All graphs on 3 and 4 vertices.
    for n in (3, 4):
        for g in all_graphs(n):
            check(g, f"all n={n}")

    # All graphs on 5 vertices (2^10 = 1024).
    for g in all_graphs(5):
        check(g, "all n=5")

    # Random graphs on 6..8 vertices.
    rng = random.Random(12345)
    for n in (6, 7, 8):
        for _ in range(60):
            p = rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng), f"random n={n}")

    # A few structured cases: complete graphs and cycles.
    for n in (3, 4, 5, 6, 7):
        complete = {
            "n": n,
            "edges": [[u, v] for u in range(n) for v in range(u + 1, n)],
        }
        check(complete, f"complete n={n}")
        cycle = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        check(cycle, f"cycle n={n}")
        path = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        check(path, f"path n={n}")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for label, instance, expected, got in failures[:10]:
        print("FAIL", label, instance, "expected", expected, "got", got)
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")
