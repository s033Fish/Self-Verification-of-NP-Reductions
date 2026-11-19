"""Test the reduction from HamiltonianCycle to SAT.

The script enumerates all undirected simple graphs with up to ``MAX_N``
vertices, solves each instance by brute force, reduces it with the
provided ``reduce`` function, solves the resulting SAT instance also by
brute force, and checks that the answers agree.

It finally writes a ``verdict.json`` file containing the number of tests
run, the number passed and whether the reduction is verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict

from problems import HamiltonianCycle, Sat
from reduce import reduce

MAX_N = 4  # limit to keep SAT brute‑force tractable (2^16 assignments max)


def solve_hamiltonian_cycle(instance: Dict) -> bool:
    """Brute‑force solver for the Hamiltonian Cycle problem.

    Returns ``True`` iff there exists a Hamiltonian cycle in the given
    undirected graph.
    """
    n = instance["n"]
    edges = instance["edges"]
    edge_set = {frozenset(e) for e in edges}
    if n <= 2:
        return False
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i + 1) % n]
            if frozenset((u, v)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict) -> bool:
    """Brute‑force SAT solver for CNF formulas.

    ``instance`` follows the format defined in :class:`Sat`.
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
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(n: int) -> List[Dict]:
    """Generate every simple undirected graph on ``n`` vertices.

    The vertices are labelled ``0..n-1``.  Each possible edge is either
    present or absent, leading to ``2^{n choose 2}`` graphs.
    """
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    graphs: List[Dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for idx, (u, v) in enumerate(possible_edges):
            if (mask >> idx) & 1:
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total = 0
    passed = 0
    for n in range(0, MAX_N + 1):
        for graph in generate_all_graphs(n):
            HamiltonianCycle.validate(graph)
            hc_ans = solve_hamiltonian_cycle(graph)
            sat_instance = reduce(graph)
            Sat.validate(sat_instance)
            sat_ans = solve_sat(sat_instance)
            total += 1
            if hc_ans == sat_ans:
                passed += 1
            else:
                print("Mismatch!", graph, hc_ans, sat_ans, file=sys.stderr)
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
