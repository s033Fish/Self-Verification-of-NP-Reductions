"""Independent tests for reduce.py (3-SAT -> Dominating Set).

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small source instances, and compare the source
answer with the target answer on the reduction.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions).

def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


def solve_dominating_set(instance: dict) -> bool:
    """True iff there is a dominating set of size at most k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for size in range(0, k + 1):
        for combo in itertools.combinations(vertices, size):
            dominated = set(combo)
            for u in combo:
                dominated |= adj[u]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_clauses(m: int):
    """All distinct 3-literal clauses over variables 1..m (order-insensitive)."""
    lits = []
    for v in range(1, m + 1):
        lits.extend([v, -v])
    seen = set()
    out = []
    for combo in itertools.permutations(lits, 3):
        if len({abs(x) for x in combo}) != 3:
            continue
        key = frozenset(combo)
        if key in seen:
            continue
        seen.add(key)
        out.append(list(combo))
    return out


def gen_instances():
    instances = []
    # No clauses, m = 0..5.
    for m in range(0, 6):
        instances.append({"num_vars": m, "clauses": []})
    # Exhaustive: m = 3, every subset of the 8 clauses over 3 variables.
    clauses3 = all_clauses(3)
    for r in range(0, len(clauses3) + 1):
        for sub in itertools.combinations(clauses3, r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in sub]})
    # Random instances for m = 3..6.
    rng = random.Random(12345)
    for _ in range(600):
        m = rng.randint(3, 6)
        pool = all_clauses(m)
        c = rng.randint(0, min(len(pool), 8))
        chosen = rng.sample(pool, c)
        instances.append({"num_vars": m, "clauses": [list(x) for x in chosen]})
    return instances


# ----------------------------------------------------------------------
# Test driver.

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []
    for inst in gen_instances():
        tests_run += 1
        SOURCE.validate(inst)
        expected = solve_three_sat(inst)
        try:
            red = reduce(inst)
            TARGET.validate(red)
            got = solve_dominating_set(red)
        except Exception as exc:  # reduction crashed or produced invalid output
            failures.append((inst, "exception: %r" % (exc,)))
            continue
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, got, red))

    print("tests_run=%d tests_passed=%d failures=%d" % (tests_run, tests_passed, len(failures)))
    for f in failures[:5]:
        print("FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
