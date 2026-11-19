"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction (for n >= 3):
  Pick vertex 0 of G and "split" it into two vertices s and t, both adjacent
  to every neighbour of 0.  Add a pendant leaf p attached to s and a pendant
  leaf q attached to t.

  In the resulting graph, p and q have degree 1, so every Hamiltonian path
  must start at p and end at q and therefore has the form

        p - s - ... - t - q.

  The middle part is a Hamiltonian path of the split graph from s to t, which
  exists iff G has a Hamiltonian cycle through vertex 0 (i.e. iff G has a
  Hamiltonian cycle at all): a cycle 0-a-...-b-0 becomes s-a-...-b-t, and
  conversely a path s-a-...-b-t with a,b in N(0) closes to 0-a-...-b-0.

  For n <= 2 the source is always a no-instance, so we return a fixed
  no-instance of Hamiltonian Path.

The reduction is clearly polynomial (linear in the number of edges).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always false for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Vertex mapping:
    #   s (split of 0)      -> 0
    #   t (split of 0)      -> 1
    #   original u (u >= 1) -> u + 1
    #   pendant p           -> n + 1
    #   pendant q           -> n + 2
    s, t = 0, 1
    p, q = n + 1, n + 2

    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    new_edges: list[list[int]] = []

    # Edges of G that do not touch vertex 0 are kept (shifted).
    for a, b in edges:
        if a != 0 and b != 0:
            new_edges.append([a + 1, b + 1])

    # Both s and t are adjacent to every neighbour of 0.
    for x in adj[0]:
        new_edges.append([s, x + 1])
        new_edges.append([t, x + 1])

    # Pendant leaves force the two endpoints of the Hamiltonian path.
    new_edges.append([p, s])
    new_edges.append([q, t])

    return {"n": n + 3, "edges": new_edges}
