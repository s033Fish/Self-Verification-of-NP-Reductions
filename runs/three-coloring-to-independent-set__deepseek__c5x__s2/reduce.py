"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with V = {0, ..., n-1}, build an
Independent Set instance H as follows:

* For every vertex v and every colour c in {0, 1, 2}, create a vertex
  (v, c) of H.  Index it as 3*v + c, so H has 3n vertices.
* For every v, add the triangle {(v,0), (v,1), (v,2)}.  This forbids
  picking two colours for the same original vertex.
* For every edge {u, v} of G and every colour c, add the edge
  {(u,c), (v,c)}.  This forbids the two endpoints of an edge from
  receiving the same colour.
* Set k = n.

Correctness
-----------
(=>) A proper 3-colouring of G gives, for each v, the single vertex
(v, colour(v)).  These n vertices are pairwise non-adjacent: two chosen
vertices from the same triangle are impossible (one per vertex), and two
chosen vertices from different original vertices joined by an edge have
different colours, hence are not connected by the same-colour edge.  So
H has an independent set of size n >= k.

(<=) An independent set of size >= n exists.  Each of the n disjoint
triangles contributes at most one vertex, so the set has size exactly n
and contains exactly one vertex (v, colour(v)) per original vertex.  For
every edge {u, v} of G, the same-colour edges force colour(u) != colour(v).
Thus colour is a proper 3-colouring of G.

Edge cases: n = 0 gives H with 0 vertices and k = 0, which is yes (k <= 0
is always yes), matching that the empty graph is 3-colourable.  k is
always n >= 0, so no invalid k arises.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()

    def add_edge(a: int, b: int) -> None:
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in seen:
            return
        seen.add(key)
        new_edges.append([a, b])

    # Triangle for each original vertex: at most one colour per vertex.
    for v in range(n):
        base = 3 * v
        add_edge(base + 0, base + 1)
        add_edge(base + 0, base + 2)
        add_edge(base + 1, base + 2)

    # Same-colour edges across each original edge.
    for u, v in edges:
        for c in range(3):
            add_edge(3 * u + c, 3 * v + c)

    return {"n": 3 * n, "edges": new_edges, "k": n}
