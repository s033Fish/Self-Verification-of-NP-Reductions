"""Automated tests for the ExactCover → SubsetSum reduction.

The repository provides only validation functions for the two problems and
the ``reduce`` implementation.  To verify that the reduction is correct we
implement straightforward brute‑force solvers for both problems and compare
their answers on a large number of randomly generated small instances.

If every test agrees we write ``verdict.json`` indicating that the reduction
has been verified.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict, Any

from problems import ExactCover, SubsetSum
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Exact Cover instance has an exact cover.

    The universe is ``0..u-1`` and ``instance["sets"]`` is a list of sets
    (each represented as a list of distinct integers).  We simply try every
    subset of the given sets.
    """
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    set_objs = [frozenset(s) for s in sets]
    if u == 0:
        return True
    universe = set(range(u))
    n = len(set_objs)
    for mask in range(1 << n):
        covered: set[int] = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = set_objs[i]
                if covered & s:
                    ok = False
                    break
                covered |= s
        if ok and covered == universe:
            return True
    return False


def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff some sub‑list of ``numbers`` sums to ``target``.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_u: int = 5, max_sets: int = 6) -> Dict[str, Any]:
    """Generate a random ExactCover instance with small parameters.

    ``max_u`` and ``max_sets`` bound the size of the generated instance.
    """
    u = random.randint(0, max_u)
    num_sets = random.randint(0, max_sets)
    sets: List[List[int]] = []
    for _ in range(num_sets):
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)
    total = 200
    passed = 0
    for _ in range(total):
        src = random_exact_cover_instance()
        ExactCover.validate(src)
        expected = exact_cover_bruteforce(src)
        reduced = reduce_instance(src)
        SubsetSum.validate(reduced)
        got = subset_sum_bruteforce(reduced)
        if expected == got:
            passed += 1
        else:
            print("FAILURE", file=sys.stderr)
            print("source", src, file=sys.stderr)
            print("reduced", reduced, file=sys.stderr)
            print("expected", expected, "got", got, file=sys.stderr)
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
