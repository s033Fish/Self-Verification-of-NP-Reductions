"""Tests for the Exact Cover -> Subset Sum reduction in reduce.py."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_exact_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    target_mask = (1 << u) - 1
    for r in range(m + 1):
        for combo in itertools.combinations(range(m), r):
            mask = 0
            ok = True
            for idx in combo:
                for element in sets[idx]:
                    bit = 1 << element
                    if mask & bit:  # element already covered
                        ok = False
                        break
                    mask |= bit
                if not ok:
                    break
            if ok and mask == target_mask:
                return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in numbers:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Helpers.


def check(instance: dict) -> bool:
    """Validate, reduce, validate, and compare the two answers."""
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = solve_exact_cover(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def all_subsets_of_universe(u: int):
    """Every subset of 0..u-1, as a sorted list."""
    elements = list(range(u))
    for r in range(u + 1):
        for combo in itertools.combinations(elements, r):
            yield list(combo)


def exhaustive_instances(max_u: int, max_sets: int):
    """All instances with universe <= max_u and at most max_sets sets."""
    for u in range(max_u + 1):
        universe_subsets = list(all_subsets_of_universe(u))
        for m in range(max_sets + 1):
            for sets in itertools.product(universe_subsets, repeat=m):
                yield {"universe_size": u, "sets": [list(s) for s in sets]}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # 1. Explicit edge cases.
    run({"universe_size": 0, "sets": []})
    run({"universe_size": 0, "sets": [[], []]})
    run({"universe_size": 1, "sets": []})
    run({"universe_size": 1, "sets": [[0]]})
    run({"universe_size": 1, "sets": [[], [0], [0]]})
    run({"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]})
    run({"universe_size": 3, "sets": [[0], [1], [2]]})
    run({"universe_size": 3, "sets": [[0, 1], [2]]})
    run({"universe_size": 3, "sets": [[0, 1, 2], [0, 1, 2]]})
    run({"universe_size": 2, "sets": [[0], [1], [0, 1], [0, 1], []]})

    # 2. Exhaustive small instances.
    for instance in exhaustive_instances(max_u=3, max_sets=3):
        run(instance)

    # 3. Random slightly larger instances.
    rng = random.Random(12345)
    for _ in range(4000):
        u = rng.randint(0, 5)
        m = rng.randint(0, 7)
        sets = []
        for _ in range(m):
            size = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), size)))
        run({"universe_size": u, "sets": sets})

    # 4. Structured random instances that are more likely to be yes.
    for _ in range(2000):
        u = rng.randint(0, 6)
        elements = list(range(u))
        rng.shuffle(elements)
        sets = []
        pos = 0
        while pos < u:
            size = rng.randint(1, max(1, u - pos))
            sets.append(sorted(elements[pos:pos + size]))
            pos += size
        for _ in range(rng.randint(0, 3)):
            size = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), size)))
        rng.shuffle(sets)
        run({"universe_size": u, "sets": sets})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
