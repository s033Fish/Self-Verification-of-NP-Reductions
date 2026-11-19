"""Test suite for the Hamiltonian Cycle to SAT reduction.

The repository provides a ``reduce`` function that translates a Hamiltonian
Cycle instance into a SAT instance.  To verify its correctness we implement
brute‑force solvers for both problems and compare the answers on a collection
of small graphs.

The test counts how many instances were checked and how many passed.  The
result is written to ``verdict.json`` as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List

# Import the reduction implementation.
from reduce import reduce as reduce_instance


def solve_hamiltonian(instance: dict) -> bool:
    """Brute‑force solver for Hamiltonian Cycle.

    Returns True iff the undirected graph described by ``instance`` contains a
    Hamiltonian cycle.
    """
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add((u, v) if u < v else (v, u))

    if n <= 2:
        return False
    # generate all permutations of vertices, fixing the first to avoid
    # duplicate cycles (direction and rotation).
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (verts[0],) + perm
        # check edges between consecutive vertices and wrap‑around
        ok = True
        for i in range(n):
            a = cycle[i]
            b = cycle[(i + 1) % n]
            if (a, b) if a < b else (b, a) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Brute‑force SAT solver for a CNF formula.

    ``instance`` contains ``num_vars`` and ``clauses`` where each clause is a
    list of integers (positive for true, negative for false).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Empty clause list is always satisfiable.
    if not clauses:
        return True
    # If any clause is empty, formula is unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    for assignment in range(1 << m):
        # assignment bit i corresponds to variable i+1 (True if bit set)
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool((assignment >> var) & 1)
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(n: int) -> List[dict]:
    """Yield every simple undirected graph on ``n`` vertices.

    The graph is represented as the required instance dictionary.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[dict] = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if (mask >> idx) & 1:
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total = 0
    passed = 0
    # Test n from 0 up to 5 (5 gives 1024 graphs, which is fast enough).
    for n in range(0, 6):
        for instance in generate_all_graphs(n):
            total += 1
            hc = solve_hamiltonian(instance)
            sat_instance = reduce_instance(instance)
            sat = solve_sat(sat_instance)
            if hc == sat:
                passed += 1
            else:
                print("Mismatch!", instance, "HC", hc, "SAT", sat, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
