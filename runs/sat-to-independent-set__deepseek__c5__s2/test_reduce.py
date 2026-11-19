"""Independent tests for reduce.py: SAT -> Independent Set.

We implement our own brute-force solvers for both problems from the
definitions in problems.py and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def sat_solve(instance: dict) -> bool:
    """Brute force CNF satisfiability."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # variable v (1..m) -> bits[v-1]
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


def independent_set_solve(instance: dict) -> bool:
    """Brute force independent set of size AT LEAST k."""
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
    # An independent set of size >= k exists iff one of size exactly k exists.
    for combo in itertools.combinations(range(n), k):
        if all(v not in adj[u] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, include edge cases)
# ----------------------------------------------------------------------

def gen_sat_instances():
    """Yield a deterministic collection of small SAT instances."""
    # All clauses over variables 1..2 (including empty, repeats, both signs).
    literals = [1, -1, 2, -2]
    possible_clauses = [[]]
    for r in (1, 2, 3):
        for combo in itertools.combinations_with_replacement(literals, r):
            possible_clauses.append(list(combo))

    # Exhaustive over small clause multisets for num_vars in 0..2.
    for m in (0, 1, 2):
        lits = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        clauses_pool = [[]]
        for r in (1, 2):
            for combo in itertools.combinations_with_replacement(lits, r):
                clauses_pool.append(list(combo))
        # all multisets of up to 3 clauses
        for size in range(0, 4):
            for combo in itertools.combinations_with_replacement(
                range(len(clauses_pool)), size
            ):
                yield {
                    "num_vars": m,
                    "clauses": [list(clauses_pool[i]) for i in combo],
                }

    # Some hand-picked edge cases.
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 0, "clauses": [[]]}
    yield {"num_vars": 3, "clauses": []}
    yield {"num_vars": 3, "clauses": [[]]}
    yield {"num_vars": 3, "clauses": [[], [1]]}
    yield {"num_vars": 3, "clauses": [[], [1, 2, 3]]}
    yield {"num_vars": 3, "clauses": [[1], [-1]]}
    yield {"num_vars": 3, "clauses": [[1, -1]]}
    yield {"num_vars": 3, "clauses": [[1, 1, 1]]}
    yield {"num_vars": 3, "clauses": [[1, -1], [1], [-1]]}
    yield {"num_vars": 4, "clauses": [[1, 2], [-1, 3], [-2, -3], [4], [-4, 1]]}

    # Random instances.
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(0, 5)
        nclauses = rng.randint(0, 6)
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
        yield {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    for instance in gen_sat_instances():
        tests_run += 1
        try:
            Sat.validate(instance)
        except problems.InvalidInstance as exc:
            failures.append(("invalid generated source", instance, str(exc)))
            continue

        expected = sat_solve(instance)
        target = reduce(instance)

        # The reduction must return a valid target instance.
        try:
            IndependentSet.validate(target)
        except problems.InvalidInstance as exc:
            failures.append(("invalid reduction output", instance, target, str(exc)))
            continue

        got = independent_set_solve(target)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(("answer mismatch", instance, expected, target, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print(f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
