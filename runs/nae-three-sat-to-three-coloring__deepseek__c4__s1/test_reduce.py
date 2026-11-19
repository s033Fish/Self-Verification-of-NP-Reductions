"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

import itertools
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# --------------------------- brute-force solvers ---------------------------

def solve_nae3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                v = abs(lit)
                val = bits[v - 1]
                vals.append(val if lit > 0 else not val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def solve_3coloring(instance):
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def bt(i):
        if i == n:
            return True
        for c in range(3):
            if all(color[j] != c for j in adj[i]):
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


# --------------------------- generators ---------------------------

def random_nae_instance(rng, max_vars=5, max_clauses=5):
    m = rng.randint(0, max_vars)
    k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small_instances():
    """All NAE instances with up to 3 vars and up to 2 clauses (small)."""
    out = []
    for m in range(0, 4):
        if m < 3:
            out.append({"num_vars": m, "clauses": []})
            continue
        all_clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vs)])
        out.append({"num_vars": m, "clauses": []})
        for c in all_clauses:
            out.append({"num_vars": m, "clauses": [c]})
        for c1 in all_clauses:
            for c2 in all_clauses:
                out.append({"num_vars": m, "clauses": [c1, c2]})
    return out


# --------------------------- test driver ---------------------------

def check(instance, label):
    NaeThreeSat.validate(instance)
    target = reduce(instance)
    ThreeColoring.validate(target)
    a = solve_nae3sat(instance)
    b = solve_3coloring(target)
    if a != b:
        print(f"MISMATCH [{label}]: source={a} target={b}")
        print("  source instance:", instance)
        print("  target instance:", target)
        return False
    return True


def main():
    tests_run = 0
    tests_passed = 0

    # 1. Edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4], [1, 3, 4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4], [-1, 2, -5]]},
    ]
    for inst in edge_cases:
        tests_run += 1
        if check(inst, "edge"):
            tests_passed += 1

    # 2. Exhaustive small instances.
    for inst in exhaustive_small_instances():
        tests_run += 1
        if check(inst, "exhaustive"):
            tests_passed += 1

    # 3. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_nae_instance(rng)
        tests_run += 1
        if check(inst, "random"):
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_passed == tests_run else 1


if __name__ == "__main__":
    sys.exit(main())
