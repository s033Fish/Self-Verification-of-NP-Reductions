"""Tests for the 1-in-3-SAT -> 3-SAT reduction in reduce.py."""

import random

import problems
from problems import OneInThreeSat as SOURCE, ThreeSat as TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    """Compare brute-force answers on a source instance and its reduction."""
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)  # reduction must produce a well-formed target
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} got={got} "
        f"reduced={reduced}"
    )
    tests_passed += 1


def main():
    # --- Explicit edge cases -------------------------------------------------
    # No clauses is yes for any m, including 0.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []})

    # A single clause: exactly one true -> yes.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})

    # Duplicate clauses do not change the answer.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [2, 3, 1]]})

    # Variables that never appear.
    check({"num_vars": 10, "clauses": [[1, 2, 3]]})


    # Explicit unsatisfiable instances (every clause forces a different pair).
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})
    check({"num_vars": 6, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
                                       [1, 2, 5], [1, 3, 5], [2, 3, 5]]})

    # --- Exhaustive small instances -----------------------------------------
    for scale in (0, 1, 2, 3):
        for instance in SOURCE.enumerate_instances(scale):
            check(instance)

    # --- Random instances ----------------------------------------------------
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(200):
            check(SOURCE.random_instance(rng, scale))

    # A few larger random instances.
    for scale in (10, 12, 14):
        for _ in range(40):
            check(SOURCE.random_instance(rng, scale))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
