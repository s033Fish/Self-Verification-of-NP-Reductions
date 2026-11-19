"""Brute-force / DPLL solvers and tests for the Hamiltonian Path -> SAT reduction."""

from __future__ import annotations

import itertools
import json
import random

from reduce import reduce
from problems import Sat, HamiltonianPath


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_hamiltonian_path(instance):
    """Brute force over vertex orderings."""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for perm in itertools.permutations(range(n)):
        if all(perm[i + 1] in adj[perm[i]] for i in range(n - 1)):
            return True
    return False


def solve_sat_bruteforce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = {v + 1: bits[v] for v in range(num_vars)}
        if all(any(assignment[abs(l)] == (l > 0) for l in c) for c in clauses):
            return True
    return False


def solve_sat_dpll(instance):
    """Simple DPLL with unit propagation; correct for any CNF."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, lit):
        """Assign lit true, return simplified clause list or None on conflict."""
        new = []
        for c in clauses:
            if lit in c:
                continue
            if -lit in c:
                nc = [x for x in c if x != -lit]
                if not nc:
                    return None
                new.append(nc)
            else:
                new.append(c)
        return new

    def dpll(clauses):
        # Unit propagation.
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        # Choose a literal from the first clause.
        lit = clauses[0][0]
        for choice in (lit, -lit):
            res = simplify(clauses, choice)
            if res is not None and dpll(res):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance):
    # Use brute force for small formulas, DPLL otherwise (both exact).
    if instance["num_vars"] <= 16:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Test helpers.

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask & (1 << k)]
        yield {"n": n, "edges": edges}


def random_graph(n, rng, p=0.5):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(pair) for pair in pairs if rng.random() < p]
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianPath.validate(instance)
        src = solve_hamiltonian_path(instance)
        target = reduce(instance)
        Sat.validate(target)
        tgt = solve_sat(target)
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "src=", src, "tgt=", tgt, target)

    # Exhaustive small graphs (n <= 4 keeps brute-force SAT fast).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs, various densities and sizes.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        check(random_graph(n, rng, rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])))

    # Structured graphs.
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]})          # path: yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # cycle: yes
    check({"n": 4, "edges": [[0, 1], [2, 3]]})                          # disconnected: no
    check({"n": 3, "edges": []})                                        # no
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5],
                             [5, 0], [0, 3]]})
    check({"n": 1, "edges": []})                                        # yes
    check({"n": 0, "edges": []})                                        # no
    check({"n": 2, "edges": [[0, 1]]})                                  # yes
    check({"n": 2, "edges": []})                                        # no

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )


if __name__ == "__main__":
    main()
