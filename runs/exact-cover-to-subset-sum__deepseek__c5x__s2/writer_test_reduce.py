"""Tests for the Exact Cover -> Subset Sum reduction in reduce.py.

Includes independent brute-force solvers for both problems, written from
the definitions in problems.py, and compares their answers on many small
source instances with the answers on their reductions.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import ExactCover, SubsetSum


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)


def exact_cover_brute(instance):
    """Return True iff the Exact Cover instance is a yes instance."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    for r in range(m + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            ok = True
            for i in combo:
                for e in sets[i]:
                    if e in covered:
                        ok = False
                        break
                    covered.add(e)
                if not ok:
                    break
            if ok and len(covered) == u:
                return True
    return False


def subset_sum_brute(instance):
    """Return True iff the Subset Sum instance is a yes instance."""
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
# Tests


def check_instance(instance):
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = exact_cover_brute(instance)
    got = subset_sum_brute(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def test_hand_picked():
    cases = [
        # u = 0: yes (empty cover), target 0.
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        # empty sets never matter
        {"universe_size": 1, "sets": [[], [0]]},
        {"universe_size": 1, "sets": [[], []]},
        # simple yes / no
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0, 1], [2]]},
        # duplicate non-empty sets cannot both be used
        {"universe_size": 2, "sets": [[0], [0], [1], [1]]},
        {"universe_size": 2, "sets": [[0], [0], [0, 1]]},
        # repeated sets, exact cover needs the union
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 1], [2, 3]]},
        # overlapping but still solvable
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]},
        # a set with all elements
        {"universe_size": 5, "sets": [[0, 1, 2, 3, 4]]},
    ]
    for case in cases:
        check_instance(case)


def test_exhaustive_small():
    """Exhaustively test all small set systems over tiny universes."""
    count = 0
    for u in range(0, 4):
        # all possible non-empty subsets of the universe (plus empty set)
        all_subsets = [[]]
        for r in range(1, u + 1):
            for combo in itertools.combinations(range(u), r):
                all_subsets.append(list(combo))
        # all lists of up to 3 sets drawn from all_subsets
        for m in range(0, 4):
            for sets in itertools.product(all_subsets, repeat=m):
                instance = {"universe_size": u, "sets": [list(s) for s in sets]}
                check_instance(instance)
                count += 1
    return count


def test_random():
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        u = rng.randint(0, 6)
        m = rng.randint(0, 7)
        sets = []
        for _ in range(m):
            size = rng.randint(0, u)
            elements = rng.sample(range(u), size)
            rng.shuffle(elements)
            sets.append(elements)
        instance = {"universe_size": u, "sets": sets}
        check_instance(instance)
        count += 1
    return count


def test_no_carries_property():
    """Directly verify that no digit column ever exceeds the base."""
    rng = random.Random(999)
    for _ in range(500):
        u = rng.randint(1, 8)
        m = rng.randint(0, 10)
        sets = []
        for _ in range(m):
            size = rng.randint(0, u)
            sets.append(rng.sample(range(u), size))
        instance = {"universe_size": u, "sets": sets}
        reduced = reduce(instance)
        base = max(2, m + 1)
        # Every number's base-B digits are 0/1 and target digits are all 1.
        for num in reduced["numbers"]:
            x = num
            while x:
                assert x % base in (0, 1), (instance, reduced)
                x //= base
        x = reduced["target"]
        while x:
            assert x % base == 1, (instance, reduced)
            x //= base


if __name__ == "__main__":
    tests = [
        ("hand_picked", test_hand_picked),
        ("exhaustive_small", test_exhaustive_small),
        ("random", test_random),
        ("no_carries_property", test_no_carries_property),
    ]
    tests_run = 0
    tests_passed = 0
    for name, fn in tests:
        tests_run += 1
        try:
            result = fn()
            tests_passed += 1
            print(f"PASS {name}" + (f" ({result} instances)" if result else ""))
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {name}: {exc!r}")
    print(f"\n{tests_passed}/{tests_run} test functions passed")
    if tests_passed != tests_run:
        raise SystemExit(1)
