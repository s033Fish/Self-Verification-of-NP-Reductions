"""Brute-force solvers and randomized tests for the Exact Cover -> SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_exact_cover(instance: dict) -> bool:
    """Try every sub-collection of sets; yes iff one is an exact cover."""
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = sets[i]
                # pairwise disjoint
                if covered & set(s):
                    ok = False
                    break
                covered |= set(s)
        if ok and covered == set(range(u)):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        if all(
            any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers.

def random_exact_cover(rng: random.Random) -> dict:
    u = rng.randint(0, 5)
    n = rng.randint(0, 6)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u)
        elements = rng.sample(range(u), size) if u else []
        rng.shuffle(elements)
        sets.append(elements)
    return {"universe_size": u, "sets": sets}


def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Source must be a valid Exact Cover instance.
        ExactCover.validate(instance)
        target = reduce(instance)
        # Target must be a valid SAT instance.
        Sat.validate(target)
        expected = solve_exact_cover(instance)
        got = solve_sat(target)
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("  instance:", instance)
            print("  reduced :", target)
            print("  exact cover:", expected, " sat:", got)

    # Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},                       # yes, no sets
        {"universe_size": 0, "sets": [[], []]},                 # yes, empty sets
        {"universe_size": 1, "sets": []},                       # no
        {"universe_size": 1, "sets": [[0]]},                    # yes
        {"universe_size": 1, "sets": [[0], [0]]},               # yes (one copy)
        {"universe_size": 2, "sets": [[0], [1]]},               # yes
        {"universe_size": 2, "sets": [[0, 1]]},                 # yes
        {"universe_size": 2, "sets": [[0], [0, 1]]},            # no (overlap, 1 uncovered)
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]}, # no
        {"universe_size": 3, "sets": [[0, 1], [2]]},            # yes
        {"universe_size": 2, "sets": [[], [0], [1]]},           # yes, empty free
        {"universe_size": 2, "sets": [[0], [0], [1], [1]]},     # yes
        {"universe_size": 2, "sets": [[0], [0]]},               # no (1 uncovered)
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},  # yes
    ]
    for instance in edge_cases:
        check(instance)

    # Randomized tests.
    rng = random.Random(12345)
    for _ in range(400):
        check(random_exact_cover(rng))

    # Exhaustive small enumeration: all set systems with u <= 3, n <= 3.
    for u in range(0, 4):
        all_subsets = []
        for r in range(0, u + 1):
            all_subsets.extend(list(c) for c in itertools.combinations(range(u), r))
        for n in range(0, 4):
            for combo in itertools.product(all_subsets, repeat=n):
                check({"universe_size": u, "sets": [list(s) for s in combo]})

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")
