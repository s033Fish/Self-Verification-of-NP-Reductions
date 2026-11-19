"""Automated tests for the ExactCover → SAT reduction.

The repository provides only validation functions for the two problems.
This test file implements tiny brute‑force solvers for Exact Cover and SAT
and checks that for a large number of random small instances the answer of
the SAT instance produced by ``reduce`` matches the answer of the original
Exact Cover instance.

The test also validates that the produced SAT instance conforms to the
format required by :class:`Sat`.

The script is intended to be executed directly with ``python -m pytest``
or simply ``python test_reduce.py``.  It prints a JSON summary compatible
with the required ``verdict.json`` format.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from typing import List, Dict, Any

import problems  # The module containing ExactCover and Sat definitions
from reduce import reduce  # The reduction under test


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Exact Cover instance has an exact cover.

    The universe size is small in the tests, so we simply enumerate all
    subsets of the given sets.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Pre‑convert each set to a Python set for fast membership tests.
    set_list = [set(s) for s in sets]

    # Enumerate all subsets of indices 0..n‑1.
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            # Union of selected sets
            union = set()
            disjoint = True
            for idx in combo:
                s = set_list[idx]
                # Check disjointness with current union
                if union & s:
                    disjoint = False
                    break
                union |= s
            if not disjoint:
                continue
            # Check coverage of the whole universe
            if union == set(range(u)):
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Enumerates all possible truth assignments for the given number of
    variables (which is small in the generated tests).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Pre‑process clauses: each clause is a list of integers.
    for assignment in product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            # Empty clause is always unsatisfied
            if not clause:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance(max_universe: int, max_sets: int) -> Dict[str, Any]:
    """Create a random Exact Cover instance.

    The parameters bound the size of the universe and the number of sets.
    Elements inside each set are chosen uniformly at random; empty sets and
    duplicate sets are allowed because the reduction must handle them.
    """
    u = random.randint(0, max_universe)
    num_sets = random.randint(0, max_sets)
    sets: List[List[int]] = []
    for _ in range(num_sets):
        # Randomly decide the size of this set (including empty)
        size = random.randint(0, u)
        # Choose distinct elements
        elems = random.sample(range(u), k=size) if size > 0 else []
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0

    # Number of random instances to test – keep it modest to finish quickly.
    TOTAL = 200
    for _ in range(TOTAL):
        instance = generate_random_instance(max_universe=4, max_sets=5)
        # Validate the original instance according to the problem definition.
        problems.ExactCover.validate(instance)

        # Apply the reduction.
        sat_instance = reduce(instance)
        # Basic structural checks.
        assert isinstance(sat_instance, dict)
        assert set(sat_instance.keys()) == {"num_vars", "clauses"}
        # Validate the produced SAT instance.
        problems.Sat.validate(sat_instance)

        # Compute answers via brute force.
        exact = exact_cover_bruteforce(instance)
        sat = sat_bruteforce(sat_instance)

        tests_run += 1
        if exact == sat:
            tests_passed += 1
        else:
            # Print a minimal debugging output for the first failure.
            print("Mismatch found!", file=sys.stderr)
            print("ExactCover instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced SAT instance:", json.dumps(sat_instance), file=sys.stderr)
            print("ExactCover answer:", exact, "SAT answer:", sat, file=sys.stderr)
            break

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    # Write verdict.json as required by the task description.
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print to stdout for visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

