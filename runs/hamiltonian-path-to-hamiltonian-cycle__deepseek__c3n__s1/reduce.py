"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Standard construction: given G on vertices 0..n-1, add a new universal
vertex w = n joined to every original vertex.  Then

    G has a Hamiltonian path  <=>  G' has a Hamiltonian cycle.

Proof sketch:
  (=>) A Hamiltonian path v0,...,v_{n-1} of G, together with the two
       edges v0-w and w-v_{n-1}, forms a Hamiltonian cycle of G'.
  (<=) Any Hamiltonian cycle of G' visits w; deleting w from it leaves a
       Hamiltonian path of G (the two neighbours of w become its ends).

Edge cases:
  * n = 0: source is no.  We return a 1-vertex graph, which has no cycle.
  * n = 1: source is yes (single vertex is a path), but the construction
    would give a 2-vertex graph, which can never have a cycle.  So we map
    it to the triangle, which is a yes instance of Hamiltonian Cycle.
  * n >= 2: the construction is used directly.  For n = 2 it yields the
    triangle exactly when the edge [0, 1] is present, matching the source.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # Source: no.  Target: a single vertex has no cycle -> no.
        return {"n": 1, "edges": []}

    if n == 1:
        # Source: yes.  Target: the triangle is the smallest yes instance.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a universal vertex w = n.
    w = n
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, w])
    return {"n": n + 1, "edges": new_edges}
