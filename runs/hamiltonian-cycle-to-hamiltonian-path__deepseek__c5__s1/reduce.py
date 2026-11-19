"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction (for n >= 3):
    Pick the vertex v = 0 of the source graph G.  Build the target graph H
    with n + 3 vertices:

      * every vertex of G except v, relabelled to 0 .. n-2,
      * v1, v2  -- two "split copies" of v, each joined to every neighbour
                   of v in G,
      * p1, p2  -- pendant leaves attached to v1 and v2 respectively.

    H has a Hamiltonian path iff G has a Hamiltonian cycle.

    (=>) A cycle v, x1, ..., x_{n-1}, v in G yields the path
             p1 - v1 - x1 - ... - x_{n-1} - v2 - p2
         in H (v1 and v2 are adjacent to x1 and x_{n-1}, which are
         neighbours of v).

    (<=) p1 and p2 are leaves (degree 1), hence they must be the two
         endpoints of any Hamiltonian path of H.  The rest of the path is
             v1 - y1 - y2 - ... - y_{n-1} - v2
         where y1, ..., y_{n-1} is an ordering of G - v.  Since v1 and v2
         are only adjacent to N(v), we get y1, y_{n-1} in N(v), so
             v - y1 - y2 - ... - y_{n-1} - v
         is a Hamiltonian cycle of G.  (n >= 3 guarantees y1 != y_{n-1},
         so the cycle has length at least 3.)

    For n <= 2 the source is always "no"; we return the empty graph
    {"n": 0, "edges": []}, which is also a "no" instance of the target.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Graphs with n <= 2 never have a Hamiltonian cycle.  The empty graph
    # has no Hamiltonian path either, so it is a correct "no" instance.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0
    v1 = n - 1
    v2 = n
    p1 = n + 1
    p2 = n + 2

    def relabel(u: int) -> int:
        # Map original vertices 1..n-1 to 0..n-2 (vertex v = 0 is removed).
        return u - 1

    neighbors: set[int] = set()
    new_edges: list[list[int]] = []

    for edge in edges:
        a, b = edge
        if a == v:
            neighbors.add(b)
        elif b == v:
            neighbors.add(a)
        else:
            new_edges.append([relabel(a), relabel(b)])

    for u in neighbors:
        new_edges.append([v1, relabel(u)])
        new_edges.append([v2, relabel(u)])

    new_edges.append([p1, v1])
    new_edges.append([p2, v2])

    return {"n": n + 3, "edges": new_edges}
