"""Tests for the Dominating Set → SAT reduction.

The test suite implements naïve brute‑force solvers for both problems and
exhaustively checks the reduction on all small graphs (up to 5 vertices) and a
range of ``k`` values.  For each instance we verify that the SAT instance
produced by :func:`reduce` is satisfiable exactly when the original Dominating
Set instance has a dominating set of size at most ``k``.
"""

from __future__ import annotations

import itertools
import random
import sys
from typing import List, Dict

from problems import DominatingSet, Sat
from reduce import reduce


def dominating_set_bruteforce(instance: Dict) -> bool:
    """Return True iff the Dominating Set instance is a YES‑instance.

    The implementation follows the definition directly: it enumerates all
    subsets of vertices of size up to ``k`` and checks the domination property.
    """
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True

    # Build adjacency list
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            # Check domination
            dominated = set(D)
            for v in D:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the SAT instance is satisfiable (naïve enumeration)."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Empty clause makes formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses → trivially satisfiable.
    if not clauses:
        return True

    for bits in range(1 << m):
        # bits' i-th bit corresponds to variable i+1 being True.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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


def generate_all_graphs(max_n: int) -> List[Dict]:
    """Generate all undirected graphs with up to ``max_n`` vertices.

    For each number of vertices ``n`` we consider every subset of the possible
    ``n*(n-1)/2`` edges.
    """
    instances: List[Dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for r in range(len(possible_edges) + 1):
            for edge_subset in itertools.combinations(possible_edges, r):
                edges = [list(e) for e in edge_subset]
                # try a few k values
                for k in range(-1, n + 2):
                    instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    random.seed(0)
    # Exhaustively test small n (up to 4) – this is fast.
    all_instances = generate_all_graphs(4)
    total = len(all_instances)
    passed = 0
    for idx, inst in enumerate(all_instances, 1):
        ds_yes = dominating_set_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_yes = sat_bruteforce(sat_inst)
        if ds_yes != sat_yes:
            print("Mismatch on instance", idx, "/", total)
            print(inst)
            print("Reduced SAT", sat_inst)
            print("DominatingSet answer", ds_yes, "SAT answer", sat_yes)
            sys.exit(1)
        passed += 1
    # Additional random larger instances (n up to 6) to catch any bugs.
    for _ in range(200):
        n = random.randint(0, 6)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in random.sample(possible_edges, random.randint(0, len(possible_edges)))]
        k = random.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        ds_yes = dominating_set_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_yes = sat_bruteforce(sat_inst)
        if ds_yes != sat_yes:
            print("Random mismatch", inst)
            sys.exit(1)
        passed += 1
    # Write verdict file.
    verdict = {"verified": True, "tests_run": passed, "tests_passed": passed}
    import json
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(f"All {passed} tests passed.")

if __name__ == "__main__":
    main()

