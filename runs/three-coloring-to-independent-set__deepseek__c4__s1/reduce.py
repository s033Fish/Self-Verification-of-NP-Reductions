"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard):
  * For every vertex v of the source graph and every colour c in {0,1,2},
    create a target vertex (v, c), numbered 3*v + c.
  * For every source vertex v, add the triangle on (v,0), (v,1), (v,2) so
    that at most one colour can be chosen for v.
  * For every source edge {u, v} and every colour c, add the edge
    {(u,c), (v,c)} so that adjacent source vertices cannot share a colour.
  * Set k = n (number of source vertices).

A 3-colouring of the source gives an independent set of size n by picking
one colour per vertex; conversely an independent set of size n must pick
exactly one vertex from each colour-triangle and, by the edge constraints,
encodes a proper 3-colouring.  The construction is clearly polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_n = 3 * n
    new_edges: list[list[int]] = []

    # One triangle per source vertex: at most one colour may be selected.
    for v in range(n):
        base = 3 * v
        new_edges.append([base + 0, base + 1])
        new_edges.append([base + 0, base + 2])
        new_edges.append([base + 1, base + 2])

    # Same colour on both endpoints of a source edge is forbidden.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": new_n, "edges": new_edges, "k": n}
