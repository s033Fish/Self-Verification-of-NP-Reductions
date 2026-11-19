"""Brute-force solvers and randomized tests for the Exact Cover -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    full = set(range(u))
    m = len(sets)
    for r in range(m + 1):
        for combo in itertools.combinations(range(m), r):
            union = []
            ok = True
            for idx in combo:
                union.extend(sets[idx])
            if len(union) != len(set(union)):
                ok = False
            if ok and set(union) == full:
                return True
    return False


def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # dp over reachable sums
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Helpers

def random_exact_cover(rng, max_u=4, max_sets=5):
    u = rng.randint(0, max_u)
    m = rng.randint(0, max_sets)
    sets = []
    for _ in range(m):
        k = rng.randint(0, u) if u > 0 else 0
        subset = rng.sample(range(u), k) if u > 0 else []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def check(instance):
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = solve_exact_cover(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    # Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 1, "sets": [[], [0], []]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0], [1, 2, 3]]},
    ]
    for inst in edge_cases:
        tests_run += 1
        check(inst)
        tests_passed += 1

    # Randomized tests.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_exact_cover(rng)
        tests_run += 1
        check(inst)
        tests_passed += 1

    # A slightly larger exhaustive-ish random batch.
    rng = random.Random(999)
    for _ in range(500):
        inst = random_exact_cover(rng, max_u=6, max_sets=7)
        tests_run += 1
        check(inst)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()


def extra_large_checks():
    """Larger instances to exercise big bases / many sets."""
    import random as _random
    rng = _random.Random(2024)
    runs = 0
    for _ in range(200):
        u = rng.randint(0, 10)
        m = rng.randint(0, 12)
        sets = []
        for _ in range(m):
            k = rng.randint(0, u) if u else 0
            sets.append(rng.sample(range(u), k) if u else [])
        inst = {"universe_size": u, "sets": sets}
        ExactCover.validate(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        assert solve_exact_cover(inst) == solve_subset_sum(red), inst
        runs += 1
    # A guaranteed-yes instance: partition of the universe.
    u = 12
    sets = [[i] for i in range(u)]
    inst = {"universe_size": u, "sets": sets}
    assert solve_exact_cover(inst) is True
    assert solve_subset_sum(reduce(inst)) is True
    runs += 1
    return runs


if __name__ == "__main__":
    tr, tp = main()
    extra = extra_large_checks()
    tr += extra
    tp += extra
    print(f"final tests_run={tr} tests_passed={tp}")
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": tr == tp, "tests_run": tr, "tests_passed": tp}, f)
