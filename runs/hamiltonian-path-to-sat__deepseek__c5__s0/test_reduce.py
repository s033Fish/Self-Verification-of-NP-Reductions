"""Independent tests for reduce.py: Hamiltonian Path -> SAT.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small source
instances against the answers of their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
import reduce as reduce_module

HamiltonianPath = problems.HamiltonianPath
Sat = problems.Sat


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Path
# ----------------------------------------------------------------------

def hp_solve(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force (DPLL, complete) solver for SAT
# ----------------------------------------------------------------------

def sat_solve(instance: dict) -> bool:
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        while True:
            unit = None
            new = []
            for c in clauses:
                sat = False
                lits = []
                for lit in c:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            sat = True
                            break
                    else:
                        lits.append(lit)
                if sat:
                    continue
                if not lits:
                    return False
                if len(lits) == 1 and unit is None:
                    unit = lits[0]
                new.append(lits)
            clauses = new
            if unit is None:
                break
            v = abs(unit)
            if v in assignment:
                if assignment[v] != (unit > 0):
                    return False
            else:
                assignment = dict(assignment)
                assignment[v] = (unit > 0)
        if not clauses:
            return True
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
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    possible = [[u, v] for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [possible[i] for i in range(len(possible)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


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
        # validate source instance
        HamiltonianPath.validate(inst)
        src = hp_solve(inst)
        red = reduce_module.reduce(inst)
        # the reduction must produce a valid SAT instance
        Sat.validate(red)
        tgt = sat_solve(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, red, tgt))

    # Exhaustive over all graphs for n = 0..5
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # Random larger graphs
    rng = random.Random(12345)
    for n in (6, 7):
        for _ in range(400):
            p = rng.choice([0.2, 0.35, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng))

    # A few hand-picked edge cases
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, src, red, tgt in failures[:10]:
            print(f"  inst={inst} src={src} tgt={tgt} red={red}")

    verified = (tests_run > 0 and tests_passed == tests_run)
    with open("verdict.json", "w") as f:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict.json:", {"verified": verified, "tests_run": tests_run,
                            "tests_passed": tests_passed})
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
