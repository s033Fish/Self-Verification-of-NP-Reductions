"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard):
  * For every vertex v of the source graph and every colour c in {0, 1, 2},
    create a target vertex  node(v, c) = 3*v + c.
  * For every source vertex v, add the triangle
        node(v,0) -- node(v,1) -- node(v,2) -- node(v,0)
    so that an independent set can pick at most one colour per vertex.
  * For every source edge {u, v}, add the three "consistency" edges
        node(u,c) -- node(v,c)   for c in {0, 1, 2}
    so that adjacent vertices cannot receive the same colour.
  * Set k = n.

A 3-colouring of the source yields an independent set of size n (pick the
colour used at each vertex), and conversely an independent set of size n must
pick exactly one node from each triangle and picks consistent colours, giving
a proper 3-colouring.  Hence the source is a yes-instance iff the target is.

The construction is clearly polynomial: O(n) vertices and O(n + m) edges.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    def node(vertex: int, colour: int) -> int:
        return 3 * vertex + colour

    target_edges: list[list[int]] = []

    # One triangle per source vertex: at most one colour may be chosen.
    for v in range(n):
        target_edges.append([node(v, 0), node(v, 1)])
        target_edges.append([node(v, 0), node(v, 2)])
        target_edges.append([node(v, 1), node(v, 2)])

    # For each source edge, forbid equal colours at its two endpoints.
    for u, v in edges:
        for c in range(3):
            target_edges.append([node(u, c), node(v, c)])

    return {"n": 3 * n, "edges": target_edges, "k": n}
