"""Tests for the 3-SAT -> Exact Cover reduction.

Contains independent brute-force solvers for both problems (written from the
definitions in problems.py) and compares their answers on many small random
instances and their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] == (lit > 0) for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """Return True iff the exact cover instance is solvable."""
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    full = frozenset(range(u))

    # Backtracking: always cover the smallest uncovered element.
    def search(covered):
        if covered == full:
            return True
        # pick an uncovered element
        remaining = full - covered
        target = min(remaining)
        for s in sets:
            if target in s and not (s & covered):
                if search(covered | s):
                    return True
        return False

    return search(frozenset())


# ----------------------------------------------------------------------
# Instance generation


def random_three_sat(rng, num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        if num_vars < 3:
            break
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_instances():
    """A deterministic plus random collection of small source instances."""
    instances = []
    # Edge cases: no clauses for various m (including m = 0).
    for m in range(0, 6):
        instances.append({"num_vars": m, "clauses": []})
    # All clauses over 3 variables (m = 3): every 3-subset with signs.
    m = 3
    for combo in itertools.combinations(range(1, 4), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clause = [v * s for v, s in zip(combo, signs)]
            instances.append({"num_vars": m, "clauses": [clause]})
    # Random instances.
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(3, 5)
        k = rng.randint(0, 5)
        instances.append(random_three_sat(rng, m, k))
    # Duplicate clauses and unused variables.
    instances.append({
        "num_vars": 5,
        "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3], [3, 4, 5]],
    })
    instances.append({"num_vars": 7, "clauses": [[1, 2, 3]]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    for instance in all_instances():
        problems.ThreeSat.validate(instance)
        expected = solve_three_sat(instance)

        target = reduce(instance)
        problems.ExactCover.validate(target)
        got = solve_exact_cover(target)

        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("source:", instance)
            print("expected (3-SAT):", expected)
            print("target:", target)
            print("got (exact cover):", got)

    # A couple of larger satisfiable / unsatisfiable sanity checks.
    extra = [
        ({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]]}, True),
        ({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3],
                                     [-1, -2, -3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]}, False),
    ]
    for instance, expected in extra:
        problems.ThreeSat.validate(instance)
        assert solve_three_sat(instance) == expected, instance
        target = reduce(instance)
        problems.ExactCover.validate(target)
        got = solve_exact_cover(target)
        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH (extra)", instance, expected, got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    verified = tests_run > 0 and tests_passed == tests_run
    with open("verdict.json", "w") as f:
        json.dump({"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    return verified


if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
