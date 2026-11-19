"""Brute-force solvers and tests for the Exact Cover -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_exact_cover(instance) -> bool:
    """Yes iff some sub-collection is pairwise disjoint and covers 0..u-1."""
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    m = len(sets)
    for mask in range(1 << m):
        union = set()
        ok = True
        for i in range(m):
            if (mask >> i) & 1:
                if union & sets[i]:          # not pairwise disjoint
                    ok = False
                    break
                union |= sets[i]
        if ok and len(union) == u:           # covers the whole universe
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """Yes iff some sub-list (each position at most once) sums to target."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in instance["numbers"]:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators for small Exact Cover instances.

def random_exact_cover(rng: random.Random):
    u = rng.randint(0, 5)
    m = rng.randint(0, 6)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u)
        elements = rng.sample(range(u), size)
        sets.append(elements)
    # Occasionally duplicate an existing set to exercise that edge case.
    if sets and rng.random() < 0.3:
        sets.append(list(rng.choice(sets)))
    return {"universe_size": u, "sets": sets}


def exhaustive_small_instances():
    """All instances with u <= 3 and sets drawn from the non-empty subsets."""
    for u in range(0, 4):
        all_subsets = []
        for r in range(0, u + 1):
            all_subsets.extend([list(c) for c in itertools.combinations(range(u), r)])
        # All collections of up to 3 sets (with repetition allowed).
        for m in range(0, 4):
            for combo in itertools.product(all_subsets, repeat=m):
                yield {"universe_size": u, "sets": [list(s) for s in combo]}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_exact_cover(instance)
        reduced = reduce(instance)
        # The reduction must produce a valid Subset Sum instance.
        assert set(reduced) == {"numbers", "target"}, reduced
        assert all(isinstance(a, int) and a >= 0 for a in reduced["numbers"])
        assert isinstance(reduced["target"], int)
        got = solve_subset_sum(reduced)
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)

    # 1) Exhaustive tiny instances.
    for instance in exhaustive_small_instances():
        check(instance)

    # 2) Random small instances.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_exact_cover(rng))

    # 3) Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},                       # yes (empty)
        {"universe_size": 0, "sets": [[], []]},                 # yes
        {"universe_size": 1, "sets": []},                       # no
        {"universe_size": 1, "sets": [[]]},                     # no
        {"universe_size": 1, "sets": [[0]]},                    # yes
        {"universe_size": 1, "sets": [[0], [0]]},               # yes (one copy)
        {"universe_size": 2, "sets": [[0], [1]]},               # yes
        {"universe_size": 2, "sets": [[0, 1]]},                 # yes
        {"universe_size": 2, "sets": [[0], [0]]},               # no
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]}, # no (overlaps)
        {"universe_size": 3, "sets": [[0, 1], [2]]},            # yes
        {"universe_size": 3, "sets": [[0, 1], [2], [0, 1]]},    # yes (one copy)
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [1, 2]]}, # yes
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
