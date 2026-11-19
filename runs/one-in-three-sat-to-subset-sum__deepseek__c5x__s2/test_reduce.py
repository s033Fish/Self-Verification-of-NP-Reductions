"""Test the correctness of the reduction from OneInThreeSat to SubsetSum.

The script implements brute‑force solvers for both source and target
problems, generates a number of small random instances, applies the
provided ``reduce`` function and checks that the answers coincide.

It writes a ``verdict.json`` file with the fields required by the task
description:

* ``verified`` – ``true`` iff all generated tests passed.
* ``tests_run`` – total number of instances tested.
* ``tests_passed`` – number of instances for which the reduction was
  correct.

The script is intended to be run directly (e.g. ``python test_reduce.py``).
It does not require any external dependencies beyond the standard library.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – ensures validation helpers are available
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for the positive 1‑in‑3‑SAT problem.

    ``instance`` follows the format defined in ``problems.OneInThreeSat``.
    The function enumerates all possible truth assignments for the ``m``
    variables and returns ``True`` iff there exists an assignment where each
    clause has exactly one true literal.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses – always satisfiable.
    if not clauses:
        return True

    for assignment in product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(assignment[var - 1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict[str, Any]) -> bool:
    """Brute‑force subset‑sum solver.

    Returns ``True`` iff some sub‑list of ``numbers`` sums to ``target``.
    The implementation uses a simple depth‑first search; the input size in
    the tests is deliberately kept small (≤ 12 numbers) so exponential time
    is acceptable.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Trivial cases handled directly.
    if target == 0:
        return True
    if target < 0:
        return False
    if not numbers:
        return target == 0

    # Depth‑first search.
    def dfs(idx: int, current: int) -> bool:
        if current == target:
            return True
        if idx == len(numbers) or current > target:
            return False
        # Choose the current number.
        if dfs(idx + 1, current + numbers[idx]):
            return True
        # Skip the current number.
        return dfs(idx + 1, current)

    return dfs(0, 0)


def generate_random_instance(max_vars: int = 5, max_clauses: int = 6) -> Dict[str, Any]:
    """Create a random valid 1‑in‑3‑SAT instance.

    ``max_vars`` and ``max_clauses`` bound the size of the generated instance.
    The function respects the validation rules from ``problems`` (e.g., all
    literals are positive and distinct within a clause).
    """
    m = random.randint(0, max_vars)
    # Ensure that if there are clauses we have at least 3 variables.
    if m < 3:
        # With fewer than 3 variables we can only generate an empty clause list.
        return {"num_vars": m, "clauses": []}

    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # Choose three distinct variables uniformly.
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total_tests = 0
    passed = 0
    # Generate a mixture of deterministic edge cases and random instances.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
    ]
    instances: List[Dict[str, Any]] = edge_cases[:]
    # Add 200 random instances.
    for _ in range(200):
        instances.append(generate_random_instance())

    for inst in instances:
        total_tests += 1
        # Validate using the problem class (will raise if malformed).
        problems.OneInThreeSat.validate(inst)
        src_ans = solve_one_in_three_sat(inst)
        reduced = reduce_instance(inst)
        # Validate the reduced instance as a SubsetSum problem.
        problems.SubsetSum.validate(reduced)
        tgt_ans = solve_subset_sum(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            # Print a minimal diagnostic for debugging.
            print("Mismatch found:")
            print("Source instance:", json.dumps(inst))
            print("Source answer:", src_ans)
            print("Reduced instance:", json.dumps(reduced))
            print("Target answer:", tgt_ans)
            # Continue testing remaining instances.

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print the verdict for immediate visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
