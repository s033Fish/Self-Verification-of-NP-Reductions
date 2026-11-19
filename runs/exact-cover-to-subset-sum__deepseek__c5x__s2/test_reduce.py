"""Test suite for the ExactCover → SubsetSum reduction.

The repository provides only validation functions for the two problems and a
``reduce`` implementation.  To verify the reduction we implement brute‑force
solvers for both problems, generate many small random instances, reduce them
with ``reduce.reduce`` and compare the answers.

The script writes a ``verdict.json`` file containing:

* ``verified`` – ``true`` iff every test case agrees.
* ``tests_run`` – total number of generated instances.
* ``tests_passed`` – number of instances where the reduction preserved the
  answer.

The script is intended to be executed directly (``python test_reduce.py``).
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import List, Dict, Any

from problems import ExactCover, SubsetSum
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Exact Cover instance has an exact cover.

    The brute‑force algorithm enumerates all subsets of the given sets and
    checks the covering condition.  This is exponential but sufficient for
    the tiny instances used in the tests.
    """
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)

    # Edge case: empty universe is always a yes instance.
    if u == 0:
        return True

    # Pre‑compute each set as a bitmask for fast union/count operations.
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    full_mask = (1 << u) - 1

    # Enumerate all subsets of indices.
    for r in range(1, m + 1):
        for combo in combinations(range(m), r):
            union = 0
            overlap = False
            for idx in combo:
                if union & masks[idx]:
                    overlap = True
                    break
                union |= masks[idx]
            if not overlap and union == full_mask:
                return True
    return False


def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff a sub‑list of numbers sums to the target.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    n = len(numbers)
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_exact_cover_instance(max_u: int = 5, max_m: int = 5) -> Dict[str, Any]:
    """Generate a random small ExactCover instance.

    The universe size ``u`` is chosen uniformly from ``0..max_u``.  For each of
    ``m`` sets (``m`` chosen uniformly from ``0..max_m``) we randomly decide
    whether each element belongs to the set.
    """
    u = random.randint(0, max_u)
    m = random.randint(0, max_m)
    sets: List[List[int]] = []
    for _ in range(m):
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0

    # Run a mixture of random instances and explicit edge cases.
    test_instances: List[Dict[str, Any]] = []
    # Randomly generated instances.
    for _ in range(200):
        test_instances.append(random_exact_cover_instance())
    # Explicit edge cases.
    test_instances.extend([
        {"universe_size": 0, "sets": []},  # empty universe
        {"universe_size": 3, "sets": []},  # no sets, non‑empty universe
        {"universe_size": 2, "sets": [[], []]},  # only empty sets
    ])

    for instance in test_instances:
        # Ensure the instance conforms to the validation schema.
        try:
            ExactCover.validate(instance)
        except Exception:
            # Skip malformed instances – they are not part of the specification.
            continue
        total += 1
        ec_answer = exact_cover_bruteforce(instance)
        # Reduce and validate the target instance.
        reduced = reduce_instance(instance)
        SubsetSum.validate(reduced)
        ss_answer = subset_sum_bruteforce(reduced)
        if ec_answer == ss_answer:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("ExactCover instance:", instance, file=sys.stderr)
            print("Reduced SubsetSum instance:", reduced, file=sys.stderr)
            print("ExactCover answer:", ec_answer, file=sys.stderr)
            print("SubsetSum answer:", ss_answer, file=sys.stderr)
            break

    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

