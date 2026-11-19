"""Tests for reduce.py: compare brute-force answers on source and reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_one_in_three(instance):
    """True iff some assignment makes exactly one var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(1 for v in clause if bits[v - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_sat(instance):
    """True iff some assignment satisfies every clause (>=1 true literal)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


# ----------------------------------------------------------------------
# Helpers

def valid_source(instance):
    """Minimal structural check matching the source format."""
    m = instance["num_vars"]
    for clause in instance["clauses"]:
        assert len(clause) == 3
        assert len({abs(l) for l in clause}) == 3
        assert all(l > 0 for l in clause)
        assert all(1 <= l <= m for l in clause)


def valid_target(instance):
    m = instance["num_vars"]
    for clause in instance["clauses"]:
        assert len(clause) == 3
        assert len({abs(l) for l in clause}) == 3
        assert all(1 <= abs(l) <= m for l in clause)


def random_source(rng, max_vars=6, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        clauses = []
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0

    def check(cond, msg):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            raise AssertionError(msg)

    # Explicit edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [3, 4, 5], [1, 5, 6]]},
    ]

    for inst in edge:
        valid_source(inst)
        out = reduce(inst)
        valid_target(out)
        check(solve_one_in_three(inst) == solve_three_sat(out),
              f"mismatch on {inst}")

    # Random exhaustive comparison.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_source(rng)
        valid_source(inst)
        out = reduce(inst)
        valid_target(out)
        src = solve_one_in_three(inst)
        tgt = solve_three_sat(out)
        check(src == tgt, f"mismatch: source={inst} -> target={out} "
                          f"({src} vs {tgt})")

    # Exhaustive over all 3-variable formulas with up to 2 clauses.
    triples = [list(c) for c in itertools.combinations(range(1, 4), 3)]
    for r in range(3):
        for clauses in itertools.combinations_with_replacement(triples, r):
            inst = {"num_vars": 3, "clauses": [list(c) for c in clauses]}
            out = reduce(inst)
            valid_target(out)
            check(solve_one_in_three(inst) == solve_three_sat(out),
                  f"exhaustive mismatch: {inst}")

    # Exhaustive over 4-variable formulas with up to 2 clauses.
    triples4 = [list(c) for c in itertools.combinations(range(1, 5), 3)]
    for r in range(3):
        for clauses in itertools.combinations_with_replacement(triples4, r):
            inst = {"num_vars": 4, "clauses": [list(c) for c in clauses]}
            out = reduce(inst)
            valid_target(out)
            check(solve_one_in_three(inst) == solve_three_sat(out),
                  f"exhaustive4 mismatch: {inst}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
