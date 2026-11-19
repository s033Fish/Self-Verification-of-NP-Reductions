"""Tests for reduce.py: compare brute-force answers on many small ExactCover
instances with the answers on their SubsetSum reductions.

Ground truth comes from solvers.py (exhaustive search written directly from the
definitions in problems.py).  reduce.py is not modified.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import Any, Dict, Iterable, List, Tuple

from problems import ExactCover, SubsetSum
from reduce import reduce
from solvers import exact_cover_yes, subset_sum_yes


def all_subsets_of_universe(u: int) -> List[List[int]]:
    elems = list(range(u))
    out: List[List[int]] = []
    for r in range(u + 1):
        for combo in itertools.combinations(elems, r):
            out.append(list(combo))
    return out


def generate_instances(max_u: int = 3, max_sets: int = 4) -> Iterable[Dict[str, Any]]:
    """Yield a broad family of small ExactCover instances."""
    for u in range(0, max_u + 1):
        possible = all_subsets_of_universe(u)
        # Every possible list of sets up to max_sets, including repeats and
        # empty sets.  This is small for the chosen bounds.
        for m in range(0, max_sets + 1):
            for sets in itertools.product(possible, repeat=m):
                yield {"universe_size": u, "sets": [list(s) for s in sets]}


def check_instance(instance: Dict[str, Any]) -> Tuple[bool, str]:
    """Return (passed, message) for one source instance."""
    ExactCover.validate(instance)
    expected = exact_cover_yes(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    got = subset_sum_yes(reduced)
    if expected != got:
        return False, (
            f"MISMATCH source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
    return True, ""


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures: List[str] = []

    for instance in generate_instances():
        tests_run += 1
        ok, message = check_instance(instance)
        if ok:
            tests_passed += 1
        elif len(failures) < 20:
            failures.append(message)

    # A few hand-picked edge cases, including the known carry counterexample.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[], [0]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0], [0], [0], [0]]},
        {"universe_size": 3, "sets": [[0], [0], [0], [0], [1], [2]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        ok, message = check_instance(instance)
        if ok:
            tests_passed += 1
        elif len(failures) < 20:
            failures.append(message)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for message in failures:
        print(message)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
