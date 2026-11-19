"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is a clique in the complement
graph complement(G).  Hence G has a vertex cover of size at most k iff
complement(G) has a clique of size at least n - k.

So reduce maps (G, k) to (complement(G), n - k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    existing = set()
    for u, v in edges:
        existing.add((u, v) if u < v else (v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
