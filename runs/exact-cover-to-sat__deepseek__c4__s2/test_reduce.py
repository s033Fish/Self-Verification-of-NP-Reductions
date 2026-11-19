"""Tests for reduce.py: brute-force solvers + randomized comparison."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_exact_cover(instance) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = sets[i]
                if covered & set(s):
                    ok = False
                    break
                covered |= set(s)
        if ok and covered == set(range(u)):
            return True
    return False


def solve_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assignment = {v: bool(bits & (1 << (v - 1))) for v in range(1, m + 1)}
        if all(any((lit > 0) == assignment[abs(lit)] for lit in clause)
               for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    a = solve_exact_cover(instance)
    b = solve_sat(reduced)
    if a == b:
        tests_passed += 1
    else:
        print(f"FAIL {label}: source={a} target={b}")
        print("  instance:", instance)
        print("  reduced :", reduced)
    return a == b


def main():
    # Explicit edge cases.
    check({"universe_size": 0, "sets": []}, "u=0 no sets")
    check({"universe_size": 0, "sets": [[], [], []]}, "u=0 empty sets")
    check({"universe_size": 1, "sets": []}, "no sets, nonempty universe")
    check({"universe_size": 1, "sets": [[]]}, "only empty set")
    check({"universe_size": 1, "sets": [[0]]}, "single set covers")
    check({"universe_size": 2, "sets": [[0], [1]]}, "two singletons")
    check({"universe_size": 2, "sets": [[0, 1]]}, "one pair")
    check({"universe_size": 2, "sets": [[0, 1], [0], [1]]}, "redundant")
    check({"universe_size": 3, "sets": [[0, 1], [1, 2]]}, "overlap no cover")
    check({"universe_size": 3, "sets": [[0, 1], [2]]}, "cover with overlap-free")
    check({"universe_size": 2, "sets": [[0, 1], [0, 1]]}, "duplicate pair")
    check({"universe_size": 2, "sets": [[0], [0], [1]]}, "duplicate singleton")
    check({"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]}, "many")

    # Randomized small instances.
    rng = random.Random(12345)
    for _ in range(4000):
        u = rng.randint(0, 4)
        n = rng.randint(0, 5)
        sets = []
        for _ in range(n):
            k = rng.randint(0, u)
            elems = rng.sample(range(u), k) if u else []
            sets.append(elems)
        check({"universe_size": u, "sets": sets}, "random")

    # Slightly larger universe, few sets.
    for _ in range(1500):
        u = rng.randint(0, 6)
        n = rng.randint(0, 4)
        sets = []
        for _ in range(n):
            k = rng.randint(0, u)
            elems = rng.sample(range(u), k) if u else []
            sets.append(elems)
        check({"universe_size": u, "sets": sets}, "random2")

    # Exhaustive small enumeration of all set systems over u<=3, n<=3.
    for u in range(0, 4):
        all_subsets = []
        for k in range(u + 1):
            all_subsets.extend(itertools.combinations(range(u), k))
        all_subsets = [list(c) for c in all_subsets]
        for n in range(0, 4):
            for combo in itertools.product(all_subsets, repeat=n):
                check({"universe_size": u, "sets": [list(c) for c in combo]},
                      "exhaustive")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
