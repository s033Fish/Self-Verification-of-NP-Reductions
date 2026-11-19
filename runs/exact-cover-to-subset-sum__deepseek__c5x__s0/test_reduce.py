"""Test suite for the ExactCover → SubsetSum reduction.

The repository provides only validation functions for the two problems.
We implement straightforward brute‑force solvers for both problems and
compare the answer of a random ExactCover instance with the answer of its
reduction produced by ``reduce.py``.

If all generated instances agree, the reduction is considered verified.
The script prints a short summary and writes ``verdict.json`` in the
working directory.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – validates that the module loads correctly
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the ExactCover instance is a yes‑instance.

    The universe is ``0..u-1`` and ``instance["sets"]`` is a list of sets
    (each represented as a list of distinct integers).  We try every
    subset of the given sets and check whether the chosen sets are pairwise
    disjoint and their union equals the whole universe.
    """
    u: int = instance["universe_size"]
    sets: list[list[int]] = instance["sets"]
    m = len(sets)

    # Pre‑compute each set as a bitmask for fast union / disjoint checks.
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    full_mask = (1 << u) - 1

    # Enumerate all subsets of the index set {0,…,m‑1}.
    for r in range(m + 1):
        for combo in combinations(range(m), r):
            union = 0
            ok = True
            for idx in combo:
                if union & masks[idx]:
                    ok = False  # overlap → not disjoint
                    break
                union |= masks[idx]
            if ok and union == full_mask:
                return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """Return True iff the SubsetSum instance is a yes‑instance.

    ``instance["numbers"]`` is a list of non‑negative integers and
    ``instance["target"]`` is an integer (may be negative).  We test all
    subsets of the numbers.
    """
    numbers: list[int] = instance["numbers"]
    target: int = instance["target"]
    # Quick edge cases matching the problem statement.
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    # Enumerate subsets via bitmask.
    for mask in range(1, 1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
                if s > target:
                    # early break – all numbers are non‑negative
                    break
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_u: int = 5, max_m: int = 5) -> dict:
    """Generate a random ExactCover instance.

    ``max_u`` and ``max_m`` bound the universe size and the number of sets.
    Elements are chosen uniformly at random; sets may be empty and may be
    duplicated – this matches the definition.
    """
    u = random.randint(0, max_u)
    m = random.randint(0, max_m)
    sets = []
    for _ in range(m):
        # Random subset of the universe (including empty)
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    for _ in range(200):  # a modest number of random tests
        ec_instance = random_exact_cover_instance()
        # Validate the instance using the provided validator (will raise on error)
        problems.ExactCover.validate(ec_instance)
        ec_answer = exact_cover_bruteforce(ec_instance)
        ss_instance = reduce_instance(ec_instance)
        # The reduction should produce a valid SubsetSum instance.
        problems.SubsetSum.validate(ss_instance)
        ss_answer = subset_sum_bruteforce(ss_instance)
        total += 1
        if ec_answer == ss_answer:
            passed += 1
        else:
            # Print a failing example for debugging.
            print("Mismatch!", file=sys.stderr)
            print("ExactCover instance:", ec_instance, file=sys.stderr)
            print("ExactCover answer:", ec_answer, file=sys.stderr)
            print("Reduced SubsetSum instance:", ss_instance, file=sys.stderr)
            print("SubsetSum answer:", ss_answer, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
