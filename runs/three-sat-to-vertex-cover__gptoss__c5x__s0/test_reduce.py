"""Independent tests for reduce.py: 3-SAT -> Vertex Cover.

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answers of many small source
instances with the answers of their reductions.
"""

from __future__ import annotations

import itertools
import json
import random
from functools import lru_cache

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def solve_three_sat(instance) -> bool:
    """Try every assignment of variables 1..m."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_vertex_cover(instance) -> bool:
    """Exact vertex cover via recursive branching on an uncovered edge."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    edge_set = frozenset(frozenset(e) for e in edges)

    @lru_cache(maxsize=None)
    def rec(remaining, budget):
        if not remaining:
            return True
        if budget == 0:
            return False
        # pick an uncovered edge
        e = next(iter(remaining))
        u, v = tuple(e)
        for chosen in (u, v):
            nxt = frozenset(x for x in remaining if chosen not in x)
            if rec(nxt, budget - 1):
                return True
        return False

    return rec(edge_set, k)


# ----------------------------------------------------------------------
# Instance generation

def random_three_sat(rng, max_vars=4, max_clauses=3):
    m = rng.randint(0, max_vars)
    c = rng.randint(0, max_clauses)
    if m < 3:
        c = 0  # clauses need at least 3 variables
    clauses = []
    for _ in range(c):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver

def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_three_sat(inst)
        target = reduce(inst)
        # The reduction must produce a valid target instance.
        VertexCover.validate(target)
        tgt = solve_vertex_cover(target)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, inst, src, target, tgt))

    # Explicit edge cases.
    explicit = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, -3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},  # duplicate clause
    ]
    for i, inst in enumerate(explicit):
        check(inst, f"explicit-{i}")

    # Random tests.
    for i in range(2000):
        inst = random_three_sat(rng)
        check(inst, f"random-{i}")

    # Exhaustive over all 3-variable formulas with up to 2 clauses.
    all_clauses = [list(c) for c in itertools.combinations(
        [1, -1, 2, -2, 3, -3], 3)
        if len({abs(x) for x in c}) == 3]
    for c1 in all_clauses:
        check({"num_vars": 3, "clauses": [c1]}, f"exh1-{c1}")
    for c1 in all_clauses:
        for c2 in all_clauses:
            check({"num_vars": 3, "clauses": [c1, c2]}, f"exh2-{c1}-{c2}")

    # Exhaustive over all 4-variable formulas with 1 clause (larger m).
    all_clauses4 = [list(c) for c in itertools.combinations(
        [1, -1, 2, -2, 3, -3, 4, -4], 3)
        if len({abs(x) for x in c}) == 3]
    for c1 in all_clauses4:
        check({"num_vars": 4, "clauses": [c1]}, f"exh4-{c1}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("ALL PASSED")

    verified = (tests_run == tests_passed)
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict written:", verified)


if __name__ == "__main__":
    main()
