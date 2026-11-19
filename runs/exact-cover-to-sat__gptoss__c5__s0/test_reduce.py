"""Test the reduction from ExactCover to SAT.

The script implements brute‑force solvers for the source (ExactCover) and
target (Sat) problems, generates a number of random small instances, applies
the reduction defined in ``reduce.py`` and checks that the answers match.

If all generated tests pass, ``verdict.json`` is written with
``{"verified": true, "tests_run": N, "tests_passed": N}``.  Otherwise the
``verified`` field is false and the counts reflect the results.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from typing import List, Dict, Any

from problems import ExactCover, Sat
from reduce import reduce as reduce_ec_to_sat


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the ExactCover instance has an exact cover.

    Brute‑forces over all subsets of the given sets.
    """
    ExactCover.validate(instance)
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)
    # Edge case: empty universe is always satisfiable.
    if u == 0:
        return True

    # Pre‑convert each set to a frozenset for fast operations.
    set_frozen = [frozenset(s) for s in sets]

    for mask in range(1 << m):
        used: set[int] = set()
        ok = True
        for i in range(m):
            if mask >> i & 1:
                # If the set is empty, it contributes nothing and can be ignored.
                if not set_frozen[i]:
                    continue
                # Check disjointness.
                if used & set_frozen[i]:
                    ok = False
                    break
                used |= set_frozen[i]
        if ok and len(used) == u:
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Brute‑forces over all assignments of the given number of variables.
    """
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Empty clause makes the formula unsatisfiable.
    for clause in clauses:
        if not clause:
            return False
    for assignment in product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                if var >= m:
                    # Should not happen due to validation, but guard anyway.
                    continue
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_exact_cover_instance(max_universe: int = 4, max_sets: int = 5) -> Dict[str, Any]:
    """Generate a random ExactCover instance with small parameters.

    The universe size is chosen uniformly from 0..max_universe. For each set we
    randomly decide its elements.
    """
    u = random.randint(0, max_universe)
    num_sets = random.randint(0, max_sets)
    sets: List[List[int]] = []
    for _ in range(num_sets):
        # Random subset of the universe (may be empty)
        subset = [e for e in range(u) if random.choice([True, False])]
        # Ensure elements are distinct – they already are.
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    # Run a mixture of exhaustive small cases and random instances.
    # Exhaustive for u <= 3 and at most 3 sets.
    for u in range(0, 4):
        # generate all possible sets (including empty) up to size u
        all_subsets = []
        elems = list(range(u))
        for r in range(u + 1):
            for combo in combinations(elems, r):
                all_subsets.append(list(combo))
        # limit number of sets to 3 for tractability
        for num_sets in range(0, 4):
            # generate all possible lists of sets (allow repetitions)
            for sets_choice in product(all_subsets, repeat=num_sets):
                instance = {"universe_size": u, "sets": [list(s) for s in sets_choice]}
                total += 1
                try:
                    ec_ans = exact_cover_bruteforce(instance)
                    sat_instance = reduce_ec_to_sat(instance)
                    sat_ans = sat_bruteforce(sat_instance)
                    if ec_ans == sat_ans:
                        passed += 1
                    else:
                        print("Mismatch!", instance, sat_instance, ec_ans, sat_ans, file=sys.stderr)
                except Exception as e:
                    print("Error on instance", instance, e, file=sys.stderr)
    # Additional random tests
    for _ in range(200):
        inst = random_exact_cover_instance()
        total += 1
        try:
            ec_ans = exact_cover_bruteforce(inst)
            sat_inst = reduce_ec_to_sat(inst)
            sat_ans = sat_bruteforce(sat_inst)
            if ec_ans == sat_ans:
                passed += 1
            else:
                print("Random mismatch!", inst, sat_inst, ec_ans, sat_ans, file=sys.stderr)
        except Exception as e:
            print("Random error", inst, e, file=sys.stderr)

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
