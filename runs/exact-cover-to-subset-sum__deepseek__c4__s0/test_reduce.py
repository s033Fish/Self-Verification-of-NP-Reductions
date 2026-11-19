"""Tests for the Exact Cover -> Subset Sum reduction."""

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    m = len(sets)
    masks = []
    for subset in sets:
        mask = 0
        for element in subset:
            mask |= 1 << element
        masks.append(mask)
    # Try every sub-collection (each position used at most once).
    for r in range(m + 1):
        for combo in itertools.combinations(range(m), r):
            union = 0
            ok = True
            for idx in combo:
                if union & masks[idx]:
                    ok = False
                    break
                union |= masks[idx]
            if ok and union == full:
                return True
    return False


def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Deterministic edge cases

EDGE_CASES = [
    {"universe_size": 0, "sets": []},
    {"universe_size": 0, "sets": [[], []]},
    {"universe_size": 1, "sets": []},
    {"universe_size": 1, "sets": [[]]},
    {"universe_size": 1, "sets": [[0]]},
    {"universe_size": 1, "sets": [[0], [0]]},
    {"universe_size": 2, "sets": [[0], [1]]},
    {"universe_size": 2, "sets": [[0, 1]]},
    {"universe_size": 2, "sets": [[0], [0, 1]]},
    {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]},
    {"universe_size": 3, "sets": [[0, 1], [2]]},
    {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
    {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
    {"universe_size": 4, "sets": [[0, 1, 2, 3], [0], [1], [2], [3]]},
    {"universe_size": 5, "sets": [[0, 1], [2, 3], [4], [0, 2, 4], [1, 3]]},
]


def random_instance(rng):
    u = rng.randint(0, 5)
    m = rng.randint(0, 6)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u)
        subset = rng.sample(range(u), size) if u else []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def check(instance, results):
    # Both instances must be valid according to problems.py.
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)

    expected = solve_exact_cover(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (
        f"MISMATCH on {instance!r}\n  reduced={reduced!r}\n"
        f"  exact_cover={expected} subset_sum={got}"
    )
    results["tests_run"] += 1
    results["tests_passed"] += 1


def main():
    results = {"tests_run": 0, "tests_passed": 0}

    for instance in EDGE_CASES:
        check(instance, results)

    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), results)

    # Exhaustive small sweep: all set systems for u <= 3 with up to 4 sets
    # drawn from all non-empty subsets plus a couple of empty ones.
    for u in range(0, 4):
        all_subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                all_subsets.append(list(combo))
        for m in range(0, 4):
            for sets in itertools.product(all_subsets, repeat=m):
                check({"universe_size": u, "sets": [list(s) for s in sets]}, results)

    print(f"tests_run={results['tests_run']} tests_passed={results['tests_passed']}")
    assert results["tests_run"] == results["tests_passed"]

    import json
    with open("verdict.json", "w") as f:
        json.dump(
            {
                "verified": results["tests_run"] == results["tests_passed"],
                "tests_run": results["tests_run"],
                "tests_passed": results["tests_passed"],
            },
            f,
        )


if __name__ == "__main__":
    main()
