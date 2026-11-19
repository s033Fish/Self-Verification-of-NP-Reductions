"""Test the reduction from 3‑SAT to 3‑Coloring.

The task requires us to verify that the provided ``reduce`` function maps
instances of ``ThreeSat`` to instances of ``ThreeColoring`` such that the
YES‑answers coincide.  Because the original repository does not contain any
solvers, we implement tiny brute‑force solvers for both problems and run a
large but still manageable set of random small instances.

The script is executed directly (``python test_reduce.py``).  It writes a
``verdict.json`` file in the current directory with the fields required by
the task description:

```
{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}
```

If any test fails the ``verified`` flag is set to ``false``.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import Dict, List

from problems import ThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force SAT solver for the 3‑SAT format.

    Returns ``True`` iff there exists an assignment to the variables that
    satisfies all clauses.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Iterate over all 2^m assignments.
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: Dict) -> bool:
    """Brute‑force 3‑colorability tester.

    Tries all possible colourings (3^n) and checks edge constraints.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False


def generate_random_sat_instance(max_vars: int = 3, max_clauses: int = 4) -> Dict:
    """Generate a random 3‑SAT instance respecting the format constraints.

    The generator ensures each clause has three distinct variables and three
    literals (with random signs).  Variables are numbered from 1..m.
    """
    m = random.randint(0, max_vars)
    # If there are no variables, the only valid formula is the empty clause list.
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    # Ensure m >= 3 when we actually generate clauses (as required by the spec).
    if m < 3:
        # Allow formulas with zero clauses; they are trivially satisfiable.
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_in_clause:
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total_tests = 0
    passed = 0
    verified = True

    # Deterministic edge‑case instances.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # empty formula, satisfiable
        {"num_vars": 1, "clauses": []},  # no clauses, satisfiable
        {"num_vars": 3, "clauses": []},  # no clauses, satisfiable
        # Simple unsatisfiable instance: (x) ∧ (¬x) ∧ (y) ∧ (¬y) ∧ (z) ∧ (¬z)
        {
            "num_vars": 3,
            "clauses": [[1, 2, 3], [-1, -2, -3]],
        },
    ]

    for inst in edge_cases:
        total_tests += 1
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            verified = False
            print(f"Validation failed for edge case {inst}: {e}")
            continue
        sat = solve_three_sat(inst)
        reduced = reduce_instance(inst)
        try:
            ThreeColoring.validate(reduced)
        except Exception as e:
            verified = False
            print(f"Reduced instance validation failed: {e}")
            continue
        colorable = solve_three_coloring(reduced)
        if sat == colorable:
            passed += 1
        else:
            verified = False
            print("Mismatch on edge case", inst, sat, colorable)

    # Random instances.
    for _ in range(200):
        inst = generate_random_sat_instance()
        total_tests += 1
        try:
            ThreeSat.validate(inst)
        except Exception:
            # Invalid instance – skip (should not happen with our generator).
            verified = False
            continue
        sat = solve_three_sat(inst)
        reduced = reduce_instance(inst)
        try:
            ThreeColoring.validate(reduced)
        except Exception as e:
            verified = False
            print(f"Reduced instance validation error: {e}")
            continue
        colorable = solve_three_coloring(reduced)
        if sat == colorable:
            passed += 1
        else:
            verified = False
            print("Mismatch on random instance", inst, sat, colorable)

    verdict = {
        "verified": verified,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
