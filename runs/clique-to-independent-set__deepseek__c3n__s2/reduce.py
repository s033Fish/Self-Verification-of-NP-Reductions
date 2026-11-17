"""Polynomial-time reduction from Clique to Independent Set.

A set of vertices is a clique in G exactly when it is an independent set in
the complement graph G'.  So the reduction keeps n and k and replaces the
edge set by the complement edge set (all pairs {u, v}, u != v, that are not
edges of G).  This is O(n^2) time and space.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a Clique instance to an Independent Set instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}

    Returns the complement graph on the same vertices with the same k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v))
        present.add((v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": k}
