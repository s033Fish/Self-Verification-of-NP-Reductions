"""Independent tests for reduce.py: Exact Cover -> Subset Sum.

We implement our own brute-force solvers straight from the problem
definitions, generate many small source instances (including edge cases),
reduce them, and compare answers.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_exact_cover(instance: dict) -> bool:
    """Yes iff some sub-collection of sets is pairwise disjoint with union
    equal to the whole universe 0..u-1."""
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    set_masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        set_masks.append(mask)
    m = len(set_masks)
    for choice in range(1 << m):
        covered = 0
        ok = True
        for j in range(m):
            if (choice >> j) & 1:
                if covered & set_masks[j]:
                    ok = False
                    break
                covered |= set_masks[j]
        if ok and covered == full:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target (each position at most
    once)."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in instance["numbers"]:
        reachable |= {x + a for x in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation.

def random_exact_cover(rng: random.Random, max_u: int = 5, max_m: int = 6) -> dict:
    u = rng.randint(0, max_u)
    m = rng.randint(0, max_m)
    sets = []
    for _ in range(m):
        # random subset, possibly empty; duplicates naturally possible
        subset = [e for e in range(u) if rng.random() < 0.5]
        rng.shuffle(subset)
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def exhaustive_exact_covers(max_u: int = 3, max_m: int = 3):
    """All instances with universe size <= max_u and <= max_m sets, where
    each set ranges over every subset of the universe (duplicates allowed)."""
    for u in range(max_u + 1):
        all_subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                all_subsets.append(list(combo))
        for m in range(max_m + 1):
            for sets in itertools.product(all_subsets, repeat=m):
                yield {"universe_size": u, "sets": [list(s) for s in sets]}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ExactCover.validate(instance)
        expected = solve_exact_cover(instance)
        reduced = reduce(instance)
        SubsetSum.validate(reduced)
        got = solve_subset_sum(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, expected, got))

    # 1. Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 2, "sets": [[0], [1], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]
    for inst in edge_cases:
        check(inst, "edge")

    # 2. Exhaustive small enumeration.
    for inst in exhaustive_exact_covers(max_u=3, max_m=3):
        check(inst, "exhaustive")

    # 3. Random instances, including larger universe / more sets.
    for _ in range(20000):
        check(random_exact_cover(rng), "random")

    # 4. Random with more sets to exercise the base choice.
    for _ in range(5000):
        check(random_exact_cover(rng, max_u=6, max_m=10), "random-large")

    print(f"tests_run={tests_run}")
    print(f"tests_passed={tests_passed}")
    print(f"failures={len(failures)}")
    for label, inst, reduced, expected, got in failures[:10]:
        print("FAIL", label, inst, "->", reduced, "expected", expected, "got", got)

    assert not failures, "reduction mismatches found"


if __name__ == "__main__":
    main()
