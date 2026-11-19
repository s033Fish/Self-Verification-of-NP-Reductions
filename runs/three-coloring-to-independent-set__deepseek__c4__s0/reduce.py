"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with V = {0, ..., n-1}:

* For every vertex v and every colour c in {0, 1, 2} create a new vertex
  (3*v + c) in the Independent Set graph.  Think of it as "v is coloured c".
* For every v, add the triangle (3v, 3v+1), (3v+1, 3v+2), (3v, 3v+2).
  An independent set can therefore contain at most one copy of each v,
  and to reach size n it must contain exactly one copy of every v.
* For every edge {u, v} of G and every colour c, add the edge
  (3u + c, 3v + c).  This forbids picking the same colour for both
  endpoints of an edge.
* Set k = n.

Correctness
-----------
If G is 3-colourable, pick for each v its colour c(v); the n chosen
copies form an independent set: no triangle conflict (one per v) and no
same-colour conflict (proper colouring).  Hence the target is yes.

Conversely, an independent set of size n must contain exactly one copy
of each v (triangles cap each group at one, and there are n groups).
Assigning v the colour of its chosen copy yields a proper 3-colouring
because same-colour edges across every original edge were added.  Hence
G is 3-colourable.

The construction uses O(n + m) vertices/edges and runs in polynomial
time; no solvers are called.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges: list[list[int]] = []

    # Triangle per original vertex: at most one colour copy per vertex.
    for v in range(n):
        base = 3 * v
        new_edges.append([base, base + 1])
        new_edges.append([base + 1, base + 2])
        new_edges.append([base, base + 2])

    # Same-colour conflicts for every original edge.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
