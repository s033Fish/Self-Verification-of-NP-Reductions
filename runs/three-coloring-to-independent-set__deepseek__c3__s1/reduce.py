"""Polynomial-time reduction from 3-Coloring to Independent Set.

Standard gadget reduction:

For every vertex v of the source graph (0..n-1) and every colour
c in {0,1,2}, create a target vertex (v, c), i.e. target vertex
index 3*v + c.  The target graph has 3*n vertices.

Edges:
  * For each source vertex v, add the triangle on (v,0),(v,1),(v,2).
    An independent set can therefore contain at most one colour-copy
    of v.
  * For each source edge [u, v] and each colour c, add the edge
    between (u,c) and (v,c).  This forbids giving u and v the same
    colour.

Set k = n (the number of source vertices).

Claim: the source graph is 3-colourable iff the target graph has an
independent set of size at least n.

(=>) A proper 3-colouring assigns each v exactly one colour c(v).
The set {(v, c(v)) : v in 0..n-1} has n vertices, contains no
triangle edge (one copy per vertex) and no same-colour edge (proper
colouring), hence is independent.

(<=) An independent set S of size >= n: since the triangles limit S
to at most one copy per source vertex, |S| >= n forces exactly one
copy (v, c(v)) for every v.  No same-colour edge in S means c is a
proper 3-colouring.

The reduction runs in O(n + m) time and produces O(n) vertices and
O(n + m) edges, so it is polynomial.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    target_edges: list[list[int]] = []

    # Triangle gadget for each source vertex: at most one colour copy.
    for v in range(n):
        base = 3 * v
        target_edges.append([base + 0, base + 1])
        target_edges.append([base + 1, base + 2])
        target_edges.append([base + 0, base + 2])

    # For every source edge, forbid equal colours at the two endpoints.
    for u, v in edges:
        for c in range(3):
            target_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": target_edges, "k": n}
