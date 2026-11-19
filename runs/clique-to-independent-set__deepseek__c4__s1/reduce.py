"""Polynomial-time reduction from Clique to Independent Set.

A set of vertices is a clique in G exactly when it is an independent set in
the complement graph of G.  So we map (G, k) to (complement(G), k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}

    The complement graph has the same vertex set 0..n-1 and contains exactly
    the edges that are absent from the input graph.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present: set[frozenset[int]] = {frozenset((u, v)) for u, v in edges}

    complement_edges: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
