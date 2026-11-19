"""Brute-force solvers and randomized/edge-case tests for the Clique->SAT reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written directly from the problem definitions.

def clique_solver(instance: dict) -> bool:
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
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


def sat_solver(instance: dict) -> bool:
    """DPLL with unit propagation (a from-scratch exact SAT solver)."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        while True:
            # simplify
            new_clauses = []
            unit = None
            for clause in clauses:
                sat = False
                unassigned = []
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            sat = True
                            break
                    else:
                        unassigned.append(lit)
                if sat:
                    continue
                if not unassigned:
                    return False  # empty clause -> unsat
                new_clauses.append(unassigned)
                if len(unassigned) == 1:
                    unit = unassigned[0]
            clauses = new_clauses
            if not clauses:
                return True
            if unit is None:
                break
            assignment = dict(assignment)
            assignment[abs(unit)] = unit > 0
        # choose a variable
        lit = clauses[0][0]
        v = abs(lit)
        for val in (True, False):
            a = dict(assignment)
            a[v] = val
            if dpll(clauses, a):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Tests

def check(instance: dict, results: list) -> None:
    Clique.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = clique_solver(instance)
    got = sat_solver(reduced)
    results.append(expected == got)
    assert expected == got, (instance, reduced, expected, got)


def main() -> None:
    results: list[bool] = []

    # --- explicit edge cases ---
    check({"n": 0, "edges": [], "k": 0}, results)   # k<=0 yes
    check({"n": 0, "edges": [], "k": -5}, results)  # k<=0 yes
    check({"n": 0, "edges": [], "k": 1}, results)   # k>n no
    check({"n": 1, "edges": [], "k": 1}, results)   # yes
    check({"n": 1, "edges": [], "k": 2}, results)   # k>n no
    check({"n": 3, "edges": [], "k": 1}, results)   # yes
    check({"n": 3, "edges": [], "k": 2}, results)   # no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3}, results)  # no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 3}, results)  # yes
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 5}, results)  # yes
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 6}, results)  # no

    # --- exhaustive over all small graphs ---
    rng = random.Random(12345)
    for n in range(0, 6):
        all_pairs = list(itertools.combinations(range(n), 2))
        trials = 1 << len(all_pairs) if len(all_pairs) <= 6 else 40
        for t in range(trials):
            if len(all_pairs) <= 6:
                mask = t
            else:
                mask = rng.randrange(1 << len(all_pairs))
            edges = [list(p) for idx, p in enumerate(all_pairs) if (mask >> idx) & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, results)

    # --- random larger instances ---
    for _ in range(300):
        n = rng.randint(0, 9)
        all_pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in all_pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k}, results)

    tests_run = len(results)
    tests_passed = sum(results)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
