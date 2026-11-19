"""Independent solvers and randomized tests for reduce.py.

We implement solvers for both problems directly from the docstrings in
problems.py, then compare answers on many small source instances.
The SAT solver is a DPLL with unit propagation (not a full 2^m scan),
so it can handle the n^2-variable formulas produced by reduce.
"""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force / DPLL solvers (written from the definitions)

def hamiltonian_path_bruteforce(instance):
    """Return True iff the graph has a Hamiltonian path (any endpoints)."""
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


def sat_solve(instance):
    """DPLL satisfiability solver for the CNF format in problems.py."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    # assignment: dict var -> bool
    def simplify(clauses, assign):
        """Return simplified clauses or None if immediately unsat."""
        new = []
        for clause in clauses:
            sat = False
            rest = []
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    val = assign[v]
                    if (lit > 0) == val:
                        sat = True
                        break
                else:
                    rest.append(lit)
            if sat:
                continue
            if not rest:
                return None  # empty clause -> unsat
            new.append(rest)
        return new

    def dpll(clauses, assign):
        clauses = simplify(clauses, assign)
        if clauses is None:
            return False
        if not clauses:
            return True
        # unit propagation
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            assign = dict(assign)
            assign[abs(unit)] = unit > 0
            clauses = simplify(clauses, assign)
            if clauses is None:
                return False
            if not clauses:
                return True
        # pure literal elimination
        while True:
            pos = set()
            neg = set()
            for clause in clauses:
                for lit in clause:
                    (pos if lit > 0 else neg).add(abs(lit))
            pure = None
            for v in pos:
                if v not in neg:
                    pure = v
                    break
            if pure is None:
                for v in neg:
                    if v not in pos:
                        pure = -v
                        break
            if pure is None:
                break
            assign = dict(assign)
            assign[abs(pure)] = pure > 0
            clauses = simplify(clauses, assign)
            if clauses is None:
                return False
            if not clauses:
                return True
        # branch on the variable in the shortest clause
        shortest = min(clauses, key=len)
        lit = shortest[0]
        for choice in (lit, -lit):
            a2 = dict(assign)
            a2[abs(choice)] = choice > 0
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


def sat_bruteforce_small(instance):
    """Exhaustive check, only used for tiny formulas as a cross-check."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    if num_vars == 0:
        return all(len(c) > 0 for c in clauses)
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            if not any(
                (bits[lit - 1] if lit > 0 else not bits[-lit - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, tag):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianPath.validate(instance)
        expected = hamiltonian_path_bruteforce(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        got = sat_solve(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((tag, instance, expected, reduced, got))

    # Exhaustive over all graphs for n = 0..5
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Random graphs for n = 6..9
    for _ in range(300):
        n = rng.randint(6, 9)
        p = rng.choice([0.15, 0.25, 0.4, 0.6, 0.85])
        check(random_graph(n, p, rng), f"random n={n}")

    # Structured cases
    for n in range(1, 11):
        path_edges = [[i, i + 1] for i in range(n - 1)]
        check({"n": n, "edges": path_edges}, f"path n={n}")
        if n >= 3:
            check({"n": n, "edges": path_edges + [[0, n - 1]]}, f"cycle n={n}")
        check({"n": n, "edges": []}, f"empty n={n}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for tag, inst, exp, red, got in failures[:10]:
            print(f"  {tag}: instance={inst} expected={exp} got={got}")
        print(f"  reduced sample: {failures[0][3]}")
    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
