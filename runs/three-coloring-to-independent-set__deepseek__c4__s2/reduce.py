"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with V = {0, ..., n-1}, build an
Independent Set instance H = (V', E') as follows.

* For every original vertex v and every colour c in {0, 1, 2}, create a
  new vertex (v, c).  Identify it with the integer 3*v + c, so H has
  n' = 3*n vertices.

* For every original vertex v, add the three edges among (v, 0), (v, 1)
  and (v, 2).  These form a triangle, so an independent set of H can use
  at most one colour-vertex per original vertex.

* For every original edge {u, v} and every colour c, add the edge
  {(u, c), (v, c)}.  This forbids giving both endpoints of an original
  edge the same colour.

* Set k = n.

Correctness
-----------
(=>) A proper 3-colouring of G picks, for each vertex v, one colour
col(v).  The set {(v, col(v)) : v in V} has exactly n vertices.  It is
independent: no two chosen vertices share an original vertex (one per
vertex), and for an original edge {u, v} the chosen colours differ, so
the corresponding colour-vertices are not joined.

(<=) Any independent set S of H has at most one vertex per original
vertex (triangles), hence |S| <= n.  If |S| = n it contains exactly one
(v, col(v)) per v.  For every original edge {u, v}, S contains no edge
of H, in particular not {(u, col(u)), (v, col(v))}, so col(u) != col(v).
Thus col is a proper 3-colouring of G.

Therefore H has an independent set of size at least n iff G is
3-colourable.  The construction uses O(n + |E|) vertices/edges and runs
in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges: list[list[int]] = []

    # Triangle for each original vertex: at most one colour per vertex.
    for v in range(n):
        base = 3 * v
        new_edges.append([base, base + 1])
        new_edges.append([base, base + 2])
        new_edges.append([base + 1, base + 2])

    # Same-colour conflicts across each original edge.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
