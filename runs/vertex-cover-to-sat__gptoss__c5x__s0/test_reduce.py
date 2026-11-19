"""Independent tests for reduce.py: Vertex Cover -> SAT.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def brute_vertex_cover(instance) -> bool:
    """True iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    verts = range(n)
    for r in range(0, k + 1):
        for subset in itertools.combinations(verts, r):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def brute_sat(instance) -> bool:
    """True iff the CNF is satisfiable.  Recursive with pruning."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    if any(len(c) == 0 for c in clauses):
        return False

    # Normalise clauses to sets of literals for quick falsification checks.
    norm = [set(c) for c in clauses]

    def rec(var, assignment):
        # assignment: dict var -> bool for vars < var
        if var > num_vars:
            return True
        for value in (False, True):
            assignment[var] = value
            ok = True
            for c in norm:
                # clause falsified if every literal is false under assignment
                falsified = True
                for lit in c:
                    v = abs(lit)
                    if v not in assignment:
                        falsified = False
                        break
                    want = lit > 0
                    if assignment[v] == want:
                        falsified = False
                        break
                if falsified:
                    ok = False
                    break
            if ok and rec(var + 1, assignment):
                return True
            del assignment[var]
        return False

    return rec(1, {})


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(inst)
        expected = brute_vertex_cover(inst)
        red = reduce(inst)
        Sat.validate(red)  # reduction must produce a valid target instance
        got = brute_sat(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, red, got))

    # Exhaustive: all graphs on n = 0..4, all k in -1..n+1
    for n in range(0, 5):
        for g in all_graphs(n):
            for k in range(-1, n + 2):
                inst = {"n": g["n"], "edges": g["edges"], "k": k}
                check(inst)

    # Random larger graphs with small k (keep SAT brute force tractable)
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(5, 7)
        g = random_graph(n, rng.random(), rng)
        k = rng.randint(-1, 3)
        inst = {"n": g["n"], "edges": g["edges"], "k": k}
        check(inst)

    # A few targeted edge cases
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
    ]
    for inst in targeted:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for f in failures[:10]:
        print("FAIL:", f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
