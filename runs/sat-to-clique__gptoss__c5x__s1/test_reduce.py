"""Independent tests for reduce.py (SAT -> Clique).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def sat_solve(instance) -> bool:
    """True iff some assignment satisfies every clause."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Any empty clause => unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance) -> bool:
    """True iff the graph has a clique of at least k vertices."""
    Clique.validate(instance)
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    # Existence of a clique of size exactly k (any larger clique contains one).
    for combo in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_sat(rng: random.Random):
    m = rng.randint(0, 4)
    nclauses = rng.randint(0, 4)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, 3)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def explicit_instances():
    return [
        # no clauses -> yes
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        # empty clause -> no
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 2, "clauses": [[1], []]},
        # single unit clauses
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        # tautology
        {"num_vars": 1, "clauses": [[1, -1]]},
        # repeated literals
        {"num_vars": 1, "clauses": [[1, 1]]},
        {"num_vars": 1, "clauses": [[1, 1], [-1]]},
        # duplicate clauses
        {"num_vars": 1, "clauses": [[1], [1]]},
        # both polarities across clauses
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        # unused variables
        {"num_vars": 5, "clauses": [[1], [-2]]},
    ]


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            expected = sat_solve(inst)
            red = reduce(inst)
            # reduction output must be a valid Clique instance
            Clique.validate(red)
            got = clique_solve(red)
            if got == expected:
                tests_passed += 1
            else:
                failures.append((label, inst, red, expected, got))
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, None, "exception", repr(exc)))

    for i, inst in enumerate(explicit_instances()):
        check(inst, f"explicit[{i}]")

    rng = random.Random(12345)
    N_RANDOM = 3000
    for i in range(N_RANDOM):
        inst = random_sat(rng)
        check(inst, f"random[{i}]")

    # A few larger random instances (still brute-forceable).
    rng2 = random.Random(999)
    for i in range(200):
        m = rng2.randint(1, 6)
        nclauses = rng2.randint(1, 5)
        clauses = []
        for _ in range(nclauses):
            length = rng2.randint(1, 3)
            clauses.append([rng2.choice([1, -1]) * rng2.randint(1, m)
                            for _ in range(length)])
        check({"num_vars": m, "clauses": clauses}, f"larger[{i}]")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------
# Exhaustive small-instance enumeration (appended)
# ----------------------------------------------------------------------

def _clause_pool(m, max_len):
    lits = []
    for v in range(1, m + 1):
        lits += [v, -v]
    pool = []
    for length in range(0, max_len + 1):
        for c in itertools.product(lits, repeat=length):
            pool.append(list(c))
    return pool


def exhaustive_instances(max_m=2, max_clauses=2, max_len=2):
    for m in range(0, max_m + 1):
        pool = _clause_pool(m, max_len)
        for nc in range(0, max_clauses + 1):
            for combo in itertools.product(pool, repeat=nc):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def run_exhaustive():
    run = passed = 0
    fails = []
    for inst in exhaustive_instances():
        run += 1
        exp = sat_solve(inst)
        red = reduce(inst)
        Clique.validate(red)
        got = clique_solve(red)
        if exp == got:
            passed += 1
        else:
            fails.append((inst, red, exp, got))
    return run, passed, fails
