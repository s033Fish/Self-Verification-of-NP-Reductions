"""Test the reduction from ThreeSat to VertexCover.

The tests generate a number of small random 3‑SAT instances, solve them by
brute‑force, apply ``reduce`` and solve the resulting Vertex‑Cover instance
by brute‑force as well.  The answers must coincide.  A verdict JSON file is written describing the outcome.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

from problems import SOURCE, TARGET
from reduce import reduce as reduce_instance


def three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance follows the format defined in ``problems.py``.  For small
    numbers of variables (the tests only use up to 3) we simply enumerate all
    possible truth assignments.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            lit_vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                lit_vals.append(val if lit > 0 else not val)
            if not any(lit_vals):
                ok = False
                break
        if ok:
            return True
    return False


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size at most k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def random_three_sat_instance(max_vars: int = 3, max_clauses: int = 3) -> dict:
    """Generate a random valid 3‑SAT instance respecting the validation rules."""
    m = random.randint(0, max_vars)
    # If we will generate clauses, ensure at least 3 variables as required.
    if m > 0 and m < 3:
        m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m == 0:
            break
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_in_clause:
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(30):
        instance = random_three_sat_instance()
        SOURCE.validate(instance)
        sat = three_sat_bruteforce(instance)
        reduced = reduce_instance(instance)
        TARGET.validate(reduced)
        vc = vertex_cover_bruteforce(reduced)
        total += 1
        if sat == vc:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("ThreeSat instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced VertexCover instance:", json.dumps(reduced), file=sys.stderr)
            print(f"ThreeSat answer={sat}, VertexCover answer={vc}", file=sys.stderr)
            break
    verified = passed == total
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
