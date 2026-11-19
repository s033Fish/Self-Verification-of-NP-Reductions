"""Automated tests for the reduction from ThreeSat to IndependentSet.

The repository provides only validation functions for the two problems.
To verify the correctness of ``reduce.py`` we implement brute‑force
solvers for both source and target problems and then compare the answers
on a large number of randomly generated small instances.

The script:
* Generates random 3‑SAT instances with up to 4 variables and up to 5
  clauses.  The generator respects the format constraints (exactly three
  distinct variables per clause, no complementary literals in the same
  clause).
* For each instance it computes the correct answer using a simple
  exhaustive search.
* It runs ``reduce`` on the instance, validates the produced target
  instance and solves the Independent‑Set instance also by exhaustive
  search.
* It records whether the answers match.

At the end a JSON file ``verdict.json`` is written with the fields required
by the task specification:

```
{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}
```

The script exits with status 0 regardless of the outcome – the presence of
``verdict.json`` is what will be inspected by the evaluation harness.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from typing import List, Dict

from problems import ThreeSat, IndependentSet
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for the ThreeSat problem.

    Returns True iff there exists an assignment to the variables that makes
    every clause contain at least one true literal.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all possible assignments as a tuple of booleans indexed by
    # variable number (1‑based).  ``True`` means the variable is assigned
    # true.
    for bits in product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1
        ok = True
        for clause in clauses:
            clause_satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0:
                    clause_satisfied = clause_satisfied or val
                else:
                    clause_satisfied = clause_satisfied or (not val)
                if clause_satisfied:
                    break
            if not clause_satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: Dict) -> bool:
    """Brute‑force solver for IndependentSet.

    Returns True iff there exists an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = {(min(u, v), max(u, v)) for u, v in instance["edges"]}
    k = instance["k"]
    # Early trivial cases
    if k <= 0:
        return True
    if k > n:
        return False
    # Check all subsets of size >= k (small n, so exhaustive is fine)
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            # Verify independence
            independent = True
            for u, v in combinations(subset, 2):
                if (min(u, v), max(u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict:
    """Generate a random valid ThreeSat instance.

    The generator respects the constraints: each clause has three distinct
    variables and does not contain both a variable and its negation.
    """
    m = random.randint(0, max_vars)
    # If there are fewer than 3 variables, a valid 3‑SAT formula cannot have
    # any clause (each clause needs three distinct variables). In that case
    # we only generate the empty clause list.
    if m < 3:
        return {"num_vars": m, "clauses": []}
    # Number of clauses can be zero as well.
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Choose 3 distinct variables from the available pool.
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_in_clause:
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    # Generate a reasonable number of test cases
    for _ in range(200):
        src = random_three_sat()
        # Validate source (should never raise)
        ThreeSat.validate(src)
        src_ans = solve_three_sat(src)
        tgt = reduce_instance(src)
        # Validate target (should never raise)
        IndependentSet.validate(tgt)
        tgt_ans = solve_independent_set(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            # For debugging, print the failing instance
            print("Mismatch!", file=sys.stderr)
            print("Source:", src, file=sys.stderr)
            print("Source answer:", src_ans, file=sys.stderr)
            print("Target:", tgt, file=sys.stderr)
            print("Target answer:", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

