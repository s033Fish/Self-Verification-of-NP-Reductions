"""Tests for the reduction from ThreeSat to ExactCover.

The test suite implements brute‑force solvers for both problems based on the
formal definitions in ``problems.py``.  It then enumerates a collection of
small, valid ThreeSat instances, applies ``reduce`` and checks that the answer
to the ExactCover instance matches the answer to the original ThreeSat
instance.

The number of generated instances is modest so that the test suite finishes
quickly even without any optimisation.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

# Import the problem definitions and the reduction implementation.
from problems import ThreeSat, ExactCover
from reduce import reduce as reduce_instance


def three_sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance is assumed to be valid (i.e., ``ThreeSat.validate`` would not
    raise).  We simply try all possible Boolean assignments.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    # Iterate over all 2**num_vars assignments.
    for mask in range(1 << num_vars):
        assignment = [(mask >> i) & 1 == 1 for i in range(num_vars)]  # var i+1
        ok = True
        for clause in clauses:
            clause_satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                lit_true = val if lit > 0 else (not val)
                if lit_true:
                    clause_satisfied = True
                    break
            if not clause_satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the ExactCover instance has an exact cover.

    Uses a simple recursive backtracking algorithm.  The universe size is
    small in the generated tests, so this exhaustive search is sufficient.
    """
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    uncovered = set(range(u))

    # Pre‑process: discard empty sets and duplicate sets.
    processed_sets = []
    seen = set()
    for s in sets:
        s_tuple = tuple(sorted(s))
        if not s:
            continue
        if s_tuple in seen:
            continue
        seen.add(s_tuple)
        processed_sets.append(set(s))

    def backtrack(remaining: set[int]) -> bool:
        if not remaining:
            return True
        elem = min(remaining)
        for s in processed_sets:
            if elem not in s:
                continue
            if not s.isdisjoint(remaining) and s <= remaining:
                if backtrack(remaining - s):
                    return True
        return False

    return backtrack(uncovered)


def generate_three_sat_instances() -> List[Dict[str, Any]]:
    """Generate a modest collection of valid ThreeSat instances.

    For each number of variables 0‑4 we generate all possible clauses (subject
    to the three‑literal distinct‑variable rule) and then consider all subsets
    of up to two clauses.  This keeps the total number of instances manageable
    while still covering many edge‑cases.
    """
    instances: List[Dict[str, Any]] = []
    for num_vars in range(0, 5):
        clauses = []
        if num_vars >= 3:
            var_choices = list(itertools.combinations(range(1, num_vars + 1), 3))
            for vars_triplet in var_choices:
                for signs in itertools.product([True, False], repeat=3):
                    clause = []
                    for v, pos in zip(vars_triplet, signs):
                        clause.append(v if pos else -v)
                    clauses.append(clause)
        for r in range(0, min(3, len(clauses) + 1)):
            for subset in itertools.combinations(clauses, r):
                instance = {"num_vars": num_vars, "clauses": [list(c) for c in subset]}
                try:
                    ThreeSat.validate(instance)
                except Exception:
                    continue
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_three_sat_instances()
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        sat = three_sat_bruteforce(inst)
        reduced = reduce_instance(inst)
        ExactCover.validate(reduced)
        cover = exact_cover_bruteforce(reduced)
        if sat == cover:
            passed += 1
        else:
            print("Mismatch on instance", idx, file=sys.stderr)
            print(json.dumps(inst, indent=2), file=sys.stderr)
            print("Reduced instance:", json.dumps(reduced, indent=2), file=sys.stderr)
            print(f"ThreeSat answer: {sat}, ExactCover answer: {cover}", file=sys.stderr)
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
