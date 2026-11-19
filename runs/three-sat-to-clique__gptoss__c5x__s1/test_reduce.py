"""Independent tests for reduce.py: brute-force 3-SAT and Clique solvers.

We implement our own solvers directly from the problem definitions in
problems.py, then compare the answers on many small instances (including
edge cases) against the answers of the reduced Clique instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.


def solve_three_sat(instance) -> bool:
    """Yes iff some assignment satisfies every clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) is bits[v-1]
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


def solve_clique(instance) -> bool:
    """Yes iff the graph has a clique of at least k vertices."""
    Clique.validate(instance)
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
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, covering edge cases).


def random_three_sat(rng, max_vars=5, max_clauses=5):
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small formulas over variables 1..3."""
    instances = []
    # No clauses, various m.
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # All single clauses over 3 vars (sign patterns), plus duplicates.
    for signs in itertools.product([1, -1], repeat=3):
        clause = [signs[i] * (i + 1) for i in range(3)]
        instances.append({"num_vars": 3, "clauses": [clause]})
        instances.append({"num_vars": 3, "clauses": [clause, list(clause)]})
    # All pairs of clauses over 3 vars.
    base = []
    for signs in itertools.product([1, -1], repeat=3):
        base.append([signs[i] * (i + 1) for i in range(3)])
    for c1 in base:
        for c2 in base:
            instances.append({"num_vars": 3, "clauses": [list(c1), list(c2)]})
    return instances


# ----------------------------------------------------------------------
# Test driver.


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_three_sat(inst)
        try:
            red = reduce(inst)
            Clique.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "reduce raised: %r" % (exc,)))
            return
        tgt = solve_clique(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    # 1. Exhaustive small formulas.
    for inst in all_small_three_sat():
        check(inst)

    # 2. Random formulas.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_three_sat(rng, max_vars=6, max_clauses=6))

    # 3. Larger random formulas (still brute-forceable).
    for _ in range(200):
        check(random_three_sat(rng, max_vars=8, max_clauses=8))

    # 4. Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 3, "clauses": []})
    # Unsatisfiable: all 8 clauses over 3 vars.
    unsat = []
    for signs in itertools.product([1, -1], repeat=3):
        unsat.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": unsat})
    # Satisfiable with duplicated clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [-1, 2, 3]]})
    # Contradictory pair -> unsat.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})

    print("tests_run:", tests_run)
    print("tests_passed:", tests_passed)
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:10]:
            print("  ", f)
    else:
        print("ALL PASSED")

    import json
    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
