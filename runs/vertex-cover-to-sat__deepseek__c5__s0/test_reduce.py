"""Independent tests for reduce.py: Vertex Cover -> SAT.

We implement our own solvers for both problems directly from the definitions
in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import VertexCover, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the definitions, no reduce.py involved)
# ----------------------------------------------------------------------

def solve_vertex_cover(instance: dict) -> bool:
    """True iff graph has a vertex cover of size <= k (brute force)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause (DPLL + unit prop)."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for clause in clauses:
                sat = False
                unassigned = []
                for lit in clause:
                    val = assignment.get(abs(lit))
                    if val is None:
                        unassigned.append(lit)
                    elif (lit > 0) == val:
                        sat = True
                        break
                if sat:
                    continue
                if not unassigned:
                    return False  # all literals false -> conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    val = lit > 0
                    if var in assignment and assignment[var] != val:
                        return False
                    if var not in assignment:
                        assignment = dict(assignment)
                        assignment[var] = val
                        changed = True
                        continue
                new_clauses.append(unassigned)
            clauses = new_clauses
        if not clauses:
            return True
        # choose a variable from the shortest clause
        shortest = min(clauses, key=len)
        var = abs(shortest[0])
        for val in (True, False):
            a2 = dict(assignment)
            a2[var] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield edges


def make_vc(n, edges, k):
    return {"n": n, "edges": edges, "k": k}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            VertexCover.validate(inst)
        except InvalidInstance as exc:
            failures.append(("source invalid", inst, repr(exc)))
            return
        expected = solve_vertex_cover(inst)
        try:
            out = reduce(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append(("reduce raised", inst, repr(exc)))
            return
        try:
            Sat.validate(out)
        except InvalidInstance as exc:
            failures.append(("target invalid", inst, repr(exc), out))
            return
        got = solve_sat(out)
        if got != expected:
            failures.append(("mismatch", inst, expected, got, out))
            return
        tests_passed += 1

    # Exhaustive: all graphs on 0..5 vertices, k from -1 to n+1.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                check(make_vc(n, edges, k))

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]), rng)
        k = rng.randint(-2, n + 1)
        check(make_vc(n, edges, k))

    # Explicit edge cases from the definitions.
    check(make_vc(0, [], 0))          # empty graph, k=0 -> yes
    check(make_vc(0, [], -1))         # empty graph, k=-1 -> no
    check(make_vc(3, [], -1))         # no edges, k=-1 -> no
    check(make_vc(3, [], 0))          # no edges, k=0 -> yes
    check(make_vc(3, [], 5))          # no edges, k>=n -> yes
    check(make_vc(4, [[0, 1], [1, 2], [2, 3]], 1))  # path P4, k=1 -> no
    check(make_vc(4, [[0, 1], [1, 2], [2, 3]], 2))  # path P4, k=2 -> yes
    check(make_vc(3, [[0, 1], [1, 2], [0, 2]], 1))  # triangle, k=1 -> no
    check(make_vc(3, [[0, 1], [1, 2], [0, 2]], 2))  # triangle, k=2 -> yes
    check(make_vc(5, [[0, 1]], 0))    # one edge, k=0 -> no
    check(make_vc(5, [[0, 1]], 1))    # one edge, k=1 -> yes

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
