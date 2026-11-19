"""Test the reduction from Hamiltonian Cycle to SAT.

The script implements brute‑force solvers for both problems based directly on
the definitions in ``problems.py`` and then checks that for a collection of
small instances the answer of the SAT instance produced by ``reduce`` matches
the answer of the original Hamiltonian‑Cycle instance.

If every test passes we write ``verdict.json`` with ``verified: true``.
Otherwise ``verified`` is false.  The number of tests run and passed are also
recorded.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat
from reduce import reduce


def hc_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has a Hamiltonian cycle.

    Implements the definition literally: try every permutation of the vertices
    and check whether consecutive vertices (including the wrap‑around) are
    edges of the graph.
    """
    n = instance["n"]
    if n <= 2:
        return False
    edges = set()
    for u, v in instance["edges"]:
        edges.add((u, v))
        edges.add((v, u))
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i + 1) % n]
            if (u, v) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the CNF formula is satisfiable.

    Brute‑forces all assignments of the variables (up to a reasonable size).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for clause in clauses:
        if not clause:
            return False
    for bits in range(1 << m):
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


def generate_graphs(n: int) -> List[Dict[str, Any]]:
    """Generate all simple undirected graphs on ``n`` vertices.

    The representation matches the expected instance format.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[Dict[str, Any]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total = 0
    passed = 0
    for n in range(0, 5):
        for graph in generate_graphs(n):
            total += 1
            HamiltonianCycle.validate(graph)
            hc_ans = hc_bruteforce(graph)
            sat_instance = reduce(graph)
            Sat.validate(sat_instance)
            sat_ans = sat_bruteforce(sat_instance)
            if hc_ans == sat_ans:
                passed += 1
            else:
                print("Mismatch for graph", graph, file=sys.stderr)
                print("HC answer", hc_ans, "SAT answer", sat_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
