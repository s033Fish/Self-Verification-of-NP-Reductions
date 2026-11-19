"""Brute-force solvers and tests comparing 3-SAT with its reduction."""

from __future__ import annotations

import itertools
import random
import sys

from problems import DominatingSet, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def sat_solve(instance: dict) -> bool:
    """Brute force 3-SAT: try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
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


def ds_solve(instance: dict) -> bool:
    """Brute force Dominating Set: is there a dominating set of size <= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    closed = [adj[v] | {v} for v in range(n)]
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            covered = set()
            for v in combo:
                covered |= closed[v]
            if len(covered) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_3sat(num_vars: int, num_clauses: int, rng: random.Random) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_small_3sat(max_vars: int = 4, max_clauses: int = 4):
    """Exhaustively enumerate small formulas (up to symmetry it is plenty)."""
    for m in range(0, max_vars + 1):
        if m == 0:
            yield {"num_vars": 0, "clauses": []}
            continue
        if m < 3:
            # Only the empty clause list is a valid instance.
            yield {"num_vars": m, "clauses": []}
            continue
        literals = [s * v for v in range(1, m + 1) for s in (1, -1)]
        possible = []
        for combo in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product((1, -1), repeat=3):
                possible.append([s * v for s, v in zip(signs, combo)])
        for r in range(0, max_clauses + 1):
            for clauses in itertools.combinations(possible, r):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


# ----------------------------------------------------------------------
# Tests

def check(instance: dict) -> bool:
    """Validate both instances and compare answers; return True if equal."""
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    DominatingSet.validate(reduced)
    expected = sat_solve(instance)
    got = ds_solve(reduced)
    if expected != got:
        print("MISMATCH")
        print("  source:", instance)
        print("  target:", reduced)
        print("  sat_solve =", expected, " ds_solve =", got)
        return False
    return True


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance):
            tests_passed += 1

    # 1. Hand-picked edge cases.
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 1, "clauses": []})
    run({"num_vars": 5, "clauses": []})
    run({"num_vars": 3, "clauses": [[1, 2, 3]]})
    run({"num_vars": 3, "clauses": [[1, 2, -3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})  # duplicate clause
    # Unsatisfiable: all 8 clauses over 3 vars.
    run({"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]})
    # Variables that never appear.
    run({"num_vars": 6, "clauses": [[1, 2, 3]]})

    # 2. Exhaustive small formulas.
    for instance in all_small_3sat(max_vars=4, max_clauses=4):
        run(instance)

    # 3. Random formulas of various sizes.
    rng = random.Random(12345)
    for _ in range(3000):
        m = rng.randint(0, 6)
        if m < 3:
            clauses = []
        else:
            clauses = random_3sat(m, rng.randint(0, 8), rng)["clauses"]
        run({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
