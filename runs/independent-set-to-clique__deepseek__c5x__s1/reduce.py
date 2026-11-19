"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph G'.
So map (G, k) -> (complement(G), k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": k}
