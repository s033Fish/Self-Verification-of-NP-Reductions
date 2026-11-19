"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph G'.
So we keep n and k unchanged and replace the edge set with its complement.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map an Independent Set instance to a Clique instance.

    Instance format (both problems): {"n": n, "edges": [[u, v], ...], "k": k}
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
