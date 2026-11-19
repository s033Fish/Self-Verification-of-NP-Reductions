"""Tests for the SAT -> Clique reduction in reduce.py.

Includes independent brute-force solvers for both problems, then compares
their answers on many small instances against the answers of the reduced
instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def sat_solver(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # value of variable v (1-based) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solver(instance: dict) -> bool:
    """True iff the graph has a clique of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, covering edge cases).

def all_small_sat_instances():
    """Exhaustive small SAT instances: up to 3 vars, clauses from a pool."""
    # literal pool for m vars
    for m in range(0, 4):
        lits = [l for v in range(1, m + 1) for l in (v, -v)]
        # candidate clauses: empty, singletons, pairs, plus repeats/tautologies
        pool = [[]]
        pool += [[l] for l in lits]
        pool += [[a, b] for a in lits for b in lits]
        # choose up to 3 clauses (with repetition allowed) from pool
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(pool, r):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def random_sat_instances(count: int, seed: int = 12345):
    rng = random.Random(seed)
    for _ in range(count):
        m = rng.randint(0, 5)
        num_clauses = rng.randint(0, 6)
        clauses = []
        for _ in range(num_clauses):
            size = rng.randint(0, 4)
            clause = []
            for _ in range(size):
                if m == 0:
                    break
                v = rng.randint(1, m)
                clause.append(v if rng.random() < 0.5 else -v)
            clauses.append(clause)
        yield {"num_vars": m, "clauses": clauses}


def random_clique_instances(count: int, seed: int = 999):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(0, 6)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        k = rng.randint(-1, n + 2)
        yield {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(cond: bool, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            print(f"FAIL: {label}")

    # --- sanity checks on the brute-force solvers themselves ---
    check(sat_solver({"num_vars": 0, "clauses": []}) is True, "empty formula sat")
    check(sat_solver({"num_vars": 0, "clauses": [[]]}) is False, "empty clause unsat")
    check(sat_solver({"num_vars": 1, "clauses": [[1], [-1]]}) is False, "x and not x")
    check(sat_solver({"num_vars": 1, "clauses": [[1, -1]]}) is True, "tautology")
    check(clique_solver({"n": 0, "edges": [], "k": 0}) is True, "k<=0 yes")
    check(clique_solver({"n": 0, "edges": [], "k": 1}) is False, "k>n no")
    check(clique_solver({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}) is True, "triangle")
    check(clique_solver({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}) is False, "path no triangle")

    # --- exhaustive small SAT instances ---
    for inst in all_small_sat_instances():
        Sat.validate(inst)
        red = reduce(inst)
        Clique.validate(red)
        expected = sat_solver(inst)
        got = clique_solver(red)
        check(
            expected == got,
            f"exhaustive SAT {inst} -> {red}: expected {expected}, got {got}",
        )

    # --- random SAT instances ---
    for inst in random_sat_instances(3000):
        Sat.validate(inst)
        red = reduce(inst)
        Clique.validate(red)
        expected = sat_solver(inst)
        got = clique_solver(red)
        check(
            expected == got,
            f"random SAT {inst} -> {red}: expected {expected}, got {got}",
        )

    # --- random Clique instances: verify the clique solver itself ---
    for inst in random_clique_instances(2000):
        Clique.validate(inst)
        # brute force by checking all subsets of every size >= k
        n = inst["n"]
        k = inst["k"]
        adj = [[False] * n for _ in range(n)]
        for u, v in inst["edges"]:
            adj[u][v] = adj[v][u] = True
        expected = k <= 0
        if not expected:
            for size in range(max(k, 1), n + 1):
                if any(
                    all(adj[u][v] for u, v in itertools.combinations(s, 2))
                    for s in itertools.combinations(range(n), size)
                ):
                    expected = True
                    break
        check(
            clique_solver(inst) == expected,
            f"clique solver {inst}: {clique_solver(inst)} vs {expected}",
        )

    # --- structural properties of the reduction ---
    inst = {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]}
    red = reduce(inst)
    check(red["k"] == 3, "k equals number of clauses")
    check(red["n"] == 4, "n equals total literal occurrences")
    check(sat_solver(inst) == clique_solver(red), "structural example")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
