"""Tests comparing brute-force Exact Cover answers with SAT answers on reductions."""

from __future__ import annotations

import random

from problems import ExactCover, Sat
from reduce import reduce
from solvers import solve_exact_cover, solve_sat

tests_run = 0
tests_passed = 0


def check(instance: dict, label: str = "") -> None:
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    src = solve_exact_cover(instance)
    tgt = solve_sat(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        raise AssertionError(
            f"MISMATCH {label}: source={src} target={tgt}\n"
            f"instance={instance}\nreduced={reduced}"
        )


# ---- hand-written edge cases ----
check({"universe_size": 0, "sets": []}, "u=0 no sets")
check({"universe_size": 0, "sets": [[], []]}, "u=0 empty sets")
check({"universe_size": 1, "sets": []}, "element uncovered")
check({"universe_size": 1, "sets": [[]]}, "only empty set")
check({"universe_size": 1, "sets": [[0]]}, "single set")
check({"universe_size": 2, "sets": [[0], [1]]}, "two singletons")
check({"universe_size": 2, "sets": [[0, 1]]}, "one pair")
check({"universe_size": 2, "sets": [[0, 1], [0], [1]]}, "redundant sets")
check({"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]}, "odd cycle no cover")
check({"universe_size": 4, "sets": [[0, 1], [2, 3], [1, 2], [0, 3]]}, "two covers")
check({"universe_size": 2, "sets": [[0], [0]]}, "duplicate singleton")
check({"universe_size": 2, "sets": [[0, 1], [0, 1]]}, "duplicate pair")
check({"universe_size": 3, "sets": [[0, 1, 2], [0], [1], [2]]}, "big plus singles")
check({"universe_size": 3, "sets": [[], [0], [1], [2]]}, "empty plus singles")
check({"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [0, 3]]}, "cycle cover")
check({"universe_size": 5, "sets": [[0], [1], [2], [3], [4], [0, 1, 2, 3, 4]]}, "singles")

# ---- randomized tests ----
rng = random.Random(12345)
for trial in range(3000):
    u = rng.randint(0, 5)
    n = rng.randint(0, 7)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u) if u > 0 else 0
        elems = rng.sample(range(u), size)
        sets.append(elems)
    check({"universe_size": u, "sets": sets}, f"random {trial}")

# a few larger random ones (still brute-forceable)
for trial in range(200):
    u = rng.randint(4, 7)
    n = rng.randint(3, 9)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u)
        sets.append(rng.sample(range(u), size))
    check({"universe_size": u, "sets": sets}, f"larger {trial}")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
