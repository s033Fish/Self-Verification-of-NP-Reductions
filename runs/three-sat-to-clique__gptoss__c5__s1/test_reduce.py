"""Automated tests for the 3‑SAT → Clique reduction.

The repository provides only validation code for the two problems and a
``reduce`` implementation.  To verify the reduction we implement brute‑force
solvers for both source and target problems and then compare the answers on
many small random instances.

The script is deliberately lightweight – it does not depend on any external
libraries and runs quickly because the generated instances are tiny (≤5
variables, ≤4 clauses).  For each instance we check that:

* ``reduce`` returns a well‑formed Clique instance (the validation call will
  raise if not).
* The answer of the Clique solver on the reduced instance matches the answer
  of the 3‑SAT solver on the original instance.

If all generated tests pass we write ``verdict.json`` with ``verified: true``.
Otherwise ``verified`` is ``false`` and the counts of total and passed tests
are reported.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import List, Dict, Any

from problems import ThreeSat, Clique
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force SAT solver for the 3‑SAT instance.

    Returns ``True`` iff there exists an assignment to the ``num_vars``
    variables that satisfies all clauses.  The instance is assumed to be
    validated already.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all possible truth assignments as bit‑vectors.
    for bits in range(1 << m):
        # Evaluate each clause.
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1  # variables are 1‑based
                val = (bits >> var) & 1
                # literal is true if (lit>0 and val==1) or (lit<0 and val==0)
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for the Clique problem.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge lookup set for O(1) checks.
    edge_set = {frozenset(e) for e in edges}

    # Trivial edge cases handled directly.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size >= k (we can stop at the first success).
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Verify every pair is an edge.
            if all(frozenset((a, b)) in edge_set for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def random_three_sat_instance(max_vars: int = 5, max_clauses: int = 4) -> Dict[str, Any]:
    """Generate a random 3‑SAT instance respecting the validation rules.

    The function may return an empty formula (no clauses) which is allowed.
    """
    m = random.randint(0, max_vars)
    # Ensure at least 3 variables when we create clauses, as required by the
    # problem statement.  If m < 3 we simply produce zero clauses.
    if m < 3:
        return {"num_vars": m, "clauses": []}

    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Choose three distinct variables.
        vars_selected = random.sample(range(1, m + 1), 3)
        # Randomly assign a sign to each.
        clause = [v if random.choice([True, False]) else -v for v in vars_selected]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    total = 0
    passed = 0
    random.seed(0)  # deterministic for reproducibility
    for _ in range(200):  # generate a reasonable number of tests
        src = random_three_sat_instance()
        # Validate source (should never raise).
        ThreeSat.validate(src)
        # Reduce.
        tgt = reduce_instance(src)
        # Validate target (will raise if reduction produced an invalid instance).
        Clique.validate(tgt)
        # Solve both.
        ans_src = solve_three_sat(src)
        ans_tgt = solve_clique(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            # Print a minimal debug line for the failing case.
            print("Mismatch!", json.dumps({"src": src, "tgt": tgt, "src_ans": ans_src, "tgt_ans": ans_tgt}))
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

if __name__ == "__main__":
    main()

