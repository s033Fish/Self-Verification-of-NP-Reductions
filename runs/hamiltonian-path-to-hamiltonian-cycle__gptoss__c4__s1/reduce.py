"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) we construct G' by adding a new vertex s
and connecting s to every vertex of G.  Formally:

* V' = V ∪ {s} where s = |V|.
* E' = E ∪ {{s, v} : v ∈ V}.

If G has a Hamiltonian path v1,…,vn then the cycle s‑v1‑v2‑…‑vn‑s is a
Hamiltonian cycle in G'.  Conversely, any Hamiltonian cycle in G' must start
and end at s (the only vertex of degree > 2) and therefore the remaining
vertices form a Hamiltonian path in G.  This reduction works for all n ≥ 2.

Edge cases:
* n = 0: the source instance is a definite NO.  We output a graph with a
  single vertex (n' = 1, no edges); by definition Hamiltonian‑Cycle answers
  NO for n ≤ 2.
* n = 1: the source instance is YES.  We output a triangle on three vertices
  (n' = 3, edges forming K3), which has a Hamiltonian cycle.
* n = 2: the construction above yields a triangle when the original edge is
  present (YES) and a V‑shaped graph otherwise (NO), matching the source.

The reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, HamiltonianCycle


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary representing a HamiltonianPath instance.

    Returns
    -------
    dict
        An instance of HamiltonianCycle that is a YES instance iff the input
        instance is a YES instance.
    """
    # Validate source instance.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case n = 0: always NO for both problems.
    if n == 0:
        reduced = {"n": 1, "edges": []}
        HamiltonianCycle.validate(reduced)
        return reduced

    # Edge case n = 1: source is YES. Return a triangle (3‑vertex clique).
    if n == 1:
        reduced = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}
        HamiltonianCycle.validate(reduced)
        return reduced

    # General case n >= 2.
    s = n  # new vertex index
    new_n = n + 1
    # Copy original edges.
    new_edges: List[List[int]] = [e.copy() for e in edges]
    # Connect s to every original vertex.
    for v in range(n):
        new_edges.append([s, v])

    reduced = {"n": new_n, "edges": new_edges}
    HamiltonianCycle.validate(reduced)
    return reduced

