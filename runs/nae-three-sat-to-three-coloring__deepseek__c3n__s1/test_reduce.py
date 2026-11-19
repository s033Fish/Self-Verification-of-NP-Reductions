"""Brute-force solvers and tests comparing NAE-3-SAT with its reduction."""

from __future__ import annotations

import itertools
import random

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def nae_sat_solver(instance: dict) -> bool:
    """True iff some assignment makes every clause not-all-equal."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for literal in clause:
                value = bits[abs(literal) - 1]
                values.append(value if literal > 0 else not value)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solver(instance: dict) -> bool:
    """True iff the graph is properly 3-colourable (backtracking)."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    colour = [-1] * n

    def backtrack(vertex: int) -> bool:
        if vertex == n:
            return True
        for c in range(3):
            if all(colour[w] != c for w in adj[vertex]):
                colour[vertex] = c
                if backtrack(vertex + 1):
                    return True
                colour[vertex] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generation.

def all_clauses(m: int) -> list[list[int]]:
    """All valid NAE-3-SAT clauses over variables 1..m."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def random_instance(rng: random.Random, m: int, max_clauses: int) -> dict:
    pool = all_clauses(m)
    k = rng.randint(0, min(max_clauses, len(pool)))
    clauses = [list(rng.choice(pool)) for _ in range(k)]
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = nae_sat_solver(instance)
        reduced = reduce(instance)
        ThreeColoring.validate(reduced)
        got = three_coloring_solver(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, reduced, got))

    # Edge cases: no clauses, m = 0..4.
    for m in range(0, 5):
        check({"num_vars": m, "clauses": []})

    # Exhaustive over all subsets of clauses for m = 3 (8 clauses -> 256).
    pool3 = all_clauses(3)
    for mask in range(1 << len(pool3)):
        clauses = [pool3[i] for i in range(len(pool3)) if (mask >> i) & 1]
        check({"num_vars": 3, "clauses": clauses})

    # Exhaustive over all subsets of clauses for m = 4 is 2^32, too many;
    # instead test many random formulas for m = 4 and m = 5.
    rng = random.Random(12345)
    for m in (4, 5):
        for _ in range(3000):
            check(random_instance(rng, m, max_clauses=6))

    # Random formulas with duplicate clauses and unused variables.
    for _ in range(2000):
        m = rng.randint(3, 6)
        pool = all_clauses(m)
        k = rng.randint(0, 5)
        clauses = [list(rng.choice(pool)) for _ in range(k)]
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for instance, expected, reduced, got in failures[:5]:
            print("  instance:", instance)
            print("  expected:", expected, "got:", got)
            print("  reduced:", reduced)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
