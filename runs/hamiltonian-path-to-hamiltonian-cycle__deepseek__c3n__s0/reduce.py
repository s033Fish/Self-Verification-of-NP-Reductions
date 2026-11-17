"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Reduction
---------
Given a Hamiltonian Path instance G = (V, E) with |V| = n, build a
Hamiltonian Cycle instance G' by adding one brand-new vertex x and
connecting it to every vertex of G:

    V' = V u {x},   E' = E u { {v, x} : v in V }.

Correctness for n >= 2
----------------------
(=>) If v1 - v2 - ... - vn is a Hamiltonian path of G, then
     x - v1 - v2 - ... - vn - x is a Hamiltonian cycle of G'.
(<=) If G' has a Hamiltonian cycle, x has exactly two neighbours in it,
     both in V (x is adjacent only to V). Removing x from the cycle
     leaves a Hamiltonian path of G through all n vertices.

Edge cases
----------
* n = 0: G' has 1 vertex -> no cycle; source is no. Correct.
* n = 1: the naive construction gives G' with 2 vertices, which can never
  have a cycle, but the source is yes (a single vertex is a path). This is
  the one case the construction does not cover, so we map it to a fixed
  yes-instance of the target (the triangle).
* n = 2: G' has 3 vertices; a cycle must be the triangle, which exists iff
  the edge {0,1} is present -- exactly the source condition.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n == 1: source is always yes, but the construction below would produce
    # a 2-vertex graph, which can never contain a cycle. Map to the triangle,
    # a canonical yes-instance of Hamiltonian Cycle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])

    return {"n": n + 1, "edges": new_edges}
