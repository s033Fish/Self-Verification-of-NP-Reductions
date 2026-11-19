"""Independent verification of reduce.py (3-SAT -> Independent Set).

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small valid source instances, reduce them, and
compare the answers.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    problems.ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size AT LEAST k."""
    problems.IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(v not in adj[u] for i, u in enumerate(combo)
                   for v in combo[i + 1:]):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation (small, valid 3-SAT instances).

def random_three_sat(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    else:
        nclauses = 0
    return {"num_vars": m, "clauses": clauses}


def all_small_instances(max_vars: int, max_clauses: int):
    """Exhaustively enumerate a structured family of small instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        vars_ = list(range(1, m + 1))
        # all possible clauses (as frozensets of signed literals) up to relabel
        possible = []
        for vs in itertools.combinations(vars_, 3):
            for signs in itertools.product([1, -1], repeat=3):
                possible.append([s * v for s, v in zip(signs, vs)])
        for nclauses in range(0, max_clauses + 1):
            for combo in itertools.combinations(range(len(possible)), nclauses):
                yield {"num_vars": m,
                       "clauses": [possible[i] for i in combo]}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeSat.validate(inst)
        src = solve_three_sat(inst)
        red = reduce(inst)
        problems.IndependentSet.validate(red)
        tgt = solve_independent_set(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    # 1) Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                      [1, -2, 3], [-1, 2, -3],
                                      [1, 2, -3], [-1, -2, 3],
                                      [1, -2, -3], [-1, 2, 3]]})
    # duplicate clauses
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})

    # 2) Exhaustive small instances.
    for inst in all_small_instances(max_vars=3, max_clauses=3):
        check(inst)
    for inst in all_small_instances(max_vars=4, max_clauses=2):
        check(inst)

    # 3) Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_three_sat(rng, max_vars=5, max_clauses=5))
    for _ in range(1500):
        check(random_three_sat(rng, max_vars=6, max_clauses=8))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, red, src, tgt in failures[:10]:
            print("  instance:", inst)
            print("  reduced :", red)
            print("  src:", src, "tgt:", tgt)
    else:
        print("all passed")


if __name__ == "__main__":
    main()
