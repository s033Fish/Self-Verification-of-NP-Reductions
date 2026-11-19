"""Polynomial-time reduction from Hamiltonian Path (SOURCE) to
Hamiltonian Cycle (TARGET).

Construction
------------
Given a source instance G = (V, E) with V = {0, ..., n-1}:

* If n == 0: G has no Hamiltonian path, and the target instance
  {"n": 0, "edges": []} has no Hamiltonian cycle.  Return it unchanged.

* If n == 1: G has a Hamiltonian path (the lone vertex), so we must return
  a YES instance of Hamiltonian Cycle.  The triangle on 3 vertices is the
  smallest YES instance; return it.

* If n >= 2: add one new vertex w = n and connect it to every vertex of G.
  Return G' = (V u {w}, E u {{v, w} : v in V}).

Correctness for n >= 2
----------------------
(=>) If v1, ..., vn is a Hamiltonian path of G, then
     w, v1, ..., vn, w is a Hamiltonian cycle of G' (all consecutive pairs
     are edges, and w-v1, vn-w exist by construction).

(<=) If G' has a Hamiltonian cycle C, it must visit w.  The two neighbours
     of w on C are vertices of G, and deleting w from C leaves a path that
     visits every vertex of G exactly once, i.e. a Hamiltonian path of G.

The construction is clearly polynomial: O(n + |E|) time and output size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n == 0: no Hamiltonian path; empty graph has no Hamiltonian cycle.
    if n == 0:
        return {"n": 0, "edges": []}

    # n == 1: the single vertex is a Hamiltonian path, so we need a YES
    # target instance.  A triangle is the smallest YES instance.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a new universal vertex.
    new_vertex = n
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])
    return {"n": n + 1, "edges": new_edges}
