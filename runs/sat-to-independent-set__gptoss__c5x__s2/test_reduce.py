"""Independent review of reduce.py: SAT -> Independent Set.

We implement brute-force solvers for both problems straight from the
definitions in problems.py, then compare the answer of every small source
instance with the answer of its reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def brute_sat(instance) -> bool:
    """True iff some assignment satisfies every clause."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is the value of variable v
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def brute_independent_set(instance) -> bool:
    """True iff there is an independent set of size >= k."""
    IndependentSet.validate(instance)
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
    best = 0
    # brute force over all subsets
    for r in range(n + 1):
        if r <= best:
            continue
        for comb in itertools.combinations(range(n), r):
            s = set(comb)
            if all(v not in adj[u] for u in comb for v in comb if v != u):
                best = r
                break
    return best >= k


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_sat_instance(rng, max_vars=3, max_clauses=4, max_len=3):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small():
    """All formulas with num_vars <= 2 and up to 3 clauses of length <= 2."""
    lits = [1, -1, 2, -2]
    clauses_pool = [[]]
    for r in (1, 2):
        for comb in itertools.combinations_with_replacement(lits, r):
            clauses_pool.append(list(comb))
    for m in (0, 1, 2):
        pool = [c for c in clauses_pool if all(abs(l) <= m for l in c)]
        for nclauses in range(0, 4):
            for combo in itertools.combinations_with_replacement(range(len(pool)), nclauses):
                yield {"num_vars": m, "clauses": [list(pool[i]) for i in combo]}


def targeted():
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 0, "clauses": [[]]}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 1, "clauses": [[]]}
    yield {"num_vars": 1, "clauses": [[1]]}
    yield {"num_vars": 1, "clauses": [[-1]]}
    yield {"num_vars": 1, "clauses": [[1], [-1]]}
    yield {"num_vars": 1, "clauses": [[1, -1]]}
    yield {"num_vars": 1, "clauses": [[1, 1]]}
    yield {"num_vars": 1, "clauses": [[1, 1], [-1]]}
    yield {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]}
    yield {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    yield {"num_vars": 3, "clauses": [[1], [2], [3], [-1, -2, -3]]}
    yield {"num_vars": 2, "clauses": [[1, 2], [1, 2], [-1], [-2]]}
    yield {"num_vars": 2, "clauses": [[1, -1, 2], [-2]]}
    yield {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]}
    yield {"num_vars": 2, "clauses": [[1, 2], [1, 2], [1, 2]]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    cases = list(targeted()) + list(exhaustive_small())
    rng = random.Random(12345)
    for _ in range(4000):
        cases.append(random_sat_instance(rng))
    for _ in range(3000):
        cases.append(random_sat_instance(rng, max_vars=4, max_clauses=5, max_len=3))
    for _ in range(1500):
        cases.append(random_sat_instance(rng, max_vars=6, max_clauses=6, max_len=4))

    for inst in cases:
        tests_run += 1
        try:
            Sat.validate(inst)
            src = brute_sat(inst)
            red = reduce(inst)
            IndependentSet.validate(red)
            tgt = brute_independent_set(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, f"exception: {exc!r}"))
            continue
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
