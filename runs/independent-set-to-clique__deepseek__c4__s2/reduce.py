"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement graph
G'.  So we map an Independent Set instance (G, k) to the Clique instance
(G', k) where G' has the same vertex set and an edge {u, v} exactly when
{u, v} is NOT an edge of G.  The parameter k is unchanged.

This is correct for all edge cases:
  * k <= 0: both answers are yes (independent set / clique of size 0).
  * k > n: neither graph has a k-vertex subset, so both are no.
  * The complement is computed in O(n^2) time, so the reduction is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    instance: {"n": n, "edges": [[u, v], ...], "k": k}
    returns:  {"n": n, "edges": [[u, v], ...], "k": k}

    The returned graph is the complement of the input graph.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the set of existing (undirected) edges as canonical tuples.
    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Complement edges: all pairs not present in the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
