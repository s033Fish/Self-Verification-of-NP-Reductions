"""Tests for the Exact Cover -> SAT reduction.

Contains brute-force solvers written from the problem definitions, a random
instance generator, and checks that the reduction preserves the answer.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers

def solve_exact_cover(instance: dict) -> bool:
    """True iff some subfamily of sets exactly covers 0..u-1."""
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    target = (1 << u) - 1
    # Try every subset of the sets.
    for mask in range(1 << n):
        union = 0
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = 0
                for e in sets[i]:
                    s |= 1 << e
                if union & s:  # overlap -> not disjoint
                    ok = False
                    break
                union |= s
        if ok and union == target:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assignment = [(bits >> v) & 1 for v in range(m)]  # index v -> var v+1
        good = True
        for clause in clauses:
            if not any(
                (assignment[abs(lit) - 1] == 1) == (lit > 0) for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Random instance generator

def random_exact_cover(rng: random.Random, max_u: int = 4, max_sets: int = 5) -> dict:
    u = rng.randint(0, max_u)
    n = rng.randint(0, max_sets)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u)
        subset = rng.sample(range(u), size) if u > 0 else []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


# ----------------------------------------------------------------------
# Tests

def test_edge_cases() -> int:
    passed = 0
    cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [2, 0]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]},
    ]
    for inst in cases:
        ExactCover.validate(inst)
        out = reduce(inst)
        Sat.validate(out)
        a = solve_exact_cover(inst)
        b = solve_sat(out)
        assert a == b, (inst, out, a, b)
        passed += 1
    return passed


def test_random(trials: int = 3000) -> int:
    rng = random.Random(12345)
    passed = 0
    for _ in range(trials):
        inst = random_exact_cover(rng)
        ExactCover.validate(inst)
        out = reduce(inst)
        Sat.validate(out)
        a = solve_exact_cover(inst)
        b = solve_sat(out)
        assert a == b, (inst, out, a, b)
        passed += 1
    return passed


def test_exhaustive_small() -> int:
    """Exhaustively enumerate all set systems for tiny universes."""
    passed = 0
    for u in range(0, 4):
        all_subsets = []
        for r in range(u + 1):
            all_subsets.extend(itertools.combinations(range(u), r))
        all_subsets = [list(c) for c in all_subsets]
        # All families of up to 3 sets drawn from the power set.
        for n in range(0, 4):
            for family in itertools.product(all_subsets, repeat=n):
                inst = {"universe_size": u, "sets": [list(s) for s in family]}
                ExactCover.validate(inst)
                out = reduce(inst)
                Sat.validate(out)
                a = solve_exact_cover(inst)
                b = solve_sat(out)
                assert a == b, (inst, out, a, b)
                passed += 1
    return passed


if __name__ == "__main__":
    total = 0
    total += test_edge_cases()
    total += test_random()
    total += test_exhaustive_small()
    print(f"all tests passed: {total}")
