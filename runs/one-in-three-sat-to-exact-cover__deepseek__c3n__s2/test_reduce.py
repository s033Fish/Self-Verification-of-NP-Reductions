"""Tests for the 1-in-3-SAT -> Exact Cover reduction.

Includes independent brute-force solvers for both problems (problems.py
provides none) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three(instance):
    """Return True iff some assignment makes exactly one var true per clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        ok = True
        for clause in clauses:
            true_count = sum(1 for v in clause if bits[v - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """Return True iff some subcollection exactly covers the universe."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    # Backtracking on the lowest uncovered element.
    full = (1 << universe_size) - 1
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    def rec(covered):
        if covered == full:
            return True
        # lowest uncovered element
        remaining = full & ~covered
        e = (remaining & -remaining).bit_length() - 1
        for mask in masks:
            if (mask >> e) & 1 and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Helpers

def valid_source(num_vars, clauses):
    inst = {"num_vars": num_vars, "clauses": clauses}
    problems.OneInThreeSat.validate(inst)
    return inst


def check(instance):
    problems.OneInThreeSat.validate(instance)
    reduced = reduce(instance)
    problems.ExactCover.validate(reduced)
    a = solve_one_in_three(instance)
    b = solve_exact_cover(reduced)
    assert a == b, (instance, reduced, a, b)
    return a


def random_instance(rng, max_vars=7, max_clauses=5):
    num_vars = rng.randint(0, max_vars)
    if num_vars < 3:
        clauses = []
    else:
        num_clauses = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            clause = rng.sample(range(1, num_vars + 1), 3)
            clauses.append(clause)
    return valid_source(num_vars, clauses)


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # --- explicit edge cases ---
    run(valid_source(0, []))
    run(valid_source(5, []))
    run(valid_source(3, [[1, 2, 3]]))
    run(valid_source(4, [[1, 2, 3], [1, 2, 3]]))          # duplicate clause
    run(valid_source(4, [[1, 2, 3], [1, 2, 4]]))
    # parity-unsatisfiable: each var in 3 of 4 clauses
    run(valid_source(4, [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]))
    # variables not appearing
    run(valid_source(10, [[1, 2, 3]]))
    run(valid_source(6, [[4, 5, 6], [4, 5, 6], [1, 2, 3]]))

    # --- exhaustive small enumeration ---
    # all sets of clauses over 3 vars (up to a few clauses), plus 4 vars
    for num_vars in (3, 4):
        all_clauses = list(itertools.combinations(range(1, num_vars + 1), 3))
        for num_clauses in range(0, 4):
            for clauses in itertools.combinations_with_replacement(all_clauses, num_clauses):
                run(valid_source(num_vars, [list(c) for c in clauses]))

    # --- random instances ---
    rng = random.Random(12345)
    for _ in range(3000):
        run(random_instance(rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
