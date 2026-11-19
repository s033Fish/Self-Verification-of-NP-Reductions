"""Tests for the Exact Cover -> SAT reduction.

Contains independent brute-force solvers for both problems (written from the
docstrings in problems.py) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def exact_cover_bruteforce(instance):
    """Return True iff some sub-collection of the sets is an exact cover."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = set(sets[i])
                if covered & s:  # overlap -> not disjoint
                    ok = False
                    break
                covered |= s
        if ok and len(covered) == universe_size and covered == set(range(universe_size)):
            return True
    return False


def sat_bruteforce(instance):
    """Return True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << num_vars):
        assignment = [False] * (num_vars + 1)
        for v in range(1, num_vars + 1):
            assignment[v] = bool(bits >> (v - 1) & 1)
        satisfied = True
        for clause in clauses:
            if not any(
                (lit > 0 and assignment[lit]) or (lit < 0 and not assignment[-lit])
                for lit in clause
            ):
                satisfied = False
                break
        if satisfied:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation


def all_source_instances():
    """Exhaustively enumerate small Exact Cover instances."""
    for u in range(0, 4):
        possible_sets = []
        elements = list(range(u))
        for r in range(u + 1):
            possible_sets.extend(list(c) for c in itertools.combinations(elements, r))
        for length in range(0, 5):
            for combo in itertools.product(possible_sets, repeat=length):
                yield {"universe_size": u, "sets": [list(s) for s in combo]}


def random_source_instances(count, seed=12345):
    rng = random.Random(seed)
    for _ in range(count):
        u = rng.randint(0, 6)
        n = rng.randint(0, 8)
        sets = []
        for _ in range(n):
            size = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), size)))
        yield {"universe_size": u, "sets": sets}


# ----------------------------------------------------------------------
# Tests


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(source):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both instances must be valid according to problems.py.
        ExactCover.validate(source)
        target = reduce(source)
        Sat.validate(target)
        expected = exact_cover_bruteforce(source)
        got = sat_bruteforce(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((source, target, expected, got))

    for source in all_source_instances():
        check(source)

    for source in random_source_instances(2000):
        check(source)

    # A few hand-picked edge cases.
    check({"universe_size": 0, "sets": []})
    check({"universe_size": 0, "sets": [[], []]})
    check({"universe_size": 1, "sets": []})  # element 0 uncoverable -> no
    check({"universe_size": 1, "sets": [[]]})  # still no
    check({"universe_size": 1, "sets": [[0], [0]]})  # yes, choose one
    check({"universe_size": 2, "sets": [[0], [1]]})  # yes
    check({"universe_size": 2, "sets": [[0, 1], [0], [1]]})  # yes via [0,1]
    check({"universe_size": 3, "sets": [[0, 1], [1, 2]]})  # no (1 overlaps)
    check({"universe_size": 3, "sets": [[0, 1], [2]]})  # no (1 uncovered)

    if failures:
        print(f"FAILURES: {len(failures)}")
        for source, target, expected, got in failures[:10]:
            print("  source  :", source)
            print("  target  :", target)
            print("  expected:", expected, "got:", got)
    else:
        print("All tests passed.")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed, not failures


if __name__ == "__main__":
    run_tests()
