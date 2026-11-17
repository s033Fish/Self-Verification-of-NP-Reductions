"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G iff S is an independent set in the
complement graph G_bar (same vertex set; an edge in G_bar exactly when the
pair is a non-edge of G).  Therefore G has a clique of size >= k iff G_bar
has an independent set of size >= k, so the reduction keeps n and k and
replaces the edge list by the list of non-edges of G.

Building the complement takes O(n^2) time, which is polynomial in the input
size (the input itself lists at most O(n^2) edges).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a Clique instance to an Independent Set instance.

    Input / output format: {"n": n, "edges": [[u, v], ...], "k": k}.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = {frozenset((u, v)) for u, v in edges}

    complement_edges: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
