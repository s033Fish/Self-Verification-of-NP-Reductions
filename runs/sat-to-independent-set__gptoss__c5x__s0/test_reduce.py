"""Independent tests for reduce.py (SAT -> Independent Set).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answers on many small source
instances (including edge cases) against the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def sat_solve(instance) -> bool:
    """Brute force CNF satisfiability."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) -> bits[v-1]
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
    return False


def independent_set_solve(instance) -> bool:
    """Brute force: is there an independent set of size >= k?"""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = {frozenset(e) for e in instance["edges"]}
    # try all subsets of size exactly k (if any independent set of size >= k
    # exists then one of size exactly k exists, since subsets of independent
    # sets are independent)
    for combo in itertools.combinations(range(n), k):
        s = set(combo)
        if all(frozenset(e) not in edges for e in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_sat_instance(rng: random.Random):
    num_vars = rng.randint(0, 4)
    num_clauses = rng.randint(0, 5)
    clauses = []
    for _ in range(num_clauses):
        if num_vars == 0:
            clause = []
        else:
            length = rng.randint(0, 4)
            clause = []
            for _ in range(length):
                v = rng.randint(1, num_vars)
                clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def exhaustive_small_instances():
    """Enumerate a structured set of tiny instances."""
    instances = []
    # num_vars 0..3, clauses built from a small pool of possible clauses
    for num_vars in range(0, 4):
        if num_vars == 0:
            pool = [[]]
        else:
            lits = []
            for v in range(1, num_vars + 1):
                lits.append(v)
                lits.append(-v)
            pool = [[]]
            for r in range(1, 4):
                for combo in itertools.combinations_with_replacement(lits, r):
                    pool.append(list(combo))
        # all formulas with up to 3 clauses from the pool (with repetition)
        for c in range(0, 4):
            for clauses in itertools.combinations_with_replacement(pool, c):
                instances.append({"num_vars": num_vars, "clauses": [list(x) for x in clauses]})
    return instances


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = exhaustive_small_instances()
    # add random instances
    for _ in range(4000):
        instances.append(random_sat_instance(rng))

    for inst in instances:
        tests_run += 1
        try:
            # source must be valid
            Sat.validate(inst)
            expected = sat_solve(inst)
            out = reduce(inst)
            # target must be a valid IndependentSet instance
            IndependentSet.validate(out)
            got = independent_set_solve(out)
            if got != expected:
                failures.append((inst, out, expected, got))
                continue
            tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, None, "exception", repr(exc)))

    # Explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},                 # yes
        {"num_vars": 0, "clauses": [[]]},               # no
        {"num_vars": 1, "clauses": [[1], [-1]]},        # no
        {"num_vars": 1, "clauses": [[1, -1]]},          # yes
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]}, # no
        {"num_vars": 2, "clauses": [[1], [1]]},         # yes
        {"num_vars": 3, "clauses": [[1, 2], [-1], [-2]]},  # no
        {"num_vars": 3, "clauses": [[1, 2], [-1, 2]]},  # yes
    ]
    for inst in edge_cases:
        tests_run += 1
        try:
            Sat.validate(inst)
            expected = sat_solve(inst)
            out = reduce(inst)
            IndependentSet.validate(out)
            got = independent_set_solve(out)
            if got != expected:
                failures.append((inst, out, expected, got))
                continue
            tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, None, "exception", repr(exc)))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
