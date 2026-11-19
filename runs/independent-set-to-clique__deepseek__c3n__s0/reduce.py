"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph
(and vice versa).  So we keep n and k and map the edge set to its
complement: the target graph has an edge {u, v} iff the source graph
does not.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance."""
    n = instance["n"]
    edges = instance["edges"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": instance["k"]}
