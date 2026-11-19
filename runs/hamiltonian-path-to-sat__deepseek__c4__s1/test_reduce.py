"""Tests comparing brute-force answers on small instances with their reductions."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def solve_hamiltonian(instance: dict) -> bool:
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
    # DFS over simple paths.
    def dfs(v, visited):
        if len(visited) == n:
            return True
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited):
                    return True
                visited.remove(w)
        return False

    for start in range(n):
        if dfs(start, {start}):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    # DPLL with unit propagation.
    def simplify(clauses, assignment):
        new_clauses = []
        for clause in clauses:
            satisfied = False
            remaining = []
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0) == assignment[var]:
                        satisfied = True
                        break
                else:
                    remaining.append(lit)
            if satisfied:
                continue
            if not remaining:
                return None  # empty clause -> conflict
            new_clauses.append(remaining)
        return new_clauses

    def dpll(clauses, assignment):
        clauses = simplify(clauses, assignment)
        if clauses is None:
            return False
        if not clauses:
            return True
        # unit propagation
        for clause in clauses:
            if len(clause) == 1:
                lit = clause[0]
                var = abs(lit)
                new_assignment = dict(assignment)
                new_assignment[var] = lit > 0
                return dpll(clauses, new_assignment)
        # pure literal
        counts = {}
        for clause in clauses:
            for lit in clause:
                counts[lit] = counts.get(lit, 0) + 1
        for lit in counts:
            if -lit not in counts:
                var = abs(lit)
                new_assignment = dict(assignment)
                new_assignment[var] = lit > 0
                return dpll(clauses, new_assignment)
        # branch
        lit = clauses[0][0]
        var = abs(lit)
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_hamiltonian(instance)
        reduced = reduce(instance)
        got = solve_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", instance, "expected", expected, "got", got)

    # Exhaustive over all graphs on 0..5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random larger instances.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(60):
            check(random_graph(n, rng.uniform(0.1, 0.9), rng))

    # Edge cases explicitly.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 3, "edges": [[0, 1]]})

    # Validate reduced instances against the target format.
    from problems import Sat
    for n in range(0, 7):
        for g in all_graphs(n):
            Sat.validate(reduce(g))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
