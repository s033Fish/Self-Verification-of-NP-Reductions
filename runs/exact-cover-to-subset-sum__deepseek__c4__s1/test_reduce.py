"""Tests comparing brute-force answers with the reduction's answers."""

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    full = set(range(u))
    for mask in range(1 << m):
        covered = set()
        ok = True
        for j in range(m):
            if mask & (1 << j):
                s = set(sets[j])
                if covered & s:          # not pairwise disjoint
                    ok = False
                    break
                covered |= s
        if ok and covered == full:
            return True
    return False


def solve_subset_sum(instance):
    target = instance["target"]
    numbers = instance["numbers"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {r + a for r in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators.

def random_exact_cover(rng, max_u=5, max_sets=5):
    u = rng.randint(0, max_u)
    m = rng.randint(0, max_sets)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u) if u > 0 else 0
        elems = rng.sample(range(u), size)
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


def all_small_instances(max_u=3, max_sets=3):
    """Exhaustively enumerate small instances (subsets of the power set)."""
    for u in range(0, max_u + 1):
        all_subsets = []
        for r in range(u + 1):
            all_subsets.extend(list(c) for c in itertools.combinations(range(u), r))
        for m in range(0, max_sets + 1):
            for combo in itertools.product(all_subsets, repeat=m):
                yield {"universe_size": u, "sets": [list(s) for s in combo]}


# ----------------------------------------------------------------------
# Tests.

def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_exact_cover(instance)
        reduced = reduce(instance)
        got = solve_subset_sum(reduced)
        if expected != got:
            print("MISMATCH", instance, "expected", expected, "got", got,
                  "reduced", reduced)
            return
        tests_passed += 1

    # Exhaustive small instances.
    for inst in all_small_instances(max_u=3, max_sets=3):
        check(inst)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_exact_cover(rng, max_u=6, max_sets=7))

    # Explicit edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 3, "sets": []},
        {"universe_size": 3, "sets": [[], [0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]},
        {"universe_size": 2, "sets": [[0], [0], [1], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 1, 2, 3]]},
    ]
    for inst in edge_cases:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
