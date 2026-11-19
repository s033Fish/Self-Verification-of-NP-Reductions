"""Tests for the reduction from Dominating Set to SAT.

The repository provides only a reduction implementation.  To verify its
correctness we implement brute‑force solvers for both source and target
problems and compare the answers on a large set of randomly generated
instances (including edge‑cases).

The test script is executed directly by the evaluation harness – it does
not import any external test framework.  It prints a short summary and
exits with status 0 on success or non‑zero on failure.
"""

from __future__ import annotations

import itertools
import random
import sys
from typing import List, Dict, Any

from problems import DominatingSet, Sat
from reduce import reduce


def dominating_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Dominating Set instance has a dominating set of size ≤ k.

    The implementation follows the definition literally: it enumerates all
    subsets of vertices up to size ``k`` and checks the domination condition.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases matching the specification
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True

    # Build adjacency list including self (closed neighbourhood)
    neigh: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)
    for i in range(n):
        neigh[i].add(i)

    vertices = list(range(n))
    for size in range(k + 1):
        for subset in itertools.combinations(vertices, size):
            dominated = set()
            for v in subset:
                dominated.update(neigh[v])
            if len(dominated) == n:
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The number of variables is expected to be small in the generated tests,
    so exhaustive enumeration is feasible.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Empty formula (no clauses) is satisfiable.
    if not clauses:
        return True

    # Any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False

    for bits in range(1 << m):
        # bits' i‑th bit corresponds to variable i+1 being True.
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(bits & (1 << var))
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance(max_n: int = 5) -> Dict[str, Any]:
    """Create a random DominatingSet instance respecting the validation rules.

    The function limits ``n`` to ``max_n`` to keep exhaustive checking fast.
    """
    n = random.randint(0, max_n)
    # generate a simple undirected graph without parallel edges or self‑loops
    edges: List[List[int]] = []
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    random.shuffle(possible)
    # each possible edge is included with probability 0.4
    for u, v in possible:
        if random.random() < 0.4:
            edges.append([u, v])
    k = random.randint(-1, max(n, 0) + 2)  # allow values outside the normal range
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = generate_random_instance()
        # Validate source instance (should not raise)
        DominatingSet.validate(inst)
        # Reduce and validate target instance
        red = reduce(inst)
        Sat.validate(red)
        src_ans = dominating_set_bruteforce(inst)
        tgt_ans = sat_bruteforce(red)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source instance:", inst, file=sys.stderr)
            print("Reduced instance:", red, file=sys.stderr)
            print("Source answer:", src_ans, "Target answer:", tgt_ans, file=sys.stderr)
            sys.exit(1)
    # Write verdict file for the outer harness
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    print(f"All {total} tests passed.")

if __name__ == "__main__":
    main()
