"""Polynomial-time reduction from Vertex Cover to Clique.

Idea: a set S is a vertex cover of G iff V \\ S is a clique in the complement
graph complement(G).  Therefore G has a vertex cover of size AT MOST k iff
complement(G) has a clique of size AT LEAST n - k.

So the reduction keeps n, replaces the edge set by its complement, and maps
k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add(frozenset((u, v)))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
