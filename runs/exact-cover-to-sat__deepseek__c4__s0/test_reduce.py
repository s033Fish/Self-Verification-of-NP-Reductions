"""Tests comparing brute-force solvers on small Exact Cover instances and
their reductions to SAT."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from solvers import solve_exact_cover, solve_sat
from problems import ExactCover, Sat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    a = solve_exact_cover(instance)
    b = solve_sat(reduced)
    assert a == b, (instance, reduced, a, b)
    tests_passed += 1


def all_small_instances():
    # Exhaustive: universe sizes 0..3, all subsets of the universe as a
    # multiset of up to 3 sets (with repetition).
    for u in range(4):
        subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                subsets.append(list(combo))
        for n in range(4):
            for chosen in itertools.product(subsets, repeat=n):
                yield {"universe_size": u, "sets": [list(s) for s in chosen]}


def main():
    # Exhaustive small cases.
    for inst in all_small_instances():
        check(inst)

    # Explicit edge cases.
    check({"universe_size": 0, "sets": []})
    check({"universe_size": 0, "sets": [[], [], []]})
    check({"universe_size": 3, "sets": []})
    check({"universe_size": 3, "sets": [[], []]})
    check({"universe_size": 3, "sets": [[0, 1, 2]]})
    check({"universe_size": 3, "sets": [[0, 1], [2]]})
    check({"universe_size": 3, "sets": [[0, 1], [1, 2]]})
    check({"universe_size": 3, "sets": [[0, 1], [0, 1], [2]]})
    check({"universe_size": 2, "sets": [[0], [0], [1]]})
    check({"universe_size": 2, "sets": [[0], [0]]})

    # Random larger cases.
    rng = random.Random(12345)
    for _ in range(3000):
        u = rng.randint(0, 6)
        n = rng.randint(0, 7)
        sets = []
        for _ in range(n):
            r = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), r)) if u else [])
        check({"universe_size": u, "sets": sets})

    # Random cases biased toward duplicates and empty sets.
    for _ in range(2000):
        u = rng.randint(0, 5)
        pool = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                pool.append(list(combo))
        if not pool:
            pool = [[]]
        n = rng.randint(0, 8)
        sets = [list(rng.choice(pool)) for _ in range(n)]
        check({"universe_size": u, "sets": sets})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
