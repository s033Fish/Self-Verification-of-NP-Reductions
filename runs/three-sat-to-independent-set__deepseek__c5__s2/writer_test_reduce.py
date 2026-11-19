"""Tests comparing brute-force solvers on 3-SAT and Independent Set."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_sat(instance):
    """Brute force over all assignments of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1-indexed) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    """Brute force over all subsets of vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            s = set(combo)
            if all(not (adj[v] & s) for v in combo):
                return True
    return False


# ------------------------------------------------------------- generators

def random_three_sat(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ------------------------------------------------------------------ tests

def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        src = solve_three_sat(instance)
        tgt = solve_independent_set(reduced)
        assert src == tgt, (instance, reduced, src, tgt)
        tests_passed += 1

    # explicit edge cases
    explicit = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]] * 3},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 3], [-3, 4, -1]]},
    ]
    for inst in explicit:
        check(inst)

    # exhaustive-ish random small instances
    for _ in range(400):
        check(random_three_sat(rng))

    # exhaustive over all 3-var formulas with up to 2 clauses
    lits = [1, -1, 2, -2, 3, -3]
    all_clauses = []
    for combo in itertools.combinations(range(6), 3):
        vars_used = {abs(lits[i]) for i in combo}
        if len(vars_used) == 3:
            all_clauses.append([lits[i] for i in combo])
    for clause in all_clauses:
        check({"num_vars": 3, "clauses": [clause]})
    for c1 in all_clauses:
        for c2 in all_clauses:
            check({"num_vars": 3, "clauses": [c1, c2]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict written")


if __name__ == "__main__":
    main()
