"""Automated tests for the reduction from ThreeSat to VertexCover.

The script generates many small 3‑SAT instances, applies ``reduce`` and checks
that the answer of the generated VertexCover instance matches the answer of
the original formula as computed by the brute‑force solvers.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product

import problems
from reduce import reduce as reduce_instance
from solve_three_sat import solve_three_sat
from solve_vertex_cover import solve_vertex_cover


def generate_all_clauses(vars_count: int) -> list[list[int]]:
    """Return all possible 3‑literal clauses over ``vars_count`` variables.
    Each clause uses three distinct variables and each literal can be positive
    or negative.
    """
    clauses = []
    for vars_tuple in combinations(range(1, vars_count + 1), 3):
        # for each variable choose sign
        for signs in product([1, -1], repeat=3):
            clause = [signs[i] * vars_tuple[i] for i in range(3)]
            clauses.append(clause)
    return clauses


def random_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    m = random.randint(0, max_vars)
    # For m < 3, clauses must be empty per problem definition, but the validator
    # only requires literals within range, not that m>=3 when clauses exist.
    # We'll simply allow zero clauses when m<3.
    possible_clauses = generate_all_clauses(m) if m >= 3 else []
    c = random.randint(0, max_clauses)
    clauses = random.sample(possible_clauses, min(c, len(possible_clauses)))
    return {"num_vars": m, "clauses": clauses}


def test_one(instance: dict) -> bool:
    # Validate source instance
    problems.ThreeSat.validate(instance)
    # Compute answers
    sat = solve_three_sat(instance)
    vc_instance = reduce_instance(instance)
    # Validate target instance
    problems.VertexCover.validate(vc_instance)
    vc = solve_vertex_cover(vc_instance)
    return sat == vc


def main() -> None:
    total = 0
    passed = 0
    # Exhaustive tests for small m and clause counts
    for m in range(0, 5):
        all_clauses = generate_all_clauses(m) if m >= 3 else []
        # test all subsets of clauses up to size 3
        max_c = min(3, len(all_clauses))
        for csize in range(0, max_c + 1):
            for clause_subset in combinations(all_clauses, csize):
                instance = {"num_vars": m, "clauses": list(clause_subset)}
                total += 1
                try:
                    if test_one(instance):
                        passed += 1
                except Exception as e:
                    print("Error on instance", instance, file=sys.stderr)
                    raise
    # Additional random tests
    for _ in range(200):
        instance = random_instance()
        total += 1
        if test_one(instance):
            passed += 1
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
