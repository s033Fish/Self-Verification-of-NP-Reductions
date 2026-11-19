"""Independent tests for reduce.py (HamiltonianCycle -> Sat).

We implement our own brute-force solvers for both problems from the
definitions in problems.py and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Cycle (undirected).
# ----------------------------------------------------------------------

def solve_hamiltonian(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    # Fix vertex 0 at position 0 to remove rotational symmetry.
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        seq = (0,) + perm
        ok = True
        for i in range(n):
            if not adj[seq[i]][seq[(i + 1) % n]]:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# DPLL solver for SAT (handles larger variable counts than enumeration).
# ----------------------------------------------------------------------

def solve_sat(instance):
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    # Normalize: remove duplicate literals; detect tautologies.
    norm = []
    for c in clauses:
        s = set(c)
        if any(-lit in s for lit in s):
            continue  # tautology, always satisfied
        norm.append(sorted(s, key=abs))
    clauses = norm

    def dpll(clauses, assignment):
        # assignment: dict var -> bool for assigned vars
        while True:
            # Unit propagation
            unit = None
            for c in clauses:
                unassigned = []
                satisfied = False
                for lit in c:
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
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            v = abs(unit)
            assignment[v] = (unit > 0)
        # Check all clauses satisfied
        all_sat = True
        for c in clauses:
            if not any((abs(lit) in assignment and assignment[abs(lit)] == (lit > 0))
                       for lit in c):
                all_sat = False
                break
        if all_sat:
            return True
        # Choose an unassigned variable
        var = None
        for c in clauses:
            for lit in c:
                if abs(lit) not in assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return True  # everything satisfied (shouldn't reach)
        for value in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = value
            if dpll(clauses, new_assign):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for idx, p in enumerate(pairs) if (mask >> idx) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            HamiltonianCycle.validate(inst)
        except Exception as e:
            failures.append(("source invalid", inst, repr(e)))
            return
        red = reduce(inst)
        # reduction output must be a valid SAT instance
        try:
            Sat.validate(red)
        except Exception as e:
            failures.append(("bad reduction output", inst, repr(e)))
            return
        expected = solve_hamiltonian(inst)
        got = solve_sat(red)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(("mismatch", inst, f"expected={expected} got={got}"))

    # Exhaustive over all graphs for n = 0..5
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # Random graphs for n = 6..9 (DPLL on n^2 vars)
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(60):
            check(random_graph(n, rng))

    # Some structured instances: cycles and paths
    for n in range(3, 10):
        cyc = [[i, (i + 1) % n] for i in range(n)]
        check({"n": n, "edges": cyc})
        path = [[i, i + 1] for i in range(n - 1)]
        check({"n": n, "edges": path})
        complete = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": complete})

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}", flush=True)
    for f in failures[:20]:
        print("FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
