"""Tests for the NAE-3-SAT -> 3-Coloring reduction.

Includes brute-force solvers for both problems written directly from the
definitions in problems.py, and compares answers on many small instances.
"""

import itertools
import random

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_nae3sat(instance):
    """Return True iff some assignment makes every clause not-all-equal."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for literal in clause:
                v = abs(literal)
                val = bits[v - 1]
                if literal < 0:
                    val = not val
                values.append(val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_3coloring(instance):
    """Return True iff the graph is 3-colourable (brute force)."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def backtrack(i):
        if i == n:
            return True
        for c in range(3):
            if all(color[j] != c for j in adj[i]):
                color[i] = c
                if backtrack(i + 1):
                    return True
                color[i] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generators


def random_nae_instance(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        if m < 3:
            break
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_instances():
    """Exhaustive-ish enumeration of small NAE-3-SAT instances."""
    instances = []
    # No clauses, various m.
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3: all sign patterns of a single clause (order canonicalised).
    for signs in itertools.product((1, -1), repeat=3):
        instances.append(
            {"num_vars": 3, "clauses": [[s * (i + 1) for i, s in enumerate(signs)]]}
        )
    # m = 3: pairs of clauses over the sign patterns.
    sign_patterns = [
        [s * (i + 1) for i, s in enumerate(signs)]
        for signs in itertools.product((1, -1), repeat=3)
    ]
    for c1 in sign_patterns:
        for c2 in sign_patterns:
            instances.append({"num_vars": 3, "clauses": [c1, c2]})
    # m = 4: all single clauses over variable triples and sign patterns.
    for triple in itertools.combinations(range(1, 5), 3):
        for signs in itertools.product((1, -1), repeat=3):
            clause = [s * v for s, v in zip(signs, triple)]
            instances.append({"num_vars": 4, "clauses": [clause]})
    return instances


# ----------------------------------------------------------------------
# Tests


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        NaeThreeSat.validate(instance)
        reduced = reduce(instance)
        ThreeColoring.validate(reduced)
        expected = solve_nae3sat(instance)
        got = solve_3coloring(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, got, reduced))

    # Edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 3, "clauses": []}, "empty m=3")
    check({"num_vars": 100, "clauses": []}, "empty m=100")
    # A single clause is always satisfiable (not all equal).
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    # Unsat: every pair of variables forced equal by clauses of form (x,y,-y)?
    # Not possible with distinct vars; use known unsat NAE instance:
    # clauses (x,y,z),(x,y,-z),(x,-y,z),(x,-y,-z),(-x,y,z),(-x,y,-z),(-x,-y,z)
    # Actually the classic unsat NAE-3-SAT is all 8 clauses of a 3-var formula
    # minus one; test a known unsat one below.
    check(
        {
            "num_vars": 3,
            "clauses": [
                [1, 2, 3],
                [1, 2, -3],
                [1, -2, 3],
                [1, -2, -3],
                [-1, 2, 3],
                [-1, 2, -3],
                [-1, -2, 3],
            ],
        },
        "classic unsat 7 clauses",
    )

    # Exhaustive small instances.
    for inst in all_small_instances():
        check(inst, "exhaustive")

    # Random instances.
    rng = random.Random(12345)
    for i in range(3000):
        inst = random_nae_instance(rng, max_vars=5, max_clauses=8)
        check(inst, f"random {i}")

    # Larger random instances (still brute-forceable).
    rng = random.Random(999)
    for i in range(300):
        inst = random_nae_instance(rng, max_vars=7, max_clauses=12)
        check(inst, f"random-large {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, expected, got, reduced in failures[:5]:
            print("----", label)
            print("instance:", inst)
            print("expected:", expected, "got:", got)
            print("reduced:", reduced)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
