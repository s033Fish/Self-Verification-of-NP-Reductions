"""Tests for the 3-SAT -> Dominating Set reduction.

Includes brute-force solvers for both problems (written from the problem
definitions) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import ThreeSat, DominatingSet


# ----------------------------------------------------------------------
# Brute-force solvers

def solve_three_sat(instance: dict) -> bool:
    """Brute force 3-SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_dominating_set(instance: dict) -> bool:
    """Brute force Dominating Set: try all subsets of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            dominated = set(chosen)
            for u in chosen:
                dominated |= adj[u]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_three_sat(rng: random.Random, max_vars: int = 4, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    if m < 3:
        n_clauses = 0
    else:
        n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small 3-SAT instances."""
    instances = []
    # m = 0,1,2: only empty clause list is valid.
    for m in range(0, 3):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3: all clauses over 3 variables, and all subsets of size <= 2.
    m = 3
    all_clauses = []
    for vs in itertools.permutations([1, 2, 3]):
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([s * v for s, v in zip(signs, vs)])
    # dedupe by canonical form
    canon = []
    seen = set()
    for c in all_clauses:
        key = tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            canon.append(list(key))
    for r in range(0, 3):
        for combo in itertools.combinations(canon, r):
            instances.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        DominatingSet.validate(reduced)
        src = solve_three_sat(instance)
        tgt = solve_dominating_set(reduced)
        assert src == tgt, (
            f"MISMATCH src={src} tgt={tgt}\ninstance={instance}\nreduced={reduced}"
        )
        tests_passed += 1

    # Exhaustive small instances.
    for inst in all_small_three_sat():
        check(inst)

    # Random instances.
    rng = random.Random(12345)
    for _ in range(400):
        check(random_three_sat(rng, max_vars=4, max_clauses=5))
    for _ in range(150):
        check(random_three_sat(rng, max_vars=5, max_clauses=6))

    # Targeted edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # duplicate clauses
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [-4, 2, 3]]})
    # variable not appearing
    check({"num_vars": 5, "clauses": [[1, 2, 3]]})
    # all 8 clauses over 3 vars (unsatisfiable)
    unsat = [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ]
    check({"num_vars": 3, "clauses": unsat})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
