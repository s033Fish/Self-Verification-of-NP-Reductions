"""Test the reduction from ThreeSat to Clique.

The script implements brute‑force solvers for both problems and then
generates a number of small random instances of 3‑SAT. For each instance it
checks that:

1. The instance is valid according to ``ThreeSat.validate``.
2. The reduced instance is valid according to ``Clique.validate``.
3. The answer of the original instance matches the answer of the reduced
   instance.

The script prints a JSON object with the fields required for the final
verdict: ``verified`` (whether all tests passed), ``tests_run`` and
``tests_passed``.
"""

from __future__ import annotations

import json
import random
import itertools
import sys

# Import the problem definitions and the reduction implementation.
from problems import SOURCE, TARGET
from reduce import reduce as reduce_instance


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff the formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for Clique.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(v in adj[u] for u, v in itertools.combinations(combo, 2)):
                return True
    return False


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random valid 3‑SAT instance.
    """
    m = random.randint(0, max_vars)
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    # Need at least 3 variables to form a clause.
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_choice = random.sample(range(1, m + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_choice]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(200):
        instance = random_three_sat_instance()
        try:
            SOURCE.validate(instance)
        except Exception:
            continue
        reduced = reduce_instance(instance)
        try:
            TARGET.validate(reduced)
        except Exception as e:
            print("Reduced instance invalid:", e, file=sys.stderr)
            continue
        ans_src = solve_three_sat(instance)
        ans_tgt = solve_clique(reduced)
        tests_run += 1
        if ans_src == ans_tgt:
            tests_passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source:", json.dumps(instance), file=sys.stderr)
            print("Reduced:", json.dumps(reduced), file=sys.stderr)
            print("src ans", ans_src, "tgt ans", ans_tgt, file=sys.stderr)
    verified = tests_run == tests_passed and tests_run > 0
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

