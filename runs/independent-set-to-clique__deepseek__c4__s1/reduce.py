"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph G'.
So the reduction keeps n and k, and replaces the edge set with its
complement (all pairs u != v that are not edges of G).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": k}
