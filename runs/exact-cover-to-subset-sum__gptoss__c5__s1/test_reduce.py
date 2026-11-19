"""Tests for the reduction from ExactCover to SubsetSum.

The task requires us to verify that the provided ``reduce`` function produces a
Subset‑Sum instance that has the same yes/no answer as the original Exact‑Cover
instance.  Since the repository does not contain solvers, we implement simple
brute‑force solvers for both problems and compare their results on a collection
of small, randomly generated instances.

The test script records how many instances were generated and how many passed
the equivalence check.  It writes a ``verdict.json`` file in the repository root
containing the required fields:

``{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}``

The script is intended to be executed directly (e.g. ``python -m pytest`` or
simply ``python test_reduce.py``).  It does not rely on any external packages.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

from problems import ExactCover, SubsetSum
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the ExactCover instance is a yes‑instance.

    Brute‑force checks every subset of the given sets.
    """
    ExactCover.validate(instance)
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)
    # Iterate over all masks of length m.
    for mask in range(1 << m):
        used = set()
        ok = True
        for i in range(m):
            if mask >> i & 1:
                for elem in sets[i]:
                    if elem in used:
                        ok = False
                        break
                    used.add(elem)
                if not ok:
                    break
        if ok and len(used) == u:
            return True
    # Edge case: empty universe is always yes (handled by mask=0 when u==0).
    return u == 0


def subset_sum_bruteforce(instance: Dict) -> bool:
    """Return True iff the SubsetSum instance is a yes‑instance.

    Brute‑force checks every subset of the numbers.
    """
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    # Quick edge handling per specification.
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def generate_random_instance(max_u: int = 4, max_sets: int = 4) -> Dict:
    """Generate a random ExactCover instance with small parameters.

    ``max_u`` bounds the universe size, ``max_sets`` bounds the number of sets.
    Sets are chosen uniformly from all subsets of the universe (including the
    empty set) and duplicates are allowed, matching the problem definition.
    """
    u = random.randint(0, max_u)
    num_sets = random.randint(0, max_sets)
    sets: List[List[int]] = []
    for _ in range(num_sets):
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    # Generate a mix of random instances and exhaustive small ones.
    # Exhaustive enumeration for very tiny universes (u<=2, up to 3 sets).
    for u in range(0, 3):
        all_subsets = list(product([0, 1], repeat=u))
        universe_subsets = []
        for bits in all_subsets:
            subset = [i for i, b in enumerate(bits) if b]
            universe_subsets.append(subset)
        for num_sets in range(0, 4):
            for sets_choice in product(universe_subsets, repeat=num_sets):
                instance = {"universe_size": u, "sets": list(sets_choice)}
                total += 1
                ec_ans = exact_cover_bruteforce(instance)
                reduced = reduce_instance(instance)
                ss_ans = subset_sum_bruteforce(reduced)
                if ec_ans == ss_ans:
                    passed += 1
                else:
                    print("Mismatch!", instance, reduced, ec_ans, ss_ans, file=sys.stderr)
    # Additional random tests.
    for _ in range(200):
        instance = generate_random_instance()
        total += 1
        ec_ans = exact_cover_bruteforce(instance)
        reduced = reduce_instance(instance)
        ss_ans = subset_sum_bruteforce(reduced)
        if ec_ans == ss_ans:
            passed += 1
        else:
            print("Random mismatch!", instance, reduced, ec_ans, ss_ans, file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
