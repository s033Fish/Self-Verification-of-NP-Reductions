"""Polynomial-time reduction from Clique to Independent Set.

A clique in G is exactly an independent set in the complement graph
(and vice versa).  So we map (G, k) to (complement(G), k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v))
        present.add((v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
