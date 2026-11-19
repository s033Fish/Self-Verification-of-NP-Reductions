"""Independent review tests for reduce.py (SAT -> Independent Set).

We implement brute-force solvers for both problems straight from the
docstrings in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the documented definitions)

def brute_sat(instance):
    """Return True iff the CNF formula is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # An empty clause can never be satisfied.
    if any(len(c) == 0 for c in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def brute_is(instance):
    """Return True iff the graph has an independent set of size >= k."""
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
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (adj[u] & s) for u in subset):
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    try:
        Sat.validate(instance)
        expected = brute_sat(instance)
        out = reduce(instance)
        IndependentSet.validate(out)
        got = brute_is(out)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, out, got))
    except Exception as exc:  # noqa: BLE001
        failures.append((label, instance, "EXC", repr(exc), None))


# ----------------------------------------------------------------------
# 1. Hand-picked edge cases

hand = [
    # no clauses -> satisfiable
    {"num_vars": 0, "clauses": []},
    {"num_vars": 3, "clauses": []},
    # empty clause -> unsat
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 2, "clauses": [[]]},
    {"num_vars": 2, "clauses": [[], [1]]},
    {"num_vars": 2, "clauses": [[1], []]},
    {"num_vars": 2, "clauses": [[1, 2], [], [-1]]},
    # unit clauses
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    # tautologies
    {"num_vars": 1, "clauses": [[1, -1]]},
    {"num_vars": 2, "clauses": [[1, -1], [2]]},
    # repeated literals / clauses
    {"num_vars": 1, "clauses": [[1, 1, 1]]},
    {"num_vars": 1, "clauses": [[1], [1], [1]]},
    {"num_vars": 2, "clauses": [[1, 2], [1, 2]]},
    # unused variables
    {"num_vars": 5, "clauses": [[1]]},
    # classic unsat
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 2, "clauses": [[1], [2], [-1, -2]]},
]
for i, inst in enumerate(hand):
    check(inst, f"hand[{i}]")


# ----------------------------------------------------------------------
# 2. Exhaustive small enumeration

# All clauses over variables 1..m with length 0..2 (as tuples), allowing
# repeated literals and tautologies.  Then all formulas with 0..2 clauses.
for m in range(0, 3):
    literals = [l for v in range(1, m + 1) for l in (v, -v)]
    pool = [()]
    pool += [(l,) for l in literals]
    pool += [(a, b) for a in literals for b in literals]
    pool = sorted(set(pool))
    for r in range(0, 3):
        for combo in itertools.combinations_with_replacement(pool, r):
            inst = {"num_vars": m, "clauses": [list(c) for c in combo]}
            check(inst, f"exh m={m} r={r}")


# ----------------------------------------------------------------------
# 3. Random small instances

rng = random.Random(123456789)
for t in range(4000):
    m = rng.randint(0, 4)
    nclauses = rng.randint(0, 5)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    check({"num_vars": m, "clauses": clauses}, f"random[{t}]")


# ----------------------------------------------------------------------
# Report

print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print(f"FAILURES: {len(failures)}")
    for label, inst, expected, out, got in failures[:10]:
        print("----", label)
        print("  instance:", inst)
        print("  expected:", expected)
        print("  reduced :", out)
        print("  got     :", got)
else:
    print("ALL TESTS PASSED")

# Save counts for verdict generation.
with open("_test_counts.txt", "w") as fh:
    fh.write(f"{tests_run} {tests_passed}\n")
