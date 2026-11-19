"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard "gadget" reduction):

Given a 3-Coloring instance G = (V, E) with |V| = n, build an
Independent Set instance H = (V', E', k) as follows.

* For every vertex v in V and every colour c in {0, 1, 2}, create a
  vertex (v, c) in V'.  So |V'| = 3n.
* For every original vertex v, add the triangle
  {(v,0), (v,1), (v,2)} to E'.  An independent set can therefore contain
  at most one colour-copy of each original vertex.
* For every original edge {u, v} in E and every colour c, add the edge
  {(u,c), (v,c)} to E'.  This forbids the two endpoints of an original
  edge from receiving the same colour.
* Set k = n.

Correctness:
  (=>) A proper 3-colouring of G yields the set of vertices
       {(v, colour(v)) : v in V}, which has n vertices, contains at most
       one copy per original vertex, and never contains both (u,c) and
       (v,c) for an edge {u,v}; hence it is independent.
  (<=) An independent set of size n must, by the triangle gadgets,
       contain at most one copy of each original vertex, so size n forces
       exactly one copy (v, c_v) per vertex v.  The edge gadgets then
       guarantee c_u != c_v for every edge {u,v}, i.e. a proper
       3-colouring.

The construction uses O(n + |E|) vertices/edges, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Vertex (v, c) is encoded as integer 3*v + c.
    def vid(v: int, c: int) -> int:
        return 3 * v + c

    new_edges: list[list[int]] = []

    # Triangle gadget for every original vertex: at most one colour chosen.
    for v in range(n):
        new_edges.append([vid(v, 0), vid(v, 1)])
        new_edges.append([vid(v, 1), vid(v, 2)])
        new_edges.append([vid(v, 0), vid(v, 2)])

    # Edge gadget for every original edge: same colour forbidden.
    for u, v in edges:
        for c in range(3):
            new_edges.append([vid(u, c), vid(v, c)])

    return {"n": 3 * n, "edges": new_edges, "k": n}
