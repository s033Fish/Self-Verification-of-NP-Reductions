"""Brute-force solvers and randomized tests for the Exact Cover -> SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_exact_cover(instance: dict) -> bool:
    """True iff some subfamily of the sets is an exact cover."""
    u = instance["universe_size"]
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
        if ok and covered == set(range(u)):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        if all(
            any(assignment[abs(lit)] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Tests


def check(instance: dict) -> bool:
    ExactCover.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    expected = solve_exact_cover(instance)
    got = solve_sat(target)
    assert expected == got, (instance, target, expected, got)
    return expected


def test_fixed_cases() -> int:
    cases = [
        # u = 0 is yes
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        # simple exact cover
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [2, 0]]},  # no (odd cycle)
        {"universe_size": 3, "sets": [[0, 1], [2]]},  # yes
        {"universe_size": 3, "sets": [[0], [1], [2]]},  # yes
        # element not coverable -> empty clause
        {"universe_size": 2, "sets": [[0]]},  # no
        # empty sets never matter
        {"universe_size": 2, "sets": [[], [0], [1]]},  # yes
        {"universe_size": 1, "sets": [[], []]},  # no
        # duplicate non-empty sets cannot both be chosen
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},  # yes (one copy)
        {"universe_size": 4, "sets": [[0, 1], [0, 1], [2, 3]]},  # yes
        {"universe_size": 4, "sets": [[0, 1], [0, 1], [2], [3]]},  # yes
        # overlapping alternatives
        {"universe_size": 4, "sets": [[0, 1, 2], [1, 2, 3], [0], [3]]},  # yes
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # no
    ]
    count = 0
    for case in cases:
        check(case)
        count += 1
    return count


def random_instance(rng: random.Random) -> dict:
    u = rng.randint(0, 5)
    n = rng.randint(0, 7)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u) if u else 0
        sets.append(rng.sample(range(u), size) if u else [])
    return {"universe_size": u, "sets": sets}


def test_random(trials: int = 3000) -> int:
    rng = random.Random(12345)
    count = 0
    for _ in range(trials):
        check(random_instance(rng))
        count += 1
    return count


def test_exhaustive_small() -> int:
    """Exhaustively enumerate all set systems over small universes."""
    count = 0
    for u in range(0, 4):
        all_subsets = []
        for r in range(u + 1):
            all_subsets.extend(itertools.combinations(range(u), r))
        all_subsets = [list(s) for s in all_subsets]
        # all sequences of up to 3 subsets (with repetition)
        for n in range(0, 4):
            for combo in itertools.product(all_subsets, repeat=n):
                instance = {"universe_size": u, "sets": [list(s) for s in combo]}
                check(instance)
                count += 1
    return count


if __name__ == "__main__":
    total = 0
    total += test_fixed_cases()
    total += test_exhaustive_small()
    total += test_random()
    print(f"ALL TESTS PASSED: {total} instances checked")
