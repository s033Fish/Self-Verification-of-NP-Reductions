"""Test the reduction from HamiltonianPath to SAT.

The test suite implements brute‑force solvers for both problems based on the
exact definitions in ``problems.py`` and checks that for a variety of small
graph instances the answer of the SAT instance produced by ``reduce`` matches
the answer of the original Hamiltonian‑Path instance.

If all checks pass we write ``verdict.json`` with ``verified: true``;
otherwise ``verified: false``.  The file also records the number of tests run
and how many passed.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List

import problems
from reduce import reduce


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a Hamiltonian path.

    The instance is assumed to be valid according to ``HamiltonianPath``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    The instance is assumed to be valid according to ``Sat``.
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


def generate_all_graphs(n: int) -> List[dict]:
    """Generate all simple undirected graphs with ``n`` vertices.

    Each graph is represented as a dict matching the HamiltonianPath format.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[dict] = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if (mask >> i) & 1:
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total = 0
    passed = 0
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
    ]
    for inst in edge_cases:
        total += 1
        problems.HamiltonianPath.validate(inst)
        hp = hamiltonian_path_bruteforce(inst)
        sat_inst = reduce(inst)
        problems.Sat.validate(sat_inst)
        sat = sat_bruteforce(sat_inst)
        if hp == sat:
            passed += 1
    for n in range(3, 5):
        for inst in generate_all_graphs(n):
            total += 1
            problems.HamiltonianPath.validate(inst)
            hp = hamiltonian_path_bruteforce(inst)
            sat_inst = reduce(inst)
            problems.Sat.validate(sat_inst)
            sat = sat_bruteforce(sat_inst)
            if hp == sat:
                passed += 1
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
