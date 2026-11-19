"""Automated tests for the reduction from 3‑SAT to Vertex Cover.

The repository provides only validation code for the two problems and a
reduction implementation.  To verify the reduction we implement brute‑force
solvers for both problems, generate a collection of small random instances,
run the reduction, and compare the answers.

The script is executed by the evaluation harness – it creates a ``verdict``
dictionary that indicates whether all tests passed.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Tuple, Dict, Any

import problems  # validation utilities and problem classes
from reduce import reduce as reduction


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force check whether a 3‑SAT instance is satisfiable.

    ``instance`` follows the format defined in ``problems.ThreeSat``.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all 2^m assignments (True/False for each variable 1..m)
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # clause satisfied if any literal evaluates to True
            satisfied = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit < 0:
                    val = not val
                if val:
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_vertex_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force check whether a graph has a vertex cover of size ≤ k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    # enumerate all subsets of vertices up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def generate_random_three_sat(max_vars: int, max_clauses: int, trials: int) -> List[Dict[str, Any]]:
    """Generate a list of random 3‑SAT instances for testing.

    The generator respects the constraints of the problem definition:
    each clause contains three literals on distinct variables.
    """
    instances: List[Dict[str, Any]] = []
    for _ in range(trials):
        m = random.randint(0, max_vars)
        # ensure enough variables for a clause if we generate any
        max_possible_clauses = 0 if m < 3 else max_clauses
        c = random.randint(0, max_possible_clauses)
        clauses: List[List[int]] = []
        for _ in range(c):
            # pick 3 distinct variables
            vars_ = random.sample(range(1, m + 1), 3) if m >= 3 else []
            clause = []
            for v in vars_:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            # if m<3 we will have empty clause list anyway
            if clause:
                clauses.append(clause)
        instances.append({"num_vars": m, "clauses": clauses})
    return instances


def main() -> None:
    random.seed(0)
    # generate a modest number of instances covering edge cases
    test_instances = [
        {"num_vars": 0, "clauses": []},  # empty formula
        {"num_vars": 3, "clauses": []},  # no clauses but variables
    ]
    test_instances.extend(
        generate_random_three_sat(max_vars=4, max_clauses=3, trials=200)
    )

    total = len(test_instances)
    passed = 0
    for idx, inst in enumerate(test_instances):
        # validate source instance
        try:
            problems.ThreeSat.validate(inst)
        except Exception as e:
            print(f"Source instance {idx} failed validation: {e}", file=sys.stderr)
            continue
        sat = solve_three_sat(inst)
        # run reduction and validate target instance
        target = reduction(inst)
        try:
            problems.VertexCover.validate(target)
        except Exception as e:
            print(f"Reduced instance {idx} failed validation: {e}", file=sys.stderr)
            continue
        vc = solve_vertex_cover(target)
        if sat == vc:
            passed += 1
        else:
            print(f"Mismatch on instance {idx}: SAT={sat}, VC={vc}", file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
