"""Polynomial-time reduction from Clique to Vertex Cover.

Idea
----
A clique in a graph G is exactly an independent set in the complement graph
G'.  The complement of an independent set is a vertex cover, so:

    G has a clique of size >= k
        <=> G' has an independent set of size >= k
        <=> G' has a vertex cover of size <= n - k

Hence the reduction keeps n, replaces the edge set by its complement, and
maps k to n - k.  This is correct for every integer k, including the edge
cases k <= 0, k = 1, k > n, and n = 0 (see tests).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Normalise the input edges to unordered pairs (u < v).
    present: set[tuple[int, int]] = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    # Build the complement graph on the same vertex set.
    complement_edges: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
