"""Tests for the reduction from ThreeSat to SubsetSum.

The reduction in ``reduce.py`` is intentionally simple: it solves the 3‑SAT
instance by brute force and then returns a trivial Subset‑Sum instance whose
answer matches the computed result. The functional correctness of this
approach can be verified by comparing the answer of the generated Subset‑Sum
instance with the answer of the original 3‑SAT instance on many small random
instances.

The test suite:
* Generates a collection of random 3‑SAT instances with up to 4 variables
  (the limit keeps the brute‑force solver fast).
* For each instance it computes the exact SAT answer using a straightforward
  exhaustive search.
* It calls ``reduce.reduce`` to obtain a Subset‑Sum instance and then solves
  that instance also by exhaustive search.
* It asserts that the two answers agree.

The script also records the number of tests executed and writes a
``verdict.json`` file summarising the outcome. The ``verified`` field is set to
``True`` only if all functional tests pass **and** the reduction runs in
polynomial time without employing a brute‑force SAT solver. Detecting the
runtime property automatically is non‑trivial; for the purpose of this
automated review we conservatively set ``verified`` to ``False`` because the
implementation explicitly uses an exponential‑time brute‑force algorithm.
"""

from __future__ import annotations

import json
import random
from typing import List, Dict, Any

import pytest

from problems import ThreeSat, SubsetSum
from reduce import reduce as reduce_instance


def brute_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT (identical to the one used in ``reduce``)."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def brute_subset_sum(instance: Dict[str, Any]) -> bool:
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


def random_three_sat(num_vars: int, num_clauses: int) -> Dict[str, Any]:
    """Generate a random 3‑SAT instance respecting the problem constraints.

    The 3‑SAT definition requires each clause to contain three *distinct*
    variables.  When ``num_vars`` is less than three, the only valid formula is
    one with no clauses.  In that case we ignore ``num_clauses`` and return an
    empty clause list.
    """
    if num_vars < 3:
        return {"num_vars": num_vars, "clauses": []}
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, num_vars + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


@pytest.mark.parametrize("num_vars", [0, 1, 2, 3, 4])
def test_random_instances(num_vars: int) -> None:
    for _ in range(20):
        num_clauses = random.randint(0, 5)
        instance = random_three_sat(num_vars, num_clauses)
        ThreeSat.validate(instance)
        sat_answer = brute_sat(instance)
        reduced = reduce_instance(instance)
        SubsetSum.validate(reduced)
        subset_answer = brute_subset_sum(reduced)
        assert sat_answer == subset_answer


def main() -> None:
    result = pytest.main(["-q", __file__])
    tests_passed = result == 0
    tests_run = 5 * 20
    verdict = {
        "verified": tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_run if tests_passed else 0,
    }
    verdict["verified"] = False
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)

if __name__ == "__main__":
    main()
