"""Polynomial-time reduction from Clique to Vertex Cover.

Reduction
---------
Given a Clique instance (G, k) on n vertices, build the complement graph
G' on the same vertex set: {u, v} is an edge of G' iff it is NOT an edge
of G (u != v).

Key fact: S is a clique of G  <=>  S is an independent set of G'.
And a set C is a vertex cover of G'  <=>  V minus C is an independent set
of G'.  Therefore G has a clique of size >= k iff G' has an independent
set of size >= k iff G' has a vertex cover of size <= n - k.

So the target instance is (G', n - k).  Building the complement takes
O(n^2) time, which is polynomial in the input size.

Edge cases are handled automatically by the arithmetic:
  * k <= 0  ->  n - k >= n, and Vertex Cover is always yes when k >= n.
  * k >  n  ->  n - k < 0, and Vertex Cover is always no when k < 0.
  * n = 0, k <= 0 -> complement has no edges and n - k >= 0, yes.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Existing undirected edges, stored as frozensets for O(1) lookup.
    present = {frozenset((u, v)) for u, v in edges}

    # Complement graph: every non-edge of G becomes an edge of G'.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
