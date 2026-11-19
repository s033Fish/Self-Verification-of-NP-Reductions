"""Independent tests for reduce.py (Clique -> SAT).

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, generate many small Clique instances, reduce them,
validate the resulting SAT instances, and compare the answers.

For SAT we use a DPLL solver (plus a plain brute-force solver as a
cross-check on tiny instances) so that we can cover larger reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force Clique solver

def brute_clique(instance):
    """Yes iff the graph has a clique of at least k vertices."""
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
        if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force SAT solver (tiny instances only)

def brute_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        def val(lit):
            b = (bits >> (abs(lit) - 1)) & 1
            return bool(b) if lit > 0 else not bool(b)
        if all(any(val(lit) for lit in clause) for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# DPLL SAT solver

def dpll_sat(instance):
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    # Normalise: drop duplicate literals, detect tautologies / empty clauses.
    norm = []
    for clause in clauses:
        s = set(clause)
        if any(-lit in s for lit in s):
            continue  # tautology, always satisfied
        if len(s) == 0:
            return False  # empty clause
        norm.append(s)

    def solve(clauses, assignment):
        # Unit propagation.
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 0:
                    return False
                if len(clause) == 1:
                    unit = next(iter(clause))
                    break
            if unit is None:
                break
            # Assign unit true.
            new_clauses = []
            for clause in clauses:
                if unit in clause:
                    continue  # satisfied
                if -unit in clause:
                    reduced = clause - {-unit}
                    if len(reduced) == 0:
                        return False
                    new_clauses.append(reduced)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses
            assignment.add(unit)

        if not clauses:
            return True

        # Choose a variable to branch on.
        var = abs(next(iter(next(iter(clauses)))))
        for lit in (var, -var):
            new_clauses = []
            ok = True
            for clause in clauses:
                if lit in clause:
                    continue
                if -lit in clause:
                    reduced = clause - {-lit}
                    if len(reduced) == 0:
                        ok = False
                        break
                    new_clauses.append(reduced)
                else:
                    new_clauses.append(clause)
            if ok and solve(new_clauses, assignment | {lit}):
                return True
        return False

    return solve(norm, set())


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def random_graph(n, p, rng):
    return [list(pair) for pair in itertools.combinations(range(n), 2)
            if rng.random() < p]


# ----------------------------------------------------------------------
# Test driver

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = brute_clique(instance)
        try:
            reduced = reduce(instance)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, f"reduce raised {exc!r}"))
            return
        try:
            Sat.validate(reduced)
        except InvalidInstance as exc:
            failures.append((label, instance, f"invalid SAT output: {exc}"))
            return
        got = dpll_sat(reduced)
        # Cross-check DPLL against brute force when feasible.
        if reduced["num_vars"] <= 12:
            if brute_sat(reduced) != got:
                failures.append((label, instance, "DPLL/brute SAT disagreement"))
                return
        if got != expected:
            failures.append(
                (label, instance, f"expected {expected}, got {got}, reduced={reduced}")
            )
            return
        tests_passed += 1

    # 1. Exhaustive over all graphs for n = 0..4 and all relevant k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n} k={k}")

    # 2. Exhaustive over all graphs for n = 5, all relevant k.
    for edges in all_graphs(5):
        for k in range(-1, 7):
            check({"n": 5, "edges": edges, "k": k}, "exhaustive n=5")

    # 3. Random instances up to n = 8.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, f"random n={n} k={k} p={p}")

    # 4. Specific edge cases.
    specific = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [0, 3]], "k": 3},
        {"n": 5, "edges": [[0, 1], [0, 2], [1, 2]], "k": 3},
        {"n": 5, "edges": [[0, 1], [0, 2], [1, 2]], "k": 4},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 4},
    ]
    for inst in specific:
        check(inst, "specific")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, msg in failures[:20]:
            print("---")
            print("label:", label)
            print("instance:", inst)
            print("msg:", msg)
    else:
        print("ALL PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
