"""Tests for the 3-SAT -> 1-in-3-SAT reduction in reduce.py.

Brute-force / backtracking solvers for both problems are implemented straight
from the definitions in problems.py, then answers are compared on many small
random source instances and on hand-picked edge cases.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every 3-SAT clause (brute force)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                   for l in clause) for clause in clauses):
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    """Exact backtracking solver for positive 1-in-3-SAT with propagation."""
    n = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]
    if n == 0:
        return len(clauses) == 0

    val = [None] * (n + 1)  # 1..n

    def propagate() -> bool:
        changed = True
        while changed:
            changed = False
            for (a, b, c) in clauses:
                assigned = [(v, val[v]) for v in (a, b, c) if val[v] is not None]
                ntrue = sum(1 for _, t in assigned if t)
                nfalse = len(assigned) - ntrue
                if ntrue > 1 or nfalse > 2:
                    return False
                if ntrue == 1:
                    for v in (a, b, c):
                        if val[v] is None:
                            val[v] = False
                            changed = True
                elif nfalse == 2:
                    for v in (a, b, c):
                        if val[v] is None:
                            val[v] = True
                            changed = True
        return True

    def rec() -> bool:
        saved = val[:]
        if not propagate():
            val[:] = saved
            return False
        # all clauses satisfied?
        done = True
        for (a, b, c) in clauses:
            if val[a] is None or val[b] is None or val[c] is None:
                done = False
                break
        if done:
            return True
        # branch on an unassigned variable appearing in some clause
        pick = None
        for (a, b, c) in clauses:
            for v in (a, b, c):
                if val[v] is None:
                    pick = v
                    break
            if pick is not None:
                break
        for choice in (True, False):
            val[pick] = choice
            if rec():
                return True
            val[:] = saved
        val[:] = saved
        return False

    return rec()


# ----------------------------------------------------------------------
# Random instance generation

def random_three_sat(rng: random.Random, m: int, n_clauses: int) -> dict:
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeSat.validate(instance)
        reduced = reduce(instance)
        problems.OneInThreeSat.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_one_in_three_sat(reduced)
        assert got == expected, (
            f"MISMATCH\nsource={instance}\nexpected={expected} got={got}\n"
            f"reduced={reduced}"
        )
        tests_passed += 1

    # Edge cases: no clauses, various m including 0.
    for m in range(0, 8):
        check({"num_vars": m, "clauses": []})

    # Hand-picked small instances.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 1, 2], [-4, -1, -2]]})
    # Unsat: all 8 sign patterns over 3 vars.
    all_signs = []
    for s in itertools.product([1, -1], repeat=3):
        all_signs.append([s[0] * 1, s[1] * 2, s[2] * 3])
    check({"num_vars": 3, "clauses": all_signs})

    # Random instances over small variable counts.
    rng = random.Random(12345)
    for _ in range(500):
        m = rng.randint(3, 7)
        n_clauses = rng.randint(0, 12)
        check(random_three_sat(rng, m, n_clauses))

    # More clauses to stress satisfiability structure.
    for _ in range(100):
        m = rng.randint(3, 6)
        n_clauses = rng.randint(0, 30)
        check(random_three_sat(rng, m, n_clauses))

    # Duplicate clauses should not matter.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
