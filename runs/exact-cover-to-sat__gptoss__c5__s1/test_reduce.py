"""Automated tests for the ExactCover → SAT reduction.

The repository provides only the problem definitions and a ``reduce`` function.
This test suite implements brute‑force solvers for both Exact Cover and SAT
according to the specifications in ``problems.py`` and checks that for a large
number of randomly generated small instances the answer of the reduced SAT
instance matches the answer of the original Exact Cover instance.

The script is deliberately lightweight and has no external dependencies – it
uses only the Python standard library. It can be executed directly with
``python -m pytest -q test_reduce.py`` or simply ``python test_reduce.py``.
Running it will produce a JSON report ``verdict.json`` as required by the task.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict, Any

from problems import ExactCover, Sat
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Exact Cover instance is a YES instance.

    The implementation follows the definition verbatim: we try every subset
    of the given sets and check whether the chosen sets are pairwise disjoint
    and their union equals the whole universe.
    """
    ExactCover.validate(instance)
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n_sets = len(sets)

    # Pre‑compute the element bitmask for each set for fast union / intersection.
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    full_mask = (1 << u) - 1

    # Iterate over all subsets of sets (represented by a bitmask of chosen sets).
    for chosen in range(1 << n_sets):
        union = 0
        ok = True
        for i in range(n_sets):
            if chosen >> i & 1:
                # Check disjointness: intersection must be empty.
                if union & masks[i]:
                    ok = False
                    break
                union |= masks[i]
        if ok and union == full_mask:
            return True
    # Edge case: empty universe is always solvable (choose no sets).
    return u == 0


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Brute‑forces all assignments of the ``num_vars`` variables.
    """
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Early exit: empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses -> always satisfiable.
    if not clauses:
        return True

    for assignment in range(1 << m):
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assignment >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_exact_cover_instance(max_universe: int = 4, max_sets: int = 5) -> Dict[str, Any]:
    """Generate a random valid Exact Cover instance.

    The universe size is chosen uniformly from 0..max_universe. For each possible
    set we decide randomly whether to include it and, if so, pick a random subset
    of the universe.
    """
    u = random.randint(0, max_universe)
    sets: List[List[int]] = []
    num_sets = random.randint(0, max_sets)
    for _ in range(num_sets):
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_exact_cover_instance()
        ExactCover.validate(instance)
        ec_answer = exact_cover_bruteforce(instance)
        sat_instance = reduce_instance(instance)
        sat_answer = sat_bruteforce(sat_instance)
        total += 1
        if ec_answer == sat_answer:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("ExactCover instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced SAT instance:", json.dumps(sat_instance), file=sys.stderr)
            print("ExactCover answer:", ec_answer, file=sys.stderr)
            print("SAT answer:", sat_answer, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
