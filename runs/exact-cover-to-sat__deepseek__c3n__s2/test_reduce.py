"""Tests comparing brute-force answers on small Exact Cover instances."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce
from solvers import solve_exact_cover, solve_sat

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    problems.ExactCover.validate(instance)
    expected = solve_exact_cover(instance)
    reduced = reduce(instance)
    problems.Sat.validate(reduced)
    got = solve_sat(reduced)
    assert got == expected, (instance, reduced, expected, got)
    TESTS_PASSED += 1


def all_small_instances():
    # Exhaustive over small universes and small collections of subsets.
    for u in range(0, 4):
        subsets = []
        for r in range(0, u + 1):
            subsets.extend(list(c) for c in itertools.combinations(range(u), r))
        for n in range(0, 4):
            for combo in itertools.combinations_with_replacement(subsets, n):
                yield {"universe_size": u, "sets": [list(s) for s in combo]}


def random_instances(count: int, seed: int = 12345):
    rng = random.Random(seed)
    for _ in range(count):
        u = rng.randint(0, 6)
        n = rng.randint(0, 7)
        sets = []
        for _ in range(n):
            size = rng.randint(0, u)
            sets.append(rng.sample(range(u), size))
        yield {"universe_size": u, "sets": sets}


def main() -> None:
    # 1. Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0], [1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [2, 0]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3]]},
    ]
    for inst in edge_cases:
        check(inst)

    # 2. Exhaustive small instances.
    for inst in all_small_instances():
        check(inst)

    # 3. Random larger instances.
    for inst in random_instances(400):
        check(inst)

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
