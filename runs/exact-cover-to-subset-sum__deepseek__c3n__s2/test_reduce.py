"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import exact_cover, subset_sum

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = exact_cover(instance)
    got = subset_sum(reduced)
    assert got == expected, (instance, reduced, expected, got)
    tests_passed += 1


# ---- Exhaustive: all set systems over tiny universes -------------------
def all_subsets(u):
    return [list(c) for r in range(u + 1) for c in itertools.combinations(range(u), r)]


for u in range(0, 4):
    possible = all_subsets(u)
    # all multisets of up to 3 sets (allow duplicates)
    for m in range(0, 4):
        for combo in itertools.combinations_with_replacement(range(len(possible)), m):
            instance = {"universe_size": u, "sets": [possible[i] for i in combo]}
            check(instance)

# ---- Random larger instances ------------------------------------------
rng = random.Random(12345)
for _ in range(3000):
    u = rng.randint(0, 7)
    m = rng.randint(0, 8)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u)
        sets.append(sorted(rng.sample(range(u), size)))
    check({"universe_size": u, "sets": sets})

# ---- Specific edge cases ----------------------------------------------
check({"universe_size": 0, "sets": []})
check({"universe_size": 0, "sets": [[], []]})
check({"universe_size": 3, "sets": []})
check({"universe_size": 3, "sets": [[0, 1, 2], [0, 1, 2]]})
check({"universe_size": 3, "sets": [[0, 1, 2]]})
check({"universe_size": 3, "sets": [[0], [1], [2]]})
check({"universe_size": 3, "sets": [[0], [0, 1], [1, 2], [2]]})
check({"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 1, 2, 3], []]})

# ---- Large-ish instance: reduction stays polynomial and correct --------
big_u = 12
big_sets = [[i] for i in range(big_u)]
check({"universe_size": big_u, "sets": big_sets})
big_sets2 = [[i, (i + 1) % big_u] for i in range(big_u)]
check({"universe_size": big_u, "sets": big_sets2})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
