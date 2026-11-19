"""Test suite for the ExactCover → SubsetSum reduction.

The purpose of this file is to automatically verify that ``reduce.py``
produces a SubsetSum instance whose answer matches the answer of the
original ExactCover instance.  The test generates a number of small random
instances, solves both problems by exhaustive search, and compares the
results.

If all generated instances agree, we consider the reduction verified.
The script prints a JSON object suitable for ``verdict.json``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

from problems import ExactCover, SubsetSum
from reduce import reduce as reduction


def exact_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the ExactCover instance has an exact cover.

    The universe size is at most a few elements in the generated tests, so a
    simple exponential search over all subsets of the given sets is fine.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    universe = set(range(u))

    for r in range(len(sets) + 1):
        for combo in combinations(range(len(sets)), r):
            used = set()
            ok = True
            for idx in combo:
                s = set(sets[idx])
                if used & s:
                    ok = False
                    break
                used |= s
            if ok and used == universe:
                return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """Return True iff a subset of numbers sums to the target.
    """
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for r in range(n + 1):
        for combo in combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def random_exact_cover_instance(max_u: int = 4, max_sets: int = 5) -> dict:
    """Generate a random ExactCover instance within small bounds.

    Elements are 0..u-1. Each set is a random subset (possibly empty). Duplicate
    sets are allowed because the original problem permits them.
    """
    u = random.randint(0, max_u)
    num_sets = random.randint(0, max_sets)
    sets = []
    for _ in range(num_sets):
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)
    total = 200
    passed = 0
    for _ in range(total):
        src = random_exact_cover_instance()
        ExactCover.validate(src)
        ans_src = exact_cover_bruteforce(src)
        tgt = reduction(src)
        SubsetSum.validate(tgt)
        ans_tgt = subset_sum_bruteforce(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            sys.stderr.write("Mismatch found!\nSource: %s\nReduced: %s\n" % (src, tgt))
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
