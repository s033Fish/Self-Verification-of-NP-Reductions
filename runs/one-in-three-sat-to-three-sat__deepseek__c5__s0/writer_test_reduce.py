"""Tests for the 1-in-3-SAT -> 3-SAT reduction.

Includes brute-force solvers for both problems (problems.py has none) and
compares answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_one_in_three(instance):
    """True iff exactly one variable in every clause can be made true."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for var in clause if bits[var - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance):
    """True iff every clause has at least one true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Test bookkeeping

tests_run = 0
tests_passed = 0


def check(condition, message):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        raise AssertionError(message)


def check_equivalence(instance):
    """Reduce, validate both, and compare brute-force answers."""
    OneInThreeSat.validate(instance)
    reduced = reduce(instance)
    ThreeSat.validate(reduced)  # must be a legal 3-SAT instance
    expected = solve_one_in_three(instance)
    got = solve_three_sat(reduced)
    check(
        expected == got,
        f"mismatch on {instance!r}: source={expected}, reduced={got}, "
        f"reduced_instance={reduced!r}",
    )


# ----------------------------------------------------------------------
# Hand-picked / edge cases

def test_edge_cases():
    # No clauses -> yes for any m, including m = 0.
    for m in range(0, 7):
        check_equivalence({"num_vars": m, "clauses": []})

    # Single clause: exactly one true -> satisfiable.
    check_equivalence({"num_vars": 3, "clauses": [[1, 2, 3]]})

    # Duplicate clauses do not change the answer.
    check_equivalence({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})

    # Variables not all used.
    check_equivalence({"num_vars": 5, "clauses": [[1, 2, 3]]})

    # Two clauses sharing variables: (1,2,3) and (1,2,4).
    # Exactly one of {1,2,3} and exactly one of {1,2,4} -> yes.
    check_equivalence({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})

    # (1,2,3) and (1,2,3) again with different ordering.
    check_equivalence({"num_vars": 3, "clauses": [[1, 2, 3], [3, 1, 2]]})


# ----------------------------------------------------------------------
# Randomized testing

def random_instance(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(rng.sample(range(1, m + 1), 3))
    return {"num_vars": m, "clauses": clauses}


def test_random():
    rng = random.Random(12345)
    for _ in range(400):
        instance = random_instance(rng)
        check_equivalence(instance)


def test_exhaustive_small():
    """All formulas over variables 1..4 with up to 3 clauses."""
    vars_ = [1, 2, 3, 4]
    all_clauses = [list(c) for c in itertools.combinations(vars_, 3)]
    for num_clauses in range(0, 4):
        for combo in itertools.product(all_clauses, repeat=num_clauses):
            instance = {"num_vars": 4, "clauses": [list(c) for c in combo]}
            check_equivalence(instance)


def main():
    test_edge_cases()
    test_random()
    test_exhaustive_small()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
