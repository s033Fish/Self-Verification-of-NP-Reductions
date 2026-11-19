"""Polynomial-time reduction from Clique to Independent Set.

A clique in a graph G is exactly an independent set in the complement graph
of G (and vice versa).  Therefore an instance of Clique with n vertices,
edge set E and threshold k maps to an instance of Independent Set on the same
n vertices, with edge set the complement of E, and the same threshold k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k``; its edges are exactly
    the non-edges of the input graph (the complement graph).
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
