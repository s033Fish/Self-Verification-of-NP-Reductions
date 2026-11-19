"""Tests comparing brute-force NAE-3-SAT answers with brute-force
3-colourability answers of the reduced graphs."""

import itertools
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_nae3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                val = bits[abs(lit) - 1]
                values.append(val if lit > 0 else not val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_3coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def bt(i):
        if i == n:
            return True
        for c in range(3):
            if all(colour[j] != c for j in adj[i]):
                colour[i] = c
                if bt(i + 1):
                    return True
                colour[i] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generation.

def random_formula(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    if m < 3:
        # clauses require m >= 3; otherwise no clauses
        return {"num_vars": m, "clauses": []}
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_formulas(max_vars=4, max_clauses=3):
    """Exhaustively enumerate small formulas."""
    out = []
    for m in range(0, max_vars + 1):
        if m < 3:
            out.append({"num_vars": m, "clauses": []})
            continue
        # all possible clauses over 3 distinct vars, both signs
        possible = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                possible.append([s * v for s, v in zip(signs, vs)])
        for k in range(0, max_clauses + 1):
            for combo in itertools.combinations(possible, k):
                out.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return out


def check(instance, label):
    NaeThreeSat.validate(instance)
    reduced = reduce(instance)
    ThreeColoring.validate(reduced)
    a = solve_nae3sat(instance)
    b = solve_3coloring(reduced)
    assert a == b, f"MISMATCH {label}: source={a} target={b}\n{instance}\n{reduced}"
    return a, b


def main():
    tests_run = 0
    tests_passed = 0

    # 1. Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
    ]
    for inst in edge_cases:
        tests_run += 1
        check(inst, "edge")
        tests_passed += 1

    # 2. Exhaustive small formulas.
    for inst in all_small_formulas(max_vars=4, max_clauses=3):
        tests_run += 1
        check(inst, "exhaustive")
        tests_passed += 1

    # 3. Random formulas.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_formula(rng, max_vars=5, max_clauses=5)
        tests_run += 1
        check(inst, "random")
        tests_passed += 1


    # 4. Larger random formulas (still brute-forceable).
    for _ in range(200):
        m = rng.randint(3, 8)
        clauses = []
        for _ in range(rng.randint(0, 8)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        tests_run += 1
        check(inst, "large")
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
