"""Independent tests for reduce.py (Hamiltonian Cycle -> SAT).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answers on many small source
instances against the answers of their reductions.
"""

import itertools
import json
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Cycle
# ----------------------------------------------------------------------

def brute_force_hc(instance):
    """True iff the undirected graph has a Hamiltonian cycle."""
    n = instance["n"]
    if n <= 2:
        return False
    edges = {frozenset(e) for e in instance["edges"]}
    # Fix vertex 0 at position 0 to remove rotational symmetry.
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        ok = True
        for i in range(n):
            if frozenset((order[i], order[(i + 1) % n])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force solver for SAT (DPLL with unit propagation)
# ----------------------------------------------------------------------

def brute_force_sat(instance):
    """True iff the CNF formula is satisfiable."""
    clauses = [list(c) for c in instance["clauses"]]

    def status(clause, assignment):
        unassigned = []
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if (lit > 0) == assignment[v]:
                    return "sat", None
            else:
                unassigned.append(lit)
        if not unassigned:
            return "conflict", None
        return "open", unassigned

    def dpll(assignment):
        # Unit propagation.
        while True:
            unit = None
            for c in clauses:
                st, un = status(c, assignment)
                if st == "conflict":
                    return False
                if st == "open" and len(un) == 1:
                    unit = un[0]
                    break
            if unit is None:
                break
            v = abs(unit)
            val = unit > 0
            if v in assignment:
                if assignment[v] != val:
                    return False
            else:
                assignment = dict(assignment)
                assignment[v] = val

        # Are all clauses satisfied?
        all_sat = True
        for c in clauses:
            st, un = status(c, assignment)
            if st == "conflict":
                return False
            if st == "open":
                all_sat = False
                break
        if all_sat:
            return True

        # Branch on the first unassigned literal.
        v = None
        for c in clauses:
            st, un = status(c, assignment)
            if st == "open":
                v = abs(un[0])
                break
        for val in (True, False):
            a = dict(assignment)
            a[v] = val
            if dpll(a):
                return True
        return False

    return dpll({})


# ----------------------------------------------------------------------
# Instance enumeration
# ----------------------------------------------------------------------

def all_graphs(n):
    possible = [list(e) for e in itertools.combinations(range(n), 2)]
    for mask in range(1 << len(possible)):
        edges = [possible[i] for i in range(len(possible)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(inst)
        src = brute_force_hc(inst)
        red = reduce(inst)
        # The reduction must return a well-formed SAT instance.
        Sat.validate(red)
        tgt = brute_force_sat(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, red, tgt))

    # Exhaustive over every graph on n = 0..5 vertices.
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # Random larger instances.
    random.seed(12345)
    for n in (6, 7):
        possible = [list(e) for e in itertools.combinations(range(n), 2)]
        for _ in range(80):
            edges = [e for e in possible if random.random() < 0.5]
            check({"n": n, "edges": edges})

    # Targeted edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})   # triangle -> yes
    check({"n": 3, "edges": [[0, 1], [1, 2]]})           # path -> no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # 4-cycle -> yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})   # path -> no

    print("tests_run:", tests_run)
    print("tests_passed:", tests_passed)
    for f in failures[:10]:
        print("FAILURE:", f)

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
