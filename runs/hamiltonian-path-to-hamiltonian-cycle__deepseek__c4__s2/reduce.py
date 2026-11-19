"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Reduction
---------
Given a Hamiltonian Path instance G = (V, E) with V = {0, ..., n-1}, build the
Hamiltonian Cycle instance G' by adding one brand-new vertex x and connecting it
to every vertex of G:

    V' = V u {x},   E' = E u { {v, x} : v in V }.

Correctness (for n >= 2):
  * If G has a Hamiltonian path v_1, ..., v_n, then
        x, v_1, ..., v_n, x
    is a Hamiltonian cycle of G' (all edges v_i v_{i+1} exist in G, and x is
    adjacent to every vertex).
  * If G' has a Hamiltonian cycle, then x appears exactly once in it and its two
    neighbours on the cycle are vertices of G (x has no other neighbours).
    Removing x from the cycle leaves a path through all n vertices of G using
    only edges of G, i.e. a Hamiltonian path of G.

Edge cases:
  * n = 0: source is NO.  The construction yields a 1-vertex graph, which is NO
    for Hamiltonian Cycle.  Correct.
  * n = 1: source is YES (a single vertex is a path).  The construction would
    yield a 2-vertex graph, which is NO for Hamiltonian Cycle, so we special-case
    it and return the triangle (3 vertices, all 3 edges), which is YES.
  * n = 2: source is YES iff edge {0,1} exists.  The construction yields a
    triangle exactly when {0,1} exists (x is adjacent to both 0 and 1), and a
    path 0-x-1 (no cycle) otherwise.  Correct.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n == 1 is the only case where "add a universal vertex" fails: the source
    # is YES but the constructed 2-vertex graph has no cycle.  Return a triangle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])
    return {"n": n + 1, "edges": new_edges}
