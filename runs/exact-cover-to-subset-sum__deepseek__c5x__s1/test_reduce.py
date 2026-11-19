"""Test the reduction from ExactCover to SubsetSum.

The repository provides only validation code for the two problems and a
reduction implementation.  To verify the reduction we implement brute‑force
solvers for both problems and compare the answers on a collection of random
small instances.

The script generates a number of random instances (including edge cases),
validates them using the problem classes, reduces them with ``reduce.reduce``
and checks that the answers of the two solvers agree.  It finally writes a
``verdict.json`` file containing the number of tests run, how many passed and
whether the reduction was verified.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

# Import the problem definitions and the reduction implementation.
import problems
import reduce as reduction_module


def exact_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the ExactCover instance has an exact cover.

    The universe is ``0..u-1`` and ``instance["sets"]`` is a list of subsets.
    We simply try every subset of the collection of sets (by index) and check
    the covering condition.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    n_sets = len(sets)

    # Pre‑compute each set as a Python ``set`` for fast operations.
    set_objs = [set(s) for s in sets]

    # Edge case: empty universe is always solvable (choose nothing).
    if u == 0:
        return True

    # Enumerate all possible selections of sets.
    for r in range(1, n_sets + 1):
        for combo in combinations(range(n_sets), r):
            union = set()
            disjoint = True
            for idx in combo:
                s = set_objs[idx]
                if union & s:
                    disjoint = False
                    break
                union |= s
            if disjoint and union == set(range(u)):
                return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """Return True iff the SubsetSum instance has a sub‑list summing to target.
    """
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_universe: int = 5, max_sets: int = 6) -> dict:
    """Generate a random but valid ExactCover instance.

    The generator respects the validation rules defined in ``problems``.
    """
    u = random.randint(0, max_universe)
    m = random.randint(0, max_sets)
    sets: list[list[int]] = []
    for _ in range(m):
        # Random subset (may be empty). Ensure elements are within the universe.
        if u == 0:
            subset = []
        else:
            subset_size = random.randint(0, u)
            subset = random.sample(range(u), subset_size) if subset_size > 0 else []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def run_tests(num_random: int = 200) -> dict:
    """Execute a suite of tests and return a result dictionary.
    """
    tests_run = 0
    tests_passed = 0

    # Include some deterministic edge‑case instances.
    edge_cases = [
        {"universe_size": 0, "sets": []},  # empty universe
        {"universe_size": 0, "sets": [[]]},  # empty set but universe empty
        {"universe_size": 1, "sets": [[]]},  # cannot cover element 0
        {"universe_size": 1, "sets": [[0]]},  # trivially cover
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},  # overlapping sets
    ]

    for instance in edge_cases:
        problems.ExactCover.validate(instance)
        reduced = reduction_module.reduce(instance)
        problems.SubsetSum.validate(reduced)
        ec = exact_cover_bruteforce(instance)
        ss = subset_sum_bruteforce(reduced)
        tests_run += 1
        if ec == ss:
            tests_passed += 1
        else:
            print("Mismatch on edge case", instance, file=sys.stderr)

    # Random instances
    for _ in range(num_random):
        inst = random_exact_cover_instance()
        problems.ExactCover.validate(inst)
        reduced = reduction_module.reduce(inst)
        problems.SubsetSum.validate(reduced)
        ec = exact_cover_bruteforce(inst)
        ss = subset_sum_bruteforce(reduced)
        tests_run += 1
        if ec == ss:
            tests_passed += 1
        else:
            print("Mismatch on random instance", inst, file=sys.stderr)

    verified = tests_run == tests_passed
    return {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}


if __name__ == "__main__":
    result = run_tests()
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
