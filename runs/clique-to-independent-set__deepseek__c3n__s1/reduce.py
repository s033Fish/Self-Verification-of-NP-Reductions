"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G iff S is an independent set in the
complement graph G-bar.  Therefore Clique(G, k) is a yes-instance exactly
when IndependentSet(complement(G), k) is a yes-instance.

The reduction keeps n and k unchanged and replaces the edge list with its
complement over the n vertices.  It runs in O(n^2) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a Clique instance to an Independent Set instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}

    Returns the complement graph on the same vertex set with the same k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    existing = set()
    for u, v in edges:
        existing.add((u, v))
        existing.add((v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": k}
