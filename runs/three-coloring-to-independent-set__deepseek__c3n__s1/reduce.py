"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard):
  * For every vertex v of the source graph and every colour c in {0,1,2}
    create a target vertex (v, c), encoded as index 3*v + c.
  * For every source vertex v add the triangle
        (v,0)-(v,1)-(v,2)
    so that an independent set can use at most one colour-node per vertex.
  * For every source edge {u, v} and every colour c add the conflict edge
        (u,c)-(v,c)
    so that adjacent vertices cannot receive the same colour.
  * Set k = n (the number of source vertices).

The target graph has 3n vertices.  Any independent set of size n must pick
exactly one colour-node per vertex (n disjoint triangles, at most one each),
and the conflict edges guarantee adjacent vertices get different colours.
Hence a size-n independent set exists iff the source graph is 3-colourable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    new_n = 3 * n
    new_edges: list[list[int]] = []
    seen: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            new_edges.append([u, v])

    # Triangle per source vertex: at most one colour per vertex.
    for v in range(n):
        base = 3 * v
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)

    # Conflict edges: adjacent vertices must use different colours.
    for u, v in edges:
        for c in range(3):
            add_edge(3 * u + c, 3 * v + c)

    return {"n": new_n, "edges": new_edges, "k": n}
