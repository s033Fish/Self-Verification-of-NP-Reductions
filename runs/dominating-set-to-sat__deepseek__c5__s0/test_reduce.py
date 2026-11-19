"""Independent verification of reduce.py (DominatingSet -> Sat).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

import itertools
import random
import sys

from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for DominatingSet
# ----------------------------------------------------------------------

def ds_solve(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # try all subsets of size <= k
    for size in range(0, min(k, n) + 1):
        for D in itertools.combinations(range(n), size):
            Dset = set(D)
            if all(u in Dset or (adj[u] & Dset) for u in range(n)):
                return True
    return False


# ----------------------------------------------------------------------
# Brute-force / complete solver for Sat (DPLL with unit propagation)
# ----------------------------------------------------------------------

def sat_solve(instance):
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]
    return _dpll(clauses, num_vars)


def _dpll(clauses, num_vars):
    # unit propagation + pure literal-ish simplification, then branching
    assignment = {}
    clauses = [list(c) for c in clauses]
    while True:
        # detect empty clause
        for c in clauses:
            if len(c) == 0:
                return False
        # unit propagation
        unit = None
        for c in clauses:
            if len(c) == 1:
                unit = c[0]
                break
        if unit is None:
            break
        lit = unit
        var = abs(lit)
        val = lit > 0
        if var in assignment:
            if assignment[var] != val:
                return False
            # already assigned; remove satisfied clauses
            clauses = [c for c in clauses if lit not in c]
            clauses = [[l for l in c if l != -lit] for c in clauses]
            continue
        assignment[var] = val
        new_clauses = []
        for c in clauses:
            if lit in c:
                continue  # satisfied
            nc = [l for l in c if l != -lit]
            new_clauses.append(nc)
        clauses = new_clauses
    # all clauses have >=2 literals
    if not clauses:
        return True
    # choose a variable
    var = abs(clauses[0][0])
    for val in (True, False):
        lit = var if val else -var
        new_clauses = []
        for c in clauses:
            if lit in c:
                continue
            nc = [l for l in c if l != -lit]
            new_clauses.append(nc)
        if _dpll(new_clauses, num_vars):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
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

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate source instance
        DominatingSet.validate(instance)
        expected = ds_solve(instance)
        try:
            out = reduce(instance)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, "reduce raised %r" % (exc,)))
            return
        # validate target instance
        try:
            Sat.validate(out)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, "invalid Sat output: %r" % (exc,)))
            return
        got = sat_solve(out)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, instance, "expected %s got %s" % (expected, got)))

    # Exhaustive small graphs, all k in a range covering negatives and >= n
    for n in range(0, 5):
        for g in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": g["n"], "edges": [list(e) for e in g["edges"]], "k": k}
                check(inst, "exhaustive n=%d k=%d" % (n, k))

    # Random slightly larger graphs
    rng = random.Random(12345)
    for trial in range(400):
        n = rng.randint(0, 7)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        g = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": [list(e) for e in g["edges"]], "k": k}
        check(inst, "random trial=%d" % trial)

    # Explicit edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": -5},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 1},
    ]
    for i, inst in enumerate(edge_cases):
        check(inst, "edge_case %d" % i)


    # Structured graphs with all k (stresses Sinz cardinality boundaries)
    def structured(n):
        graphs = {}
        graphs["empty"] = []
        graphs["complete"] = [[u, v] for u in range(n) for v in range(u + 1, n)]
        graphs["path"] = [[i, i + 1] for i in range(n - 1)]
        graphs["cycle"] = [[i, (i + 1) % n] for i in range(n)] if n >= 3 else []
        graphs["star"] = [[0, i] for i in range(1, n)]
        return graphs

    for n in range(1, 10):
        for name, edges in structured(n).items():
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                check(inst, "structured %s n=%d k=%d" % (name, n, k))

    # Random n up to 9, all k values
    for trial in range(300):
        n = rng.randint(0, 9)
        g = random_graph(n, rng.random(), rng)
        for k in range(-1, n + 2):
            inst = {"n": n, "edges": [list(e) for e in g["edges"]], "k": k}
            check(inst, "random2 trial=%d k=%d" % (trial, k))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:20]:
            print("  ", f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = main()
    sys.exit(0 if not fails else 1)
