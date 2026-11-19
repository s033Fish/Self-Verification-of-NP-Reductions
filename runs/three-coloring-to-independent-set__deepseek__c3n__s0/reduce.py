"""Polynomial-time reduction from 3-Coloring to Independent Set.

Reduction (standard):
  Given a 3-Coloring instance G = (V, E) with n = |V|, build an
  Independent Set instance H as follows.

  * For every vertex v in 0..n-1 and every colour c in {0, 1, 2}, create a
    node (v, c).  Number these nodes so that node id = 3*v + c, hence H has
    N = 3*n vertices.
  * For every vertex v, add the three edges among (v,0),(v,1),(v,2): a
    triangle.  Any independent set therefore contains at most one colour
    copy of each vertex.
  * For every edge {u,v} in E and every colour c, add the edge
    {(u,c),(v,c)}.  An independent set therefore cannot pick the same
    colour for both endpoints of an edge.
  * Set k = n.

  Claim: G is 3-colourable  <=>  H has an independent set of size >= n.

  (=>) A proper 3-colouring of G picks, for each vertex v, exactly one
  colour c(v); the set {(v, c(v)) : v in V} has n nodes, contains no
  triangle edge (one per vertex) and no same-colour edge (proper colouring),
  so it is independent.

  (<=) An independent set S of size >= n contains at most one copy of each
  of the n vertices, so |S| = n and it contains exactly one copy (v, c(v))
  of every vertex.  The same-colour edges guarantee that adjacent vertices
  receive different colours, so c is a proper 3-colouring.

  The construction uses O(n) vertices and O(n + |E|) edges and runs in
  polynomial time; no solver is called.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    def node(v: int, c: int) -> int:
        return 3 * v + c

    new_edges: list[list[int]] = []

    # Triangle for each original vertex: at most one colour may be chosen.
    for v in range(n):
        new_edges.append([node(v, 0), node(v, 1)])
        new_edges.append([node(v, 0), node(v, 2)])
        new_edges.append([node(v, 1), node(v, 2)])

    # Same-colour edges for each original edge: endpoints must differ.
    for u, w in edges:
        for c in range(3):
            new_edges.append([node(u, c), node(w, c)])

    return {"n": 3 * n, "edges": new_edges, "k": n}
