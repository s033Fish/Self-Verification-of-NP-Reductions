"""Tests for the SAT → Independent Set reduction.

The repository provides only validation functions for the two problems.
We implement small brute‑force solvers for SAT and Independent Set and
compare the answer of a SAT instance with the answer of its reduction.

The test generates a number of random small instances (including edge
cases such as empty clause lists, empty clauses, duplicated literals, etc.)
and checks that:

* ``reduce`` returns a syntactically valid Independent Set instance.
* The SAT solver and the Independent Set solver agree on the yes/no
  answer for the original instance and the reduced instance respectively.

If all generated instances satisfy the equivalence, the reduction is
considered verified.
"""

from __future__ import annotations

import random
import sys
from itertools import product, combinations

import problems  # provides Sat.validate and IndependentSet.validate
from reduce import reduce


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``problems.Sat``.  We simply
    enumerate all assignments for ``num_vars`` variables (0/1) and test each
    clause.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause list => satisfiable.
    if not clauses:
        return True
    for assign in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # Empty clause is always unsatisfied.
            if not clause:
                ok = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1  # variables are 1-indexed
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.

    The instance follows the format defined in ``problems.IndependentSet``.
    """
    n = instance["n"]
    # Convert edge lists to a set of (u, v) tuples for fast lookup.
    edges = {(u, v) for u, v in (tuple(e) for e in instance["edges"]))}
    # also store reverse direction for quick lookup
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets of size k up to n (small n only)
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            independent = True
            for u, v in combinations(subset, 2):
                if (u, v) in edge_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_random_sat(max_vars: int = 4, max_clauses: int = 4, max_lits: int = 3) -> dict:
    """Generate a random SAT instance respecting the validation rules.

    Variables are numbered from 1..num_vars.  Each clause may be empty or
    contain repeated literals.
    """
    num_vars = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: list[list[int]] = []
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if num_vars == 0:
                continue
            var = random.randint(1, num_vars)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        sat_instance = generate_random_sat()
        try:
            problems.Sat.validate(sat_instance)
        except Exception:
            print("Invalid SAT instance generated:", sat_instance, file=sys.stderr)
            raise
        sat_ans = sat_bruteforce(sat_instance)
        reduced = reduce(sat_instance)
        try:
            problems.IndependentSet.validate(reduced)
        except Exception:
            print("Reduced instance invalid for SAT:", sat_instance, file=sys.stderr)
            raise
        ind_ans = independent_set_bruteforce(reduced)
        total += 1
        if sat_ans == ind_ans:
            passed += 1
        else:
            print("Counterexample found:")
            print("SAT instance:", sat_instance)
            print("SAT answer:", sat_ans)
            print("Reduced instance:", reduced)
            print("Independent Set answer:", ind_ans)
            break
    import json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
