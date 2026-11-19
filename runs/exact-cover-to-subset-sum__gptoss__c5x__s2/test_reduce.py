"""Independent tests for reduce.py (Exact Cover -> Subset Sum).

We implement our own brute-force solvers from the problem definitions and
compare answers on many small source instances and their reductions.

Two solvers are provided for each problem:
  * a simple 2^m / 2^n brute force (ground truth for small instances),
  * a backtracking Exact Cover solver and a meet-in-the-middle Subset Sum
    solver (ground truth for moderately larger instances).
"""

from __future__ import annotations

import itertools
import random
import sys
import time

from problems import ExactCover, SubsetSum
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (from the documented definitions)

def exact_cover_bruteforce(instance) -> bool:
    """Yes iff some sub-collection of the sets is pairwise disjoint and
    covers the whole universe 0..u-1 exactly once."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    for mask in range(1 << m):
        covered = set()
        ok = True
        for i in range(m):
            if mask & (1 << i):
                s = sets[i]
                if covered & set(s):
                    ok = False
                    break
                covered |= set(s)
        if ok and len(covered) == u:
            return True
    return False


def subset_sum_bruteforce(instance) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if mask & (1 << i):
                total += numbers[i]
        if total == target:
            return True
    return False


# ----------------------------------------------------------------------
# Independent, larger-scale solvers

def exact_cover_backtrack(instance) -> bool:
    """Backtracking exact cover over the universe."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    if u == 0:
        return True
    # element -> list of set indices containing it
    by_elem = [[] for _ in range(u)]
    for i, s in enumerate(sets):
        for e in s:
            by_elem[e].append(i)
    # pick the uncovered element with fewest options
    def rec(covered: int, used: frozenset) -> bool:
        if covered == (1 << u) - 1:
            return True
        # find uncovered element with fewest candidate sets
        best = -1
        best_opts = None
        for e in range(u):
            if not (covered >> e) & 1:
                opts = [i for i in by_elem[e] if i not in used]
                if best_opts is None or len(opts) < len(best_opts):
                    best, best_opts = e, opts
                    if not opts:
                        return False
        for i in best_opts:
            s = sets[i]
            if s & set_of_bits(covered):
                continue
            if rec(covered | bits_of(s), used | {i}):
                return True
        return False

    def bits_of(s):
        b = 0
        for e in s:
            b |= 1 << e
        return b

    def set_of_bits(b):
        return {e for e in range(u) if (b >> e) & 1}

    return rec(0, frozenset())


def subset_sum_mitm(instance) -> bool:
    """Meet-in-the-middle subset sum (exact, handles larger n)."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    half = n // 2
    left, right = numbers[:half], numbers[half:]

    def sums(arr):
        out = [0]
        for a in arr:
            out += [x + a for x in out]
        return set(out)

    ls = sums(left)
    rs = sums(right)
    for x in ls:
        if target - x in rs:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def all_subsets(u):
    elems = list(range(u))
    out = []
    for r in range(u + 1):
        for combo in itertools.combinations(elems, r):
            out.append(list(combo))
    return out


def exhaustive_small(max_u=3, max_m=3):
    instances = []
    for u in range(0, max_u + 1):
        subs = all_subsets(u)
        for m in range(0, max_m + 1):
            for combo in itertools.product(subs, repeat=m):
                instances.append({"universe_size": u, "sets": [list(s) for s in combo]})
    return instances


def random_instances(count, seed=12345, max_u=6, max_m=8):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        u = rng.randint(0, max_u)
        m = rng.randint(0, max_m)
        subs = all_subsets(u)
        sets = [list(rng.choice(subs)) for _ in range(m)]
        out.append({"universe_size": u, "sets": sets})
    return out


# ----------------------------------------------------------------------
# Tests

def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, solver=exact_cover_bruteforce, ssolver=subset_sum_bruteforce):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solver(inst)
        reduced = reduce_mod.reduce(inst)
        try:
            SubsetSum.validate(reduced)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "invalid reduction output", repr(exc)))
            return
        got = ssolver(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, reduced, got))

    # Exhaustive small instances (u<=3, m<=3)
    for inst in exhaustive_small(3, 3):
        check(inst)

    # Exhaustive u=4 with up to 4 sets
    for inst in exhaustive_small(4, 4):
        check(inst)

    # Random instances, simple brute force
    for inst in random_instances(4000):
        check(inst)

    # Random larger instances with independent stronger solvers
    rng = random.Random(999)
    for _ in range(300):
        u = rng.randint(0, 10)
        m = rng.randint(0, 16)
        subs = all_subsets(u)
        sets = [list(rng.choice(subs)) for _ in range(m)]
        inst = {"universe_size": u, "sets": sets}
        check(inst, exact_cover_backtrack, subset_sum_mitm)

    # Explicit edge cases
    edge = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[]]},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 1, "sets": [[], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 2, "sets": [[0, 1], [0]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        # element not covered by any set
        {"universe_size": 3, "sets": [[0, 1]]},
        # many duplicate sets
        {"universe_size": 2, "sets": [[0, 1]] * 5},
        # large base stress: 30 copies of a set
        {"universe_size": 3, "sets": [[0, 1, 2]] * 30},
    ]
    for inst in edge:
        check(inst)

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    t0 = time.time()
    tests_run, tests_passed, failures = run_tests()
    elapsed = time.time() - t0
    print(f"tests_run={tests_run} tests_passed={tests_passed} elapsed={elapsed:.2f}s")
    if failures:
        print("FAILURES (first 20):")
        for f in failures[:20]:
            print("  ", f)
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
