"""Polynomial-time reduction from Clique to Independent Set.

Reduction: given a Clique instance G = (V, E) with parameter k, build the
complement graph G' = (V, E') where E' = { {u,v} : u != v and {u,v} not in E }.
Return the Independent Set instance (G', k).

Correctness: a set S of vertices is a clique in G iff every pair in S is an
edge of G, iff no pair in S is an edge of G', iff S is an independent set in
G'.  Hence G has a clique of size >= k iff G' has an independent set of
size >= k.

The construction takes O(n^2) time and space, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Normalize the edge set of the source graph.
    edge_set: set[frozenset[int]] = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    # Build the complement graph.
    complement_edges: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
