"""Brute-force solvers and tests for the Exact Cover -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ---------------------------------------------------------------- solvers
def solve_exact_cover(instance: dict) -> bool:
    """Brute force: try every sub-list of sets."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    full = set(range(u))
    for r in range(len(sets) + 1):
        for combo in itertools.combinations(range(len(sets)), r):
            union = set()
            ok = True
            for idx in combo:
                s = sets[idx]
                if union & set(s):
                    ok = False
                    break
                union |= set(s)
            if ok and union == full:
                return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Brute force: try every sub-list of numbers."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {x + a for x in reachable}
    return target in reachable


# ----------------------------------------------------------------- tests
def check(instance: dict, label: str) -> bool:
    ExactCover.validate(instance)
    expected = solve_exact_cover(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    got = solve_subset_sum(reduced)
    if expected != got:
        print(f"FAIL {label}: source={instance} expected={expected} "
              f"reduced={reduced} got={got}")
        return False
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance, label):
            tests_passed += 1

    # ---- hand-picked edge cases ----
    run({"universe_size": 0, "sets": []}, "u=0 empty")
    run({"universe_size": 0, "sets": [[], []]}, "u=0 with empty sets")
    run({"universe_size": 1, "sets": []}, "u=1 no sets")
    run({"universe_size": 1, "sets": [[0]]}, "u=1 single set")
    run({"universe_size": 1, "sets": [[], [0], [0]]}, "u=1 duplicates+empty")
    run({"universe_size": 3, "sets": [[0, 1, 2]]}, "one big set")
    run({"universe_size": 3, "sets": [[0, 1], [2]]}, "partition yes")
    run({"universe_size": 3, "sets": [[0, 1], [1, 2]]}, "overlap no")
    run({"universe_size": 3, "sets": [[0], [1], [2]]}, "singletons yes")
    run({"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 1]]}, "dup pair yes")
    run({"universe_size": 2, "sets": [[0], [0]]}, "dup same elem no")
    run({"universe_size": 3, "sets": [[0, 1], [0, 1], [2]]}, "dup big yes")
    run({"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [0, 3]]}, "cycle no")
    run({"universe_size": 4, "sets": [[0, 1], [2, 3], [1, 2], [0, 3]]}, "two covers")
    run({"universe_size": 5, "sets": [[0, 1, 2], [3, 4], [0], [2, 3]]}, "mixed")
    run({"universe_size": 6, "sets": [[0, 1, 2, 3, 4, 5]]}, "all in one")
    run({"universe_size": 6, "sets": [[0, 1], [2, 3], [4, 5], [0, 2], [1, 3]]}, "many")

    # ---- exhaustive small instances ----
    # Enumerate all set systems over universe 0..u-1 with up to `max_sets`
    # sets drawn from all non-empty subsets (plus an empty set option).
    for u in range(0, 4):
        elements = list(range(u))
        all_subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(elements, r):
                all_subsets.append(list(combo))
        for m in range(0, 4):
            for sets in itertools.product(all_subsets, repeat=m):
                run({"universe_size": u, "sets": [list(s) for s in sets]},
                    f"exhaustive u={u} m={m}")

    # ---- randomized larger instances ----
    rng = random.Random(12345)
    for trial in range(3000):
        u = rng.randint(0, 8)
        m = rng.randint(0, 8)
        sets = []
        for _ in range(m):
            size = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), size)))
        run({"universe_size": u, "sets": sets}, f"random trial {trial}")

    # ---- randomized instances biased toward solvable ----
    for trial in range(2000):
        u = rng.randint(0, 10)
        sets = []
        # random partition into pieces
        elems = list(range(u))
        rng.shuffle(elems)
        i = 0
        while i < len(elems):
            step = rng.randint(1, 3)
            sets.append(sorted(elems[i:i + step]))
            i += step
        # add noise sets
        for _ in range(rng.randint(0, 4)):
            size = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), size)))
        rng.shuffle(sets)
        run({"universe_size": u, "sets": sets}, f"partition trial {trial}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
