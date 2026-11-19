"""Tests for the reduction from ThreeSat to DominatingSet.

The test suite implements exhaustive (brute‑force) solvers for both source
and target problems based on the formal definitions in ``problems.py``. For a
generated 3‑SAT instance we:

1. Compute the correct answer using the brute‑force SAT solver.
2. Apply ``reduce`` to obtain a Dominating‑Set instance.
3. Compute the correct answer for the Dominating‑Set instance using a brute‑
   force set‑cover search.
4. Verify that the two answers agree.

The suite also checks a few edge‑case instances explicitly. At the end a
``verdict.json`` file is written containing the number of tests run, the
number passed and a boolean ``verified`` flag indicating overall success.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import List, Dict

from problems import ThreeSat, DominatingSet
from reduce import reduce as reduce_instance


def solve_three_sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance follows the format described in ``ThreeSat``: a dict with
    ``num_vars`` and ``clauses`` where each clause is a list of three distinct
    literals.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Iterate over all 2^m assignments represented as bit masks.
    for mask in range(1 << m):
        # assignment[i] is True iff variable i+1 is true.
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set_bruteforce(instance: Dict) -> bool:
    """Return True iff the graph has a dominating set of size at most k.

    Exhaustively checks all subsets of vertices up to size ``k``. Suitable for
    the small graphs produced by the test harness.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Build adjacency list including self‑loops (a vertex dominates itself).
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # If k < 0, answer is always False per problem definition.
    if k < 0:
        return False
    # Trivial yes cases handled by brute force as well.
    for size in range(k + 1):
        for combo in itertools.combinations(range(n), size):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def generate_random_three_sat(m: int, t: int) -> Dict:
    """Generate a random 3‑SAT instance respecting the problem constraints.

    ``m`` may be zero. If ``t`` > 0 and ``m`` < 3 we still generate clauses by
    allowing repeated variables – the validator in ``ThreeSat`` will reject
    such instances, so the caller must ensure ``m >= 3`` when ``t`` > 0.
    """
    clauses = []
    for _ in range(t):
        # Choose three distinct variables.
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_random: int = 200) -> Dict:
    passed = 0
    total = 0

    # Edge‑case tests.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # trivially satisfiable
        {"num_vars": 3, "clauses": []},  # no clauses
    ]
    for case in edge_cases:
        total += 1
        sat = solve_three_sat_bruteforce(case)
        reduced = reduce_instance(case)
        dom = solve_dominating_set_bruteforce(reduced)
        if sat == dom:
            passed += 1

    # Random tests.
    for _ in range(num_random):
        # Choose small sizes to keep brute force feasible.
        m = random.randint(0, 4)
        # Ensure enough variables for clauses when needed.
        max_clauses = 5
        t = random.randint(0, max_clauses)
        if t > 0 and m < 3:
            # Skip invalid instances; they would be rejected by validation.
            continue
        case = generate_random_three_sat(m, t)
        total += 1
        sat = solve_three_sat_bruteforce(case)
        reduced = reduce_instance(case)
        dom = solve_dominating_set_bruteforce(reduced)
        if sat == dom:
            passed += 1

    return {"tests_run": total, "tests_passed": passed, "verified": passed == total}


if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result, indent=2))
    # Write verdict.json for the evaluation harness.
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(result, f)
