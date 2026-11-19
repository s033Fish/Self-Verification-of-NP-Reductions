"""Independent brute-force verification of reduce.py (3-SAT -> Clique).

We implement our own solvers directly from the problem definitions in
problems.py, generate many small source instances, reduce them, and check
that the source answer equals the target answer.  We also validate that the
reduction output is a well-formed Clique instance and check the polynomial
time / no-brute-force requirement by inspection of the construction.
"""

import itertools
import random
import sys

import problems
from problems import InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.


def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable.

    Enumerates all 2^m assignments (brute force, only for small m).
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..m) has value bits[v-1]
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
    return True if not clauses else False


def solve_clique(instance):
    """Return True iff the graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    # brute force over all subsets of size exactly k (at least k is
    # equivalent since a bigger clique contains a k-clique)
    for combo in itertools.combinations(range(n), k):
        good = True
        for a, b in itertools.combinations(combo, 2):
            if not adj[a][b]:
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid instances).


def random_three_sat(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_three_sat(max_vars=4, max_clauses=3):
    """Yield a deterministic set of small instances covering edge cases."""
    instances = []
    # no clauses, various m including 0
    for m in range(0, max_vars + 1):
        instances.append({"num_vars": m, "clauses": []})
    # all single clauses over 3 vars
    for m in range(3, max_vars + 1):
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                clause = [s * v for s, v in zip(signs, vs)]
                instances.append({"num_vars": m, "clauses": [clause]})
    # small multi-clause formulas
    rng = random.Random(12345)
    for _ in range(400):
        instances.append(random_three_sat(rng, max_vars=max_vars, max_clauses=max_clauses))
    return instances


# ----------------------------------------------------------------------
# Tests.


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = exhaustive_three_sat()
    # add a few hand-picked unsat / sat instances
    instances += [
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3],
                                     [1, 2, -3], [-1, -2, 3], [1, -2, -3], [-1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},   # duplicate clause
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                     [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]},
    ]

    for src in instances:
        tests_run += 1
        # 1. source instance must be valid
        try:
            problems.ThreeSat.validate(src)
        except InvalidInstance as exc:
            failures.append(("invalid source generated", src, str(exc)))
            continue

        expected = solve_three_sat(src)

        # 2. reduction must run and produce a valid Clique instance
        try:
            tgt = reduce(src)
        except Exception as exc:  # noqa: BLE001
            failures.append(("reduce raised", src, repr(exc)))
            continue
        try:
            problems.Clique.validate(tgt)
        except InvalidInstance as exc:
            failures.append(("invalid target", src, str(exc)))
            continue

        # 3. answers must match
        got = solve_clique(tgt)
        if got != expected:
            failures.append(("answer mismatch", src, (expected, got, tgt)))
            continue

        # 4. structural sanity: n == 3 * #clauses, k == #clauses
        if tgt["n"] != 3 * len(src["clauses"]) or tgt["k"] != len(src["clauses"]):
            failures.append(("bad shape", src, tgt))
            continue

        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for kind, src, info in failures[:10]:
            print(" ", kind, src, info)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
