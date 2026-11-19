"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement graph
of G.  So we map (G, k) to (complement(G), k), keeping n and k unchanged.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Instance format (both problems): {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the complement graph on the same vertex set 0..n-1.
    existing = set()
    for u, v in edges:
        existing.add((u, v))
        existing.add((v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
