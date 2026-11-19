"""Test the reduction from ThreeSat to SubsetSum.

The test suite generates many small random 3‑SAT instances, runs the
provided ``reduce`` function, validates the produced SubsetSum instance,
and checks that a brute‑force solver for both problems yields the same
answer.  It also covers a few hand‑crafted edge cases.

The script is deliberately simple and runs quickly because all instances
are tiny (at most 4 variables and 4 clauses).  This is sufficient to catch
most logical errors in the reduction implementation.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product

import problems
from reduce import reduce as reduce_instance


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for ThreeSat.

    ``instance`` follows the format defined in ``problems.ThreeSat``.
    Returns ``True`` iff the formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit)
                val = assignment.get(var, False)
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Brute‑force solver for SubsetSum.

    Returns ``True`` iff a subset of ``numbers`` sums exactly to ``target``.
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


def random_three_sat(m: int, n: int) -> dict:
    """Generate a random 3‑SAT instance with ``m`` variables and ``n`` clauses.

    Each clause contains three distinct variables with random signs.
    """
    clauses = []
    for _ in range(n):
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0

    # Edge cases that respect the ThreeSat validation rules.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # trivially satisfiable
        {"num_vars": 3, "clauses": []},  # no clauses, any assignment works
        # A single clause with three distinct variables – always satisfiable
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        # A small unsatisfiable instance (classic contradictory set)
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, -3], [-1, 2, -3], [-1, -2, 3]]},
    ]

    for instance in edge_cases:
        problems.ThreeSat.validate(instance)
        reduced = reduce_instance(instance)
        problems.SubsetSum.validate(reduced)
        ans_src = solve_three_sat(instance)
        ans_tgt = solve_subset_sum(reduced)
        tests_run += 1
        if ans_src == ans_tgt:
            tests_passed += 1
        else:
            print("Mismatch on edge case", instance, file=sys.stderr)

    # Random small instances.
    for m in range(0, 5):  # 0..4 variables
        max_clauses = 4
        for n in range(0, max_clauses + 1):
            for _ in range(20):
                if n > 0 and m < 3:
                    continue
                instance = random_three_sat(m, n)
                problems.ThreeSat.validate(instance)
                reduced = reduce_instance(instance)
                problems.SubsetSum.validate(reduced)
                ans_src = solve_three_sat(instance)
                ans_tgt = solve_subset_sum(reduced)
                tests_run += 1
                if ans_src == ans_tgt:
                    tests_passed += 1
                else:
                    print("Mismatch", json.dumps(instance), file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
