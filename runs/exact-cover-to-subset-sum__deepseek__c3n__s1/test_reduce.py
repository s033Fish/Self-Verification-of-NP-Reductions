"""Tests for the Exact Cover -> Subset Sum reduction.

Contains independent brute-force solvers for both problems (written from the
docstrings in problems.py) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)


def solve_exact_cover(instance: dict) -> bool:
    """True iff some sub-collection of sets is an exact cover."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    target = (1 << u) - 1  # bitmask of all universe elements
    for mask in range(1 << m):
        covered = 0
        ok = True
        for i in range(m):
            if mask >> i & 1:
                bits = 0
                for e in sets[i]:
                    bits |= 1 << e
                if covered & bits:  # overlap -> not disjoint
                    ok = False
                    break
                covered |= bits
        if ok and covered == target:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """True iff some sub-list of numbers sums to target."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in instance["numbers"]:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Helpers


def random_ec_instance(rng: random.Random, max_u: int = 5, max_sets: int = 6) -> dict:
    u = rng.randint(0, max_u)
    m = rng.randint(0, max_sets)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u) if u > 0 else 0
        elems = rng.sample(range(u), size) if u > 0 else []
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


def check(instance: dict) -> bool:
    """Validate, reduce, validate the result, and compare answers."""
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = solve_exact_cover(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (
        f"mismatch on {instance!r}: exact_cover={expected}, "
        f"subset_sum={got}, reduced={reduced!r}"
    )
    return True


# ----------------------------------------------------------------------
# Tests


def test_hand_cases():
    cases = [
        # u = 0 is yes (empty sub-list).
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        # simple yes
        {"universe_size": 1, "sets": [[0]]},
        # simple no
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        # overlapping sets only -> no
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        # exact cover exists
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2], [0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        # duplicate copies of a non-empty set cannot both be chosen
        {"universe_size": 2, "sets": [[0], [0], [1]]},
        # empty sets never matter
        {"universe_size": 2, "sets": [[], [0], [], [1], []]},
        # uncovered element -> no
        {"universe_size": 3, "sets": [[0], [1]]},
        # need two sets, each covers part
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 3]]},
        # classic exact cover
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [0, 3], [0, 1, 2, 3]]},
    ]
    for c in cases:
        check(c)


def test_exhaustive_small():
    """Exhaustively test all instances with u <= 2 and up to 3 sets."""
    count = 0
    for u in range(3):
        universe = list(range(u))
        # all possible subsets of the universe
        all_subsets = []
        for r in range(u + 1):
            all_subsets.extend(itertools.combinations(universe, r))
        all_subsets = [list(s) for s in all_subsets]
        for m in range(4):
            for combo in itertools.product(all_subsets, repeat=m):
                check({"universe_size": u, "sets": list(combo)})
                count += 1
    print(f"exhaustive small: {count} instances checked")


def test_exhaustive_u3():
    """Exhaustively test u = 3 with up to 2 sets (all subsets of {0,1,2})."""
    count = 0
    universe = [0, 1, 2]
    all_subsets = []
    for r in range(4):
        all_subsets.extend(itertools.combinations(universe, r))
    all_subsets = [list(s) for s in all_subsets]
    for m in range(3):
        for combo in itertools.product(all_subsets, repeat=m):
            check({"universe_size": 3, "sets": list(combo)})
            count += 1
    print(f"exhaustive u=3: {count} instances checked")


def test_random_many():
    rng = random.Random(12345)
    n = 4000
    for _ in range(n):
        check(random_ec_instance(rng, max_u=6, max_sets=8))
    print(f"random: {n} instances checked")


def test_duplicates_and_empties():
    rng = random.Random(999)
    for _ in range(1000):
        u = rng.randint(0, 5)
        m = rng.randint(0, 7)
        sets = []
        for _ in range(m):
            if u == 0:
                sets.append([])
            else:
                size = rng.randint(0, u)
                sets.append(rng.sample(range(u), size))
        # force duplicates / empties often
        if sets:
            sets.append(list(sets[rng.randrange(len(sets))]))
        if rng.random() < 0.5:
            sets.append([])
        check({"universe_size": u, "sets": sets})
    print("duplicates/empties: 1000 instances checked")


def test_large_polynomial_behavior():
    """A larger instance: reduction must run fast and be structurally sound.

    We do NOT brute-force subset sum here (the encoded values are enormous);
    instead we verify the reduction's key invariant directly: the encoded
    numbers of a known exact cover sum to the target, and no digit exceeds m.
    """
    import time

    u = 200
    sets = []
    # a guaranteed exact cover: singletons
    sets.extend([[e] for e in range(u)])
    # plus lots of noise sets
    rng = random.Random(7)
    for _ in range(300):
        size = rng.randint(0, u)
        sets.append(rng.sample(range(u), size))
    instance = {"universe_size": u, "sets": sets}
    ExactCover.validate(instance)
    start = time.time()
    reduced = reduce(instance)
    elapsed = time.time() - start
    SubsetSum.validate(reduced)
    assert elapsed < 5.0

    # The singletons are positions 0..u-1 and form an exact cover.
    assert sum(reduced["numbers"][:u]) == reduced["target"]

    # Cross-check the encoding against an independent big-int computation.
    m = len(sets)
    base = m + 1
    for s, a in zip(sets, reduced["numbers"]):
        assert a == sum(base ** e for e in s)
    assert reduced["target"] == sum(base ** e for e in range(u))

    print(f"large instance reduced in {elapsed:.4f}s")


def test_no_carry_false_positives():
    """Carry-free encoding: no non-exact-cover sub-collection can hit target."""
    # base = m+1 > m, so digit sums never carry. Verify on tricky instances.
    tricky = [
        # many duplicate singletons: only one copy of each can be used
        {"universe_size": 2, "sets": [[0], [0], [0], [1], [1]]},
        # big overlapping sets
        {"universe_size": 3, "sets": [[0, 1, 2], [0, 1, 2], [0, 1, 2]]},
        # cover requires combining several small sets
        {"universe_size": 5, "sets": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4], [0, 1, 2, 3, 4]]},
        # no cover: element 3 unreachable
        {"universe_size": 4, "sets": [[0], [1], [2], [0, 1, 2]]},
        # base = 1 case (m = 0) with nonempty universe -> no
        {"universe_size": 3, "sets": []},
    ]
    for c in tricky:
        check(c)


def test_many_sets_small_universe():
    """Larger m stresses the base choice (b = m + 1)."""
    rng = random.Random(2024)
    for _ in range(500):
        u = rng.randint(0, 4)
        m = rng.randint(0, 12)
        sets = []
        for _ in range(m):
            if u == 0:
                sets.append([])
            else:
                size = rng.randint(0, u)
                sets.append(rng.sample(range(u), size))
        check({"universe_size": u, "sets": sets})
    print("many-sets: 500 instances checked")


def main():
    tests = [
        test_hand_cases,
        test_exhaustive_small,
        test_exhaustive_u3,
        test_random_many,
        test_duplicates_and_empties,
        test_large_polynomial_behavior,
        test_no_carry_false_positives,
        test_many_sets_small_universe,
    ]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"PASS {t.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed")
    return passed, len(tests)


if __name__ == "__main__":
    p, n = main()
    assert p == n
