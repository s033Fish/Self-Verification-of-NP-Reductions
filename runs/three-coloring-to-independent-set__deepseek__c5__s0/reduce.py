"""Polynomial-time reduction from 3-Coloring to Independent Set.

Reduction
---------
Given a 3-Coloring instance G = (V, E) with V = {0, ..., n-1}, build an
Independent Set instance H as follows.

* For every vertex v and every colour c in {0, 1, 2} create a vertex
  (v, c), numbered 3*v + c.  So H has 3*n vertices.
* For every vertex v add the triangle on (v, 0), (v, 1), (v, 2): an
  independent set may pick at most one colour for v.
* For every edge {u, v} of G and every colour c add the edge
  {(u, c), (v, c)}: adjacent vertices may not receive the same colour.
* Set k = n.

Correctness
-----------
(=>) A proper 3-colouring of G yields an independent set of H of size n,
namely {(v, colour(v)) : v in V}: no two chosen vertices share an original
vertex (one colour per vertex) and no two chosen vertices are joined by a
colour-conflict edge (the colouring is proper).

(<=) An independent set S of H of size >= n must contain exactly one copy
of each original vertex: the copies of a single vertex form a triangle, so
at most one per vertex, and there are n vertices, so |S| <= n.  Hence
|S| = n with exactly one (v, c_v) per v.  Assigning colour c_v to v gives a
proper colouring because a colour-conflict edge {(u, c), (v, c)} would put
both (u, c) and (v, c) in S.

Therefore G is 3-colourable iff H has an independent set of size >= n.

The construction uses 3*n vertices and 3*n + 3*|E| edges, so it runs in
polynomial time and never calls a solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges: list[list[int]] = []

    # One triangle per original vertex: at most one colour may be chosen.
    for v in range(n):
        base = 3 * v
        new_edges.append([base + 0, base + 1])
        new_edges.append([base + 0, base + 2])
        new_edges.append([base + 1, base + 2])

    # Colour-conflict edges: endpoints of an edge must differ in colour.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
