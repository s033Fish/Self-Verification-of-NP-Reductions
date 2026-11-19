"""Automated tests for the DominatingSet → Sat reduction.

The repository provides only validation functions for the two problems.
We implement tiny brute‑force solvers for both source and target, generate
all small instances (n ≤ 5) and compare the answer of the reduction with the
answers of the solvers.  The test script prints a JSON object compatible with
the required ``verdict.json`` format.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

from problems import DominatingSet, Sat
from reduce import reduce as reduce_instance


def dominating_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the DominatingSet instance has a dominating set of size ≤ k.

    The implementation follows the specification in ``problems.py`` exactly.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True

    # Build adjacency list
    neigh: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)

    # Enumerate subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            selected = set(subset)
            # Check domination: each vertex either in selected or adjacent to one
            ok = True
            for v in range(n):
                if v in selected:
                    continue
                if not (neigh[v] & selected):
                    ok = False
                    break
            if ok:
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Brute‑force over all assignments of the ``num_vars`` variables.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: empty clause makes formula unsatisfiable
    for cl in clauses:
        if len(cl) == 0:
            return False

    # No clauses → trivially satisfiable
    if not clauses:
        return True

    # Iterate over all possible truth assignments
    for bits in range(1 << m):
        # bits's i‑th bit corresponds to variable i+1 being True
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_instances(max_n: int = 5) -> List[Dict[str, Any]]:
    """Generate every DominatingSet instance with n ≤ max_n.

    For each n we iterate over all possible edge subsets of the complete
    graph and over a range of k values from -1 to n+1 (covering the relevant
    edge cases).
    """
    instances = []
    for n in range(max_n + 1):
        # All possible undirected edges without loops
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            for k in range(-1, n + 2):  # include -1 and n+1 to test >n case
                inst = {"n": n, "edges": edges, "k": k}
                # Validation may raise, but our generation respects the format
                DominatingSet.validate(inst)
                instances.append(inst)
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0
    for inst in instances:
        # Compute ground‑truth answers
        expected = dominating_set_bruteforce(inst)
        # Reduce and solve the SAT instance
        sat_inst = reduce_instance(inst)
        # Ensure the reduction output validates against Sat
        Sat.validate(sat_inst)
        got = sat_bruteforce(sat_inst)
        if expected == got:
            passed += 1
        else:
            # Print a minimal diagnostic for debugging
            print("Mismatch!", json.dumps(inst), file=sys.stderr)
            print("Reduced SAT", json.dumps(sat_inst), file=sys.stderr)
            print("expected", expected, "got", got, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
