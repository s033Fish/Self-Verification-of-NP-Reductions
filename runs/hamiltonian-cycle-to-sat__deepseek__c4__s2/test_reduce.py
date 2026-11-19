"""Tests for reduce.py: brute-force solvers + exhaustive/random checks."""

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_hamiltonian(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        if all(adj[order[i]][order[(i + 1) % n]] for i in range(n)):
            return True
    return False


def solve_sat_naive(instance):
    """Exhaustive truth-table check (only for tiny variable counts)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                   for l in clause) for clause in clauses):
            return True
    return False


def solve_sat_dpll(instance):
    """Simple DPLL with unit propagation; correct for any CNF."""
    clauses = [list(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False

    def simplify(clauses, lit):
        out = []
        for c in clauses:
            if lit in c:
                continue
            nc = [x for x in c if x != -lit]
            if not nc:
                return None
            out.append(nc)
        return out

    def dpll(clauses):
        if not clauses:
            return True
        # unit propagation
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
        # pure literal elimination
        lits = {l for c in clauses for l in c}
        for l in list(lits):
            if -l not in lits:
                clauses = simplify(clauses, l)
                if clauses is None:
                    return False
                if not clauses:
                    return True
                lits = {x for c in clauses for x in c}
        # branch
        l = clauses[0][0]
        for choice in (l, -l):
            nc = simplify(clauses, choice)
            if nc is not None and dpll(nc):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance):
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask >> k & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def check(inst, tests_run, tests_passed):
    HamiltonianCycle.validate(inst)
    red = reduce(inst)
    Sat.validate(red)
    expected = solve_hamiltonian(inst)
    got = solve_sat(red)
    tests_run += 1
    if expected == got:
        tests_passed += 1
    else:
        print("FAIL", inst, "expected", expected, "got", got)
    return tests_run, tests_passed


def main():
    tests_run = 0
    tests_passed = 0

    # 0. Cross-check the two SAT solvers on random small CNFs.
    rng = random.Random(999)
    for _ in range(300):
        m = rng.randint(0, 6)
        clauses = []
        for _ in range(rng.randint(0, 8)):
            clauses.append([rng.choice([1, -1]) * rng.randint(1, m)
                            for _ in range(rng.randint(0, 3))] if m else [])
        inst = {"num_vars": m, "clauses": clauses}
        Sat.validate(inst)
        a = solve_sat_naive(inst)
        b = solve_sat_dpll(inst)
        tests_run += 1
        if a == b:
            tests_passed += 1
        else:
            print("FAIL solver cross-check", inst, a, b)
    print("after solver cross-check:", tests_run, tests_passed)

    # 1. Exhaustive over all graphs with n = 0..4 (naive SAT too).
    for n in range(0, 5):
        for inst in all_graphs(n):
            HamiltonianCycle.validate(inst)
            red = reduce(inst)
            Sat.validate(red)
            expected = solve_hamiltonian(inst)
            got = solve_sat_naive(red)
            tests_run += 1
            if expected == got:
                tests_passed += 1
            else:
                print("FAIL exhaustive", inst, "expected", expected, "got", got)
                return tests_run, tests_passed
    print("after exhaustive n<=4:", tests_run, tests_passed)

    # 2. Random graphs n = 5..9.
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(5, 9)
        inst = random_graph(n, rng, rng.choice([0.2, 0.4, 0.5, 0.7, 0.9]))
        tests_run, tests_passed = check(inst, tests_run, tests_passed)
    print("after random n=5..9:", tests_run, tests_passed)

    # 3. Structured cases: cycles, paths, complete graphs.
    structured = []
    for n in range(3, 11):
        structured.append({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
        structured.append({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        structured.append({"n": n,
                           "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
        extra = [[0, 2]] if n > 3 else []
        structured.append({"n": n,
                           "edges": [[i, (i + 1) % n] for i in range(n)] + extra})
    for inst in structured:
        tests_run, tests_passed = check(inst, tests_run, tests_passed)
    print("after structured:", tests_run, tests_passed)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = main()
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")
