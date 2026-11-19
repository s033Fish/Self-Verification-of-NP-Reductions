"""Independent tests for reduce.py (3-SAT -> Clique).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small source instances (exhaustive
for tiny sizes plus randomized), reduce each, and compare answers.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def sat_solve(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[v-1] is the truth value of variable v
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def clique_solve(instance: dict) -> bool:
    """True iff the graph has a clique of at least k vertices.

    Exact branch-and-bound max-clique (bitset based) so it stays fast even
    for the somewhat larger reduced graphs.
    """
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    if k <= 0:
        return True
    if k > n:
        return False

    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    best = 0

    def expand(cand: int, size: int) -> None:
        nonlocal best
        if size + bin(cand).count("1") <= best:
            return
        if cand == 0:
            if size > best:
                best = size
            return
        # Greedy colouring bound (simple): just recurse.
        while cand:
            if size + bin(cand).count("1") <= best:
                return
            v = (cand & -cand).bit_length() - 1
            cand &= ~(1 << v)
            expand(cand & adj[v], size + 1)

    expand((1 << n) - 1, 0)
    return best >= k


# ----------------------------------------------------------------------
# Instance generation

def all_clauses_for_vars(variables):
    """All valid 3-literal clauses over the given variables (order-insensitive)."""
    clauses = []
    for combo in itertools.combinations(variables, 3):
        for signs in itertools.product((1, -1), repeat=3):
            clause = sorted((signs[i] * combo[i] for i in range(3)), key=abs)
            clauses.append(clause)
    return clauses


def gen_instances():
    """Yield many small valid ThreeSat instances."""
    # Edge case: no clauses, various m.
    for m in range(0, 5):
        yield {"num_vars": m, "clauses": []}

    # Exhaustive-ish: m = 3, all subsets of the 8 clauses, plus duplicates.
    m = 3
    pool = all_clauses_for_vars([1, 2, 3])
    assert len(pool) == 8
    for r in range(0, 5):
        for subset in itertools.combinations(range(8), r):
            yield {"num_vars": m, "clauses": [pool[i] for i in subset]}
    yield {"num_vars": 3, "clauses": list(pool)}
    yield {"num_vars": 3, "clauses": [pool[0], pool[0], pool[1]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, 3]]}

    # Random instances for m = 3..6, clause counts kept modest so the
    # brute-force clique check stays fast.
    rng = random.Random(12345)
    for m in range(3, 7):
        pool = all_clauses_for_vars(list(range(1, m + 1)))
        for _ in range(300):
            num = rng.randint(0, 6)
            clauses = [list(rng.choice(pool)) for _ in range(num)]
            yield {"num_vars": m, "clauses": clauses}

    # Larger m with few clauses.
    for m in (7, 8):
        pool = all_clauses_for_vars(list(range(1, m + 1)))
        for _ in range(150):
            num = rng.randint(0, 8)
            clauses = [list(rng.choice(pool)) for _ in range(num)]
            yield {"num_vars": m, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in gen_instances():
        # Source must be a valid instance.
        ThreeSat.validate(inst)
        expected = sat_solve(inst)

        reduced = reduce(inst)

        # Target must be a valid instance.
        Clique.validate(reduced)

        got = clique_solve(reduced)

        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, reduced, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
