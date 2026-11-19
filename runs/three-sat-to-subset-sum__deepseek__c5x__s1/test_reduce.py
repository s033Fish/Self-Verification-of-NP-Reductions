"""Test suite for the reduction from ThreeSat to SubsetSum.

The repository provides only validation functions for the two problems and a
``reduce`` implementation.  To verify the reduction we implement straightforward
brute‑force solvers for both source and target problems and compare their
answers on a collection of small, random instances.

The script generates a number of random 3‑SAT instances with a bounded number
of variables (0‑4) and clauses (0‑4).  For each instance we:

1. Validate the instance using ``ThreeSat.validate``.
2. Reduce it with ``reduce``.
3. Validate the produced SubsetSum instance.
4. Solve both the original and reduced instance with exhaustive search.
5. Record whether the answers match.

After all tests are executed the script writes ``verdict.json`` containing the
total number of tests run, the number that passed, and a boolean ``verified``
field that is true only if every test succeeded.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

import problems
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    The instance follows the format defined in ``ThreeSat``.  We try every
    assignment of ``num_vars`` boolean variables and return ``True`` if at least
    one assignment satisfies all clauses.
    """
    n = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in product([False, True], repeat=n):
        ok = True
        for clause in clauses:
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0:
                    lit_true = lit_true or val
                else:
                    lit_true = lit_true or (not val)
                if lit_true:
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict) -> bool:
    """Exhaustive subset‑sum solver.

    ``numbers`` may contain up to a few dozen elements in our tests, which is
    small enough for a full enumeration of all subsets.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target < 0:
        return False
    for mask in range(1 << len(numbers)):
        s = 0
        for i, num in enumerate(numbers):
            if mask & (1 << i):
                s += num
                if s > target:
                    break
        if s == target:
            return True
    return False


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> Dict:
    """Generate a random but well‑formed 3‑SAT instance.

    * ``num_vars`` is chosen uniformly in ``0..max_vars``.
    * ``clauses`` is a list of up to ``max_clauses`` clauses.  Each clause is
      constructed by picking three distinct variables (if ``num_vars`` >= 3)
      and assigning each a random sign.
    * When ``num_vars`` < 3 we generate an empty clause list, which is a valid
      edge case (the formula is trivially satisfiable).
    """
    n = random.randint(0, max_vars)
    clauses: List[List[int]] = []
    if n >= 3:
        num_clauses = random.randint(0, max_clauses)
        for _ in range(num_clauses):
            vars_selected = random.sample(range(1, n + 1), 3)
            clause = []
            for v in vars_selected:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": n, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_three_sat_instance()
        problems.ThreeSat.validate(instance)
        reduced = reduce_instance(instance)
        problems.SubsetSum.validate(reduced)
        ans_src = solve_three_sat(instance)
        ans_tgt = solve_subset_sum(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source:", instance, file=sys.stderr)
            print("Reduced:", reduced, file=sys.stderr)
            print("Source answer:", ans_src, "Target answer:", ans_tgt, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

