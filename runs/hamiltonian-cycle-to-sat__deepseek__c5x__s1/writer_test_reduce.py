"""Tests for the Hamiltonian Cycle -> SAT reduction in reduce.py.

Contains independent brute-force solvers for both problems (written from
the definitions in problems.py) and compares their answers on many small
instances against the answers of the reduced instances.
"""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers

def solve_hamiltonian(instance: dict) -> bool:
    """True iff the graph has a Hamiltonian cycle."""
    n = instance["n"]
    edges = instance["edges"]
    if n < 3:
        return False
    adj = {frozenset((u, v)) for u, v in edges}
    # Fix vertex 0 at the start; try orderings of the remaining vertices.
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if frozenset((a, b)) not in adj:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff the CNF formula is satisfiable (DPLL with unit propagation)."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses):
        # Unit propagation / simplification loop.
        while True:
            # Empty clause -> unsatisfiable.
            if any(len(c) == 0 for c in clauses):
                return False
            # All clauses satisfied -> satisfiable.
            if not clauses:
                return True
            # Find a unit clause.
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            # Assign unit literal to true.
            new_clauses = []
            for c in clauses:
                if unit in c:
                    continue  # clause satisfied
                reduced = [lit for lit in c if lit != -unit]
                new_clauses.append(reduced)
            clauses = new_clauses

        if any(len(c) == 0 for c in clauses):
            return False
        if not clauses:
            return True

        # Branch on the first literal.
        lit = clauses[0][0]
        for choice in (lit, -lit):
            new_clauses = []
            for c in clauses:
                if choice in c:
                    continue
                reduced = [x for x in c if x != -choice]
                new_clauses.append(reduced)
            if dpll(new_clauses):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Test harness

def check(instance: dict) -> bool:
    """Validate, reduce, validate the result, and compare answers."""
    HamiltonianCycle.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_hamiltonian(instance)
    got = solve_sat(reduced)
    if expected != got:
        print("MISMATCH", instance, "expected", expected, "got", got)
        print("reduced", reduced)
        return False
    return True


def all_graphs(n: int):
    """All simple graphs on n vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance):
            tests_passed += 1

    # Exhaustive over all graphs for n = 0..4 (2^6 = 64 graphs at n = 4).
    for n in range(0, 5):
        for g in all_graphs(n):
            run(g)

    # Random graphs for n = 5..7.
    rng = random.Random(12345)
    for n in range(5, 8):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(60):
            p = rng.random()
            edges = [list(e) for e in pairs if rng.random() < p]
            run({"n": n, "edges": edges})

    # Explicit edge cases.
    run({"n": 0, "edges": []})
    run({"n": 1, "edges": []})
    run({"n": 2, "edges": [[0, 1]]})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})   # triangle: yes
    run({"n": 3, "edges": [[0, 1], [1, 2]]})           # path: no
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # square: yes
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})   # no

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
